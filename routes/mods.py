# Stdlib
from datetime import datetime
import os
from secrets import token_hex

# External Libraries
from flask import abort, jsonify, request
from pony.orm import select, db_session

# Sayonika Internals
from simpleflake import simpleflake

from framework.models import Mod, User
from framework.objects import database_handle
from framework.route import multiroute
from framework.route_wrappers import json, requires_keycloak_login
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Mods(RouteCog):
    def __init__(self, core: Sayonika):
        super().__init__(core)

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
    @multiroute("/api/v1/mods", methods=["POST"], other_methods=["GET"])
    @requires_keycloak_login
    @json
    def post_mods(self):
        file = request.files.get('file')

        if file is None or not file.filename.endswith(".zip"):
            return abort(400, "Expecting 'file' zipfile multipart.")

        mod = {}

        for attribute in ("title", "authors"):
            val = request.json.get(attribute)
            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")
            mod[attribute] = val

        if Mod.get(title=mod["title"]) is not None:
            return abort(400, f"A mod with the name '{mod['title']}' already exists.")

        mod["verified"] = False
        mod["last_updated"] = mod["released_at"] = datetime.utcnow().timestamp()
        mod["downloads"] = 0
        mod["path"] = self.new_path()
        mod["id"] = self.new_id()

        file.save(f"mods/{mod['path']}.zip")

        return jsonify(database_handle.new_mod(**mod).json)

    @multiroute("/api/v1/mods/<mod_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_keycloak_login
    @json
    def patch_mod(self, mod_id: str):
        file = request.files.get('file')

        if file is None or not file.endswith(".zip"):
            return abort(400, "Expecting 'file' zipfile multipart.")

        mod = {}

        for attribute in ("title", "authors"):
            val = request.json.get(attribute)
            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")
            mod[attribute] = val

        if Mod.exists(mod_id) is None:
            return abort(400, f"The mod '{mod_id}' does not exist.")

        old_mod = Mod.get_s(mod_id)

        mod["path"] = self.new_path()

        os.remove(f"mods/{old_mod.path}.zip")
        file.save(f"mods/{mod['path']}.zip")

        database_handle.edit_mod(old_mod.id, **mod)

        return jsonify(old_mod.json)

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["POST"], other_methods=["GET"])
    @requires_keycloak_login
    @json
    def post_review(self, mod_id: str):
        if Mod.exists(mod_id) is None:
            return abort(400, f"The mod '{mod_id}' does not exist.")

        review = {"mod": mod_id}

        for attribute in ("author", "message"):
            val = request.json.get(attribute)
            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")
            review[attribute] = val

        if User.get(review["author"]) is None:
            return abort(400, f"A user with ID '{review['author']}' does not exist.")

        review["id"] = self.new_id()

        return jsonify(database_handle.new_review(**review).json)

    @multiroute("/api/v1/users", methods=["POST"], other_methods=["GET"])
    #@requires_keycloak_login
    @json
    def post_users(self):
        user = {}

        for attribute in ("name", "bio"):
            val = request.json.get(attribute)
            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")
            user[attribute] = val

        user["mods"] = []
        user["favorites"] = []
        user["id"] = self.new_id()

        return jsonify(database_handle.new_user(**user).json)

    @multiroute("/api/v1/users/<user_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_keycloak_login
    @json
    def patch_user(self, user_id: str):
        user = {}

        for attribute in ("name", "bio"):
            val = request.json.get(attribute)
            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")
            user[attribute] = val

        if User.exists(user_id) is None:
            return abort(400, f"A user with ID '{user['id']}' does not exist.")

        old_user = User.get_s(user_id)

        database_handle.edit_user(user_id, **user)

        return jsonify(old_user.json)


def setup(core: Sayonika):
    Mods(core).register()
