# Stdlib
from datetime import datetime

# External Libraries
from quart import jsonify, request
from flask_mail import Message

# Sayonika Internals
from framework.authentication import Authenticator
from framework.models import Mod, User, Review, UserMods, UserFavorites
from framework.objects import jwt_service
from framework.route import route, multiroute
from framework.route_wrappers import json, requires_login
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import abort

mail = Mail()
smtp = mail.init_app(Sayonika)

user_attrs = {
    "username": str,
    "password": str,
    "email": str
}

user_patch_attrs = {
    **user_attrs,
    "bio": str,
    "avatar": str
}

# Required for mail template.
def getFileContent(path):
    with open(path, 'r') as file:

        data = file.read()
        return data

class Users(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    async def get_users(self):
        page = request.args.get("page", "")
        limit = request.args.get("limit", "")
        page = int(page) if page.isdigit() else 0
        limit = int(limit) if limit.isdigit() else 50

        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        results = await User.paginate(page, limit).gino.all()
        return jsonify(self.dict_all(results))

    @multiroute("/api/v1/users/<user_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    async def get_user(self, user_id: str):  # pylint: disable=no-self-use
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                return abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        user = await User.get(user_id)

        if user is None:
            return abort(404, "Unknown user")

        return jsonify(user.to_dict())

    @route("/api/v1/users/<user_id>/favorites")
    @json
    async def get_favorites(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                return abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        if not await User.exists(user_id):
            return abort(404, "Unknown user")

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
                return abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        if not await User.exists(user_id):
            return abort(404, "Unknown user")

        mod_pairs = await UserMods.query.where(UserMods.user_id == user_id).gino.all()
        mod_pairs = [x.mod_id for x in mod_pairs]
        mods = await Mod.query.where(Mod.id.in_(mod_pairs)).gino.all()

        return jsonify(self.dict_all(mods))

    @route("/api/v1/users/<user_id>/reviews")
    @json
    async def get_user_reviews(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get("token"))

            if token is None:
                return abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        if not await User.exists(user_id):
            return abort(404, "Unknown user")

        reviews = await Review.query.where(Review.author_id == user_id).gino.all()

        return jsonify(self.dict_all(reviews))

    @multiroute("/api/v1/users", methods=["POST"], other_methods=["GET"])
    @json
    async def post_users(self):
        body = await request.json
        user = User()

        for attr, type_ in user_attrs.items():
            val = body.get(attr)

            if val is None:
                return abort(400, f"Missing value '{attr}'")
            elif isinstance(val) is not type_:
                return abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")

            setattr(user, attr, val)

        users = await User.get_any(True, username=user.username, email=user.email).first()

        if users is not None:
            return abort(400, "Username and/or email already in use")

        user.avatar = body.get("avatar")
        user.bio = body.get("bio")
        user.password = Authenticator.hash_password(user.password)
        user.last_pass_reset = datetime.now()

        # TODO: replace placeholders in template.
        template = getFileContent('./framework/mail_templates/verify_email.html')

        msg = Message(sender="noreply@sayonika.moe", recipients=body.email)
        msg.html = template

        smtp.send(msg)
        await user.create()

        print(user.to_dict())

        return jsonify(user.to_dict())

    @multiroute("/api/v1/users/<user_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_login
    @json
    async def patch_user(self, user_id: str):
        if not await User.exists(user_id):
            return abort(404, "Unknown user")

        body = await request.json
        user = await User.get(user_id)
        updates = user.update()

        for attr, type_ in user_patch_attrs.items():
            val = body.get(attr)

            if val is None:
                continue
            elif isinstance(val) is not type_:
                return abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")
            elif attr != "password":
                updates = updates.update(**{attr: val})

        if body.get("password"):
            password = Authenticator.hash_password(body["password"])
            updates = updates.update(password=password, last_pass_reset=datetime.now())

        await updates.apply()

        return jsonify(user.to_dict())


def setup(core: Sayonika):
    Users(core).register()
