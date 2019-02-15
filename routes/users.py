# Stdlib
from datetime import datetime
from enum import Enum

# External Libraries
import aiohttp
from marshmallow_enum import EnumField
from quart import abort, jsonify, request
from webargs import fields, validate

# Sayonika Internals
from framework.authentication import Authenticator
from framework.mailer import MailTemplates
from framework.models import Mod, User, Review, ModAuthors, UserFavorites
from framework.objects import mailer, jwt_service, SETTINGS
from framework.quart_webargs import use_kwargs
from framework.route import route, multiroute
from framework.route_wrappers import json, requires_login
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import paginate


class UserSorting(Enum):
    name = 1
    joined_at = 2


sorters = {
    UserSorting.name: User.username,
    UserSorting.joined_at: User.joined_at
}


class Users(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    @use_kwargs({
        "q": fields.Str(),
        "page": fields.Int(missing=0),
        "limit": fields.Int(missing=50),
        "sort": EnumField(UserSorting),
        "ascending": fields.Bool(missing=False)
    }, locations=("query",))
    async def get_users(self, q: str = None, page: int = None, limit: int = None, sort: UserSorting = None,
                        ascending: bool = False):
        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0
        query = User.query

        if q is not None:
            query = query.where(User.username.match(q))

        if sort is not None:
            sort_by = sorters[sort]
            query = query.order_by(sort_by.asc() if ascending else sort_by.desc())

        results = await paginate(query, page, limit).gino.all()
        total = await query.alias().count().gino.scalar()

        return jsonify(total=total, page=page, limit=limit, results=self.dict_all(results))

    @multiroute("/api/v1/users", methods=["POST"], other_methods=["GET"])
    @json
    @use_kwargs({
        "username": fields.Str(required=True, validate=validate.Length(max=25)),
        "password": fields.Str(required=True),
        "email": fields.Email(required=True),
        "recaptcha": fields.Str(required=True)
    }, locations=("json",))
    async def post_users(self, username: str, password: str, email: str, recaptcha: str):
        async with aiohttp.ClientSession(raise_for_status=True) as sess:
            params = {
                "secret": SETTINGS["RECAPTCHA_CHECKBOX_SECRET_KEY"],
                "response": recaptcha
            }

            async with sess.post("https://www.google.com/recaptcha/api/siteverify", params=params) as resp:
                data = await resp.json()

                if data["success"] is False:
                    abort(400, "Invalid captcha")

        users = await User.get_any(True, username=username, email=email).first()

        if users is not None:
            abort(400, "Username and/or email already in use")

        user = User(username=username, email=email)

        user.password = Authenticator.hash_password(password)
        user.last_pass_reset = datetime.now()

        await user.create()

        token = jwt_service.make_email_token(user.id, user.email)

        await mailer.send_mail(MailTemplates.VerifyEmail, email, {
            "USER_NAME": user.username,
            "TOKEN": token,
            "BASE_URL": SETTINGS["EMAIL_BASE"]
        })

        return jsonify(user.to_dict())

    @route("/api/v1/users/<user_id>", methods=["GET"])
    @json
    async def get_user(self, user_id: str):
        is_through_atme = False

        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                abort(401, "Login required")

            parsed = await jwt_service.verify_login_token(token, True)

            if parsed is False:
                abort(401, "Invalid token")

            user_id = parsed["id"]
            is_through_atme = True

        user = await User.get(user_id)

        if user is None:
            abort(404, "Unknown user")

        return jsonify(user.to_dict() if not is_through_atme else user.to_self_dict())

    @route("/api/v1/users/@me", methods=["PATCH"])
    @requires_login
    @json
    @use_kwargs({
        "username": fields.Str(validate=validate.Length(max=25)),
        "password": fields.Str(),
        "email": fields.Email(),
        "bio": fields.Str(validate=validate.Length(max=100)),
        "avatar": None
    }, locations=("json",))
    async def patch_user(self, **kwargs):
        token = request.headers.get("Authorization", request.cookies.get('token'))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        user = await User.get(user_id)
        updates = user.update()

        password = kwargs.pop('password') if 'password' in kwargs else None

        for attr, item in kwargs.items():
            updates = updates.update(**{attr: item})

        if password is not None:
            password = Authenticator.hash_password(password)
            updates = updates.update(password=password, last_pass_reset=datetime.now())

        await updates.apply()

        return jsonify(user.to_dict())

    @route("/api/v1/users/<user_id>/favorites")
    @json
    async def get_favorites(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_login_token(token, True))["id"]

        if not await User.exists(user_id):
            abort(404, "Unknown user")

        favorite_pairs = await UserFavorites.query.where(UserFavorites.user_id == user_id).gino.all()
        favorite_pairs = [x.mod_id for x in favorite_pairs]
        favorites = await Mod.query.where(Mod.id.in_(favorite_pairs)).gino.all()

        return jsonify(self.dict_all(favorites))

    @route("/api/v1/users/<user_id>/mods")
    @json
    async def get_user_mods(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_login_token(token, True))["id"]

        if not await User.exists(user_id):
            abort(404, "Unknown user")

        mod_pairs = await ModAuthors.query.where(ModAuthors.user_id == user_id).gino.all()
        mod_pairs = [x.mod_id for x in mod_pairs]
        mods = await Mod.query.where(Mod.id.in_(mod_pairs)).gino.all()

        return jsonify(self.dict_all(mods))

    @route("/api/v1/users/<user_id>/reviews")
    @json
    async def get_user_reviews(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_login_token(token, True))["id"]

        if not await User.exists(user_id):
            abort(404, "Unknown user")

        reviews = await Review.query.where(Review.author_id == user_id).gino.all()

        return jsonify(self.dict_all(reviews))


def setup(core: Sayonika):
    Users(core).register()
