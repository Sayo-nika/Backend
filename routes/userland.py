# External Libraries
from quart import abort, jsonify, request
from sqlalchemy import and_

# Sayonika Internals
from framework.authentication import Authenticator
from framework.models import Mod, User, Review, UserMods, UserFavorites
from framework.objects import jwt_service
from framework.route import route, multiroute
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    # === Mods ===

    @route("/api/v1/login", methods=["POST"])
    @json
    async def login(self):
        body = await request.json
        username = body.get("username")
        password = body.get("password")

        if username is None or password is None:
            abort(400, "Needs `username` and `password`")

        user = await User.get_any(True, username=username, email=username).first()

        if not user:
            abort(400, "Invalid username or email")

        if Authenticator.hash_password(password) != user.password:
            abort(400, "Invalid password")

        if not user.email_verified:
            abort(401, "Email needs to be verified")

        token = jwt_service.make_token(user.id, user.last_pass_reset)

        return jsonify(token=token)

    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    async def get_mods(self):
        page = request.args.get("page", "")
        limit = request.args.get("limit", "")
        page = int(page) if page.isdigit() else 0
        limit = int(limit) if limit.isdigit() else 50

        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        results = await Mod.paginate(page, limit).where(Mod.verified).gino.all()
        return jsonify(self.dict_all(results))

    @route("/api/v1/mods/recent_releases")
    @json
    async def get_recent_releases(self):
        mods = await Mod.query.where(Mod.verified).order_by(Mod.released_at.desc()).limit(10).gino.all()
        return jsonify(self.dict_all(mods))

    @route("/api/v1/mods/popular")
    @json
    async def get_popular(self):
        mods = await Mod.query.where(and_(
            Mod.verified,
            Mod.released_at is not None
        )).order_by(Mod.downloads.desc()).limit(10).gino.all()

        return jsonify(self.dict_all(mods))

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    async def get_mod(self, mod_id: str):  # pylint: disable=no-self-use
        mod = await Mod.get(mod_id)

        if mod is None:
            abort(404, "Unknown mod")

        return jsonify(mod.to_dict())

    @route("/api/v1/mods/<mod_id>/download")
    @json
    async def get_download(self, mod_id: str):  # pylint: disable=no-self-use
        mod = await Mod.get(mod_id)

        if mod is None:
            abort(404, "Unknown mod")
        elif not mod.zip_url:
            abort(404, "Mod has no download")

        # We're using a URL on Upload class. await URL only and let client handle DLs
        return jsonify(url=mod.zip_url)

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    async def get_mod_reviews(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        reviews = await Review.query.where(Review.mod_id == mod_id).gino.all()

        return jsonify(self.dict_all(reviews))

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    async def get_mod_authors(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        authors = await User.query.outerjoin(UserMods, UserMods.mod_id == mod_id).gino.all()

        return jsonify(self.dict_all(authors))

    # === Users ===

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

    @multiroute("/api/v1/users/<user_id>", methods=["GET"], other_methods=["POST"])
    @json
    async def get_user(self, user_id: str):  # pylint: disable=no-self-use
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        user = await User.get(user_id)

        if user is None:
            abort(404, "Unknown user")

        return jsonify(user.to_dict())

    @route("/api/v1/users/<user_id>/favorites")
    @json
    async def get_favorites(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        if not await User.exists(user_id):
            abort(404, "Unknown user")

        favorites = await Mod.query.outerjoin(UserFavorites, UserFavorites.user_id == user_id).gino.all()

        return jsonify(self.dict_all(favorites))

    @route("/api/v1/users/<user_id>/mods")
    @json
    async def get_user_mods(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        if not await User.exists(user_id):
            abort(404, "Unknown user")

        mods = await Mod.query.outerjoin(UserMods, UserMods.user_id == user_id).gino.all()

        return jsonify(self.dict_all(mods))

    @route("/api/v1/users/<user_id>/reviews")
    @json
    async def get_user_reviews(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                abort(401, "Login required")

            user_id = (await jwt_service.verify_token(token, True))["id"]

        if not await User.exists(user_id):
            abort(404, "Unknown user")

        reviews = await Review.query.where(Review.author_id == user_id).gino.all()

        return jsonify(self.dict_all(reviews))


def setup(core: Sayonika):
    Userland(core).register()
