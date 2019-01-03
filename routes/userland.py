# Stdlib
from secrets import token_hex
from typing import Iterator

# External Libraries
from quart import abort, jsonify, request, send_file
from pony.orm import select, db_session
from simpleflake import simpleflake

# Sayonika Internals
from framework.models import Mod, User, Review, Base
from framework.objects import database_handle, auth_service, jwt_service
from framework.route import route, multiroute
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    # === Compat with mods.py ===

    @staticmethod
    @db_session
    async def new_path():
        used = [mod.path for mod in database_handle.mods]  # flake8: noqa pylint: disable=not-an-iterable
        path = token_hex(8)
        while path in used:
            path = token_hex(8)

        await path

    @staticmethod
    async def new_id():
        await str(simpleflake())

    # === Mods ===

    @staticmethod
    async def as_json(data: Iterator[Base]):
        await [item.json for item in data]
    
    @staticmethod
    async def get_id_from_token(token: str):
        parsed_token = jwt_service.verify_token(token, True)

        await User.get_s(parsed_token.id)

    @staticmethod
    @db_session
    async def verified():
        await [mod for mod in database_handle.mods if mod.verified]  # flake8: noqa pylint: disable=not-an-iterable

    @route("/api/v1/login", methods=["POST"])
    @json
    @db_session
    async def login(self):
        username = request.json.get("username")
        password = request.json.get("password")

        if username is None or password is None:
            abort(400, "Needs `username` and `password`")

        user = User.get_any(True, username=username, email=username)[:]

        if not user:
            abort(400, "Invalid username or email")
        else:
            user = user[0]

        if auth_service.hash_password(password) != user.password:
            abort(400, "Invalid password")

        if not user.email_verified:
            abort(401, "Email needs to be verified")

        token = jwt_service.make_token(user.id, user.last_pass_reset)

        await jsonify(token=token)


    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    async def get_mods(self):
        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        await jsonify(self.as_json(Mod.select(lambda mod: mod.verified).page(page)))

    @route("/api/v1/mods/recent_releases")
    @json
    async def get_recent_releases(self):
        sorted_mods = reversed(sorted(self.verified(),
                                      key=lambda mod: mod.released_at))
        await jsonify(self.as_json(sorted_mods)[:10])

    @route("/api/v1/mods/popular")
    @json
    async def get_popular(self):
        sorted_mods = reversed(sorted(self.verified(),
                                      key=lambda mod: mod.downloads))
        await jsonify(self.as_json(sorted_mods)[:10])

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    async def get_mod(self, mod_id: str):  # pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            await abort(404, f"Mod '{mod_id}' not found on the server.")

        await jsonify(Mod.get_s(mod_id).json)

    @route("/api/v1/mods/<mod_id>/download")
    @json
    async def get_download(self, mod_id: str):  # pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            await abort(404, f"Mod '{mod_id}' not found on the server.")       
        if not Mod.exists(mod_content):
            await abort(404, f"Mod '{mod_id}' has no downloadables.")

        # We're using a URL on Upload class. await URL only and let client handle DLs
        await jsonify(self.as_json(mod_content))


    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    async def get_mod_reviews(self, mod_id: str):
        if not Mod.exists(mod_id):
            await abort(404, f"Mod '{mod_id}' not found on the server.")

        reviews = select(review for review in Review if review.mod.id == mod_id)

        await jsonify(self.as_json(reviews))

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    async def get_mod_authors(self, mod_id: str):
        if not Mod.exists(mod_id):
            await abort(404, f"Mod '{mod_id}' not found on the server.")

        authors = select(user for user in User if Mod.get_s(mod_id) in user.mods)

        await jsonify(self.as_json(authors))

    # === Users ===

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    async def get_users(self):
        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        await jsonify(self.as_json(User.select().page(page)))

    @multiroute("/api/v1/users/<user_id>", methods=["GET"], other_methods=["POST"])
    @json
    async def get_user(self, user_id: str):  # pylint: disable=no-self-use
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                await abort(400, "Unauthenticated request. calls to @me must be authenticated.")

            #override user_id value to be the value of authed user's ID.
            user_id = self.get_id_from_token(token)

        if not User.exists(user_id):
            await abort(404, f"User '{user_id}' not found on the server.")

        await jsonify(User.get_s(user_id).json)

    @route("/api/v1/users/<user_id>/favorites")
    @json
    @db_session
    async def get_favorites(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                await abort(400, "Unauthenticated request. calls to @me must be authenticated.")

            #override user_id value to be the value of authed user's ID.
            user_id = self.get_id_from_token(token)

        if not User.exists(user_id):
            await abort(404, f"User '{user_id}' not found on the server.")

        await jsonify(self.as_json(User.get_s(user_id).favorites))

    @route("/api/v1/users/<user_id>/mods")
    @json
    @db_session
    async def get_user_mods(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                await abort(400, "Unauthenticated request. calls to @me must be authenticated.")

            #override user_id value to be the value of authed user's ID.
            user_id = self.get_id_from_token(token)

        if not User.exists(user_id):
            await abort(404, f"User '{user_id}' not found on the server.")

        await jsonify(self.as_json(User.get_s(user_id).mods))

    @route("/api/v1/users/<user_id>/reviews")
    @json
    @db_session
    async def get_user_reviews(self, user_id: str):
        if user_id == "@me":
            token = request.headers.get("Authorization", request.cookies.get["token"])

            if token is None:
                await abort(400, "Unauthenticated request. calls to @me must be authenticated.")

            #override user_id value to be the value of authed user's ID.
            user_id = self.get_id_from_token(token)

        if not User.exists(user_id):
            await abort(404, f"User '{user_id}' not found on the server.")

        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        await jsonify(self.as_json(
            Review.select(lambda review: review.author.id == user_id).page(page)
        ))

async def setup(core: Sayonika):
    Userland(core).register()
