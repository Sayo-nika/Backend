# Stdlib
from datetime import datetime
from enum import Enum

# External Libraries
from marshmallow_enum import EnumField
from quart import abort, jsonify, request
from sqlalchemy import or_, not_
from webargs import fields, validate

# Sayonika Internals
from framework.authentication import Authenticator
from framework.mailer import MailTemplates
from framework.models import Mod, User, Review, ModAuthor, ReportType, UserReport, UserFavorite
from framework.objects import SETTINGS, mailer, limiter, jwt_service
from framework.quart_webargs import use_kwargs
from framework.route import route, multiroute
from framework.route_wrappers import json, requires_login
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import paginate, verify_recaptcha


class UserSorting(Enum):
    name = 1
    joined_at = 2


sorters = {
    UserSorting.name: User.username,
    UserSorting.joined_at: User.created_at
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
        "ascending": fields.Bool(missing=False),
        "ignore": fields.Str()  # Comma separated list of IDs to filter out
    }, locations=("query",))
    async def get_users(self, q: str = None, page: int = None, limit: int = None, sort: UserSorting = None,
                        ascending: bool = False, ignore: str = None):
        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0
        query = User.query

        if q is not None:
            query = query.where(or_(
                User.username.match(q),
                User.username.ilike(f"%{q}%")
            ))

        if sort is not None:
            sort_by = sorters[sort]
            query = query.order_by(sort_by.asc() if ascending else sort_by.desc())

        if ignore is not None:
            ignore = ignore.split(",")
            query = query.where(not_(User.id.in_(ignore)))

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
        """Register a user to the site."""
        score = await verify_recaptcha(recaptcha, self.core.aioh_sess)

        if score < 0.5:
            # TODO: send email/other 2FA when below 0.5
            abort(400, "Possibly a bot")

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
        }, session=self.core.aioh_sess)

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
        "old_password": fields.Str(required=True),
        "email": fields.Email(),
        "bio": fields.Str(validate=validate.Length(max=100)),
        "avatar": None
    }, locations=("json",))
    async def patch_user(self, old_password: str, password: str = None, **kwargs):
        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        user = await User.get(user_id)

        if not Authenticator.compare_password(old_password, user.password):
            abort(403, "`old_password` doesn't match")

        updates = user.update(**kwargs)

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

        favorite_pairs = await UserFavorite.query.where(UserFavorite.user_id == user_id).gino.all()
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

        mod_pairs = await ModAuthor.query.where(ModAuthor.user_id == user_id).gino.all()
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

    @route("/api/v1/users/<user_id>/report", methods=["POST"])
    @json
    @use_kwargs({
        "content": fields.Str(required=True, validate=validate.Length(min=100, max=1000)),
        "type_": EnumField(ReportType, required=True),
        "recaptcha": fields.Str(required=True)
    }, locations=("json",))
    @requires_login
    @limiter.limit("2 per hour")
    async def report_user(self, user_id: str, content: str, type_: ReportType, recaptcha: str):
        score = await verify_recaptcha(recaptcha, self.core.aioh_sess)

        if score < 0.5:
            # TODO: send email/other 2FA when below 0.5
            abort(400, "Possibly a bot")

        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        author_id = parsed_token["id"]

        report = await UserReport.create(content=content, author_id=author_id, user_id=user_id, type=type_)
        return jsonify(report.to_dict())


def setup(core: Sayonika):
    Users(core).register()
