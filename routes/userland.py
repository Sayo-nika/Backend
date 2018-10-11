# External Libraries
from datetime import datetime
from secrets import token_hex

from flask import abort, jsonify, send_file, request

# Sayonika Internals
from pony.orm import select, db_session
from simpleflake import simpleflake

from framework.models import User, Mod, Review
from framework.objects import database_handle
from framework.route import route, multiroute
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    def __init__(self, core: Sayonika):
        super().__init__(core)

    # === Compat with mods.py ===

    @db_session
    def new_path(self):
        used = [mod.path for mod in database_handle.mods]
        path = token_hex(8)
        while path in used:
            path = token_hex(8)

        return path

    @staticmethod
    def new_id():
        return str(simpleflake())

    # === Mods ===

    @staticmethod
    def as_json(data: list):
        return [item.json for item in data]

    @property
    def verified(self):
        return [mod for mod in database_handle.mods if mod.verified]

    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    def get_mods(self):
        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        return jsonify(self.as_json(Mod.select(lambda mod: mod.verified).page(page)))

    @route("/api/v1/mods/recent_releases")
    @json
    def get_recent_releases(self):
        sorted_mods = reversed(sorted(self.verified,
                                      key=lambda mod: mod["released_at"]))
        return jsonify(self.as_json(sorted_mods)[:10])

    @route("/api/v1/mods/popular")
    @json
    def get_popular(self):
        sorted_mods = sorted(self.verified,
                             key=lambda mod: mod["downloads"])  # Generator[Dict[str, Any]]
        return jsonify(self.as_json(sorted_mods)[:10])

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    def get_mod(self, mod_id: str):
        if Mod.exists(mod_id) is None:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        return jsonify(Mod.get_s(mod_id).json)

    @route("/api/v1/mods/<mod_id>/download")
    @json
    def get_download(self, mod_id: str):
        if Mod.exists(mod_id) is None:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        return send_file(f"mods/{valid_mods[0]['path']}.zip")

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    def get_mod_reviews(self, mod_id: str):
        if Mod.exists(mod_id) is None:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        reviews = select(review for review in Review if review.mod == mod_id)

        return jsonify(self.as_json(reviews))

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    def get_mod_authors(self, mod_id: str):
        if Mod.exists(mod_id) is None:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        authors = select(user for user in User if Mod.get_s(mod_id) in user.mods)

        return jsonify(self.as_json(authors))

    # === Users ===

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    def get_users(self):
        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        return jsonify(self.as_json(User.select().page(page)))

    @multiroute("/api/v1/users/<user_id>", methods=["GET"], other_methods=["POST"])
    @json
    def get_user(self, user_id: str):
        if User.exists(user_id) is None:
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(User.get_s(user_id).json)

    @route("/api/v1/users/<user_id>/favorites")
    @json
    def get_favorites(self, user_id: str):
        if User.exists(user_id) is None:
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(self.as_json(User.get_s(user_id).favorites))

    @route("/api/v1/users/<user_id>/mods")
    @json
    def get_user_mods(self, user_id: str):
        if User.exists(user_id) is None:
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(self.as_json(User.get_s(user_id).mods))

    @route("/api/v1/users/<user_id>/reviews")
    @json
    @db_session
    def get_user_reviews(self, user_id: str):
        if User.exists(user_id) is None:
            return abort(404, f"User '{user_id}' not found on the server.")

        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        return jsonify(self.as_json(Review.select(lambda review: review.author == user_id).page(page)))


def setup(core: Sayonika):
    Userland(core).register()
