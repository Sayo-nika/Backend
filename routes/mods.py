import os
from datetime import datetime
from secrets import token_hex

from flask import jsonify, abort, request

from framework.objects import mods_json
from framework.route import route
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    def __init__(self, core: Sayonika):
        super().__init__(core)
        self.data = mods_json

    def new_path(self):
        used = [mod["path"] for mod in self.data["mods"]]
        path = token_hex(8)
        while path in used:
            path = token_hex(8)

        return path

    # === Mods ===
    # TODO: Owner auth
    # TODO: Finish endpoints
    @route("/api/v1/mods", methods=["POST"])
    @json
    def post_mods(self):
        file = request.files.get('file')

        if file is None or not file.endswith(".zip"):
            abort(400, "Expecting 'file' zipfile multipart.")

        mod = {}

        for attribute in ("title", "authors"):
            val = request.form.get(attribute)
            if val is None:
                abort(400, f"Missing POST parameter: '{attribute}'.")
            mod[attribute] = val

        if mod["title"] in [mod["title"] for mod in self.data["mods"]]:
            abort(400, f"A mod with the name '{mod['title']}' already exists.")

        mod["verified"] = False
        mod["last_updated"] = mod["released_at"] = datetime.utcnow().timestamp()
        mod["downloads"] = 0
        mod["path"] = self.new_path()

        file.save(f"mods/{mod['path']}.zip")

        self.data["mods"].append(mod)
        self.data["update"] = 0

        return jsonify(mod)

    @route("/api/v1/mods/<mod_name>", methods=["PATCH"])
    @json
    def patch_mod(self, mod_name):
        file = request.files.get('file')

        if file is None or not file.endswith(".zip"):
            abort(400, "Expecting 'file' zipfile multipart.")

        mod = {}

        for attribute in ("title", "authors"):
            val = request.form.get(attribute)
            if val is None:
                abort(400, f"Missing POST parameter: '{attribute}'.")
            mod[attribute] = val

        if mod_name not in [mod["title"] for mod in self.data["mods"]]:
            abort(400, f"The mod '{mod_name}' does not exist.")

        old_mod = [mod for mod in self.data["mods"] if mod["title"] == mod_name][0]

        mod["verified"] = old_mod["verified"]
        mod["last_updated"] = datetime.utcnow().timestamp()
        mod["downloads"] = old_mod["downloads"]
        mod["path"] = self.new_path()

        os.remove(f"mods/{old_mod['path']}.zip")
        file.save(f"mods/{mod['path']}.zip")

        self.data["mods"] = [mod for mod in self.data["mods"] if not mod["title"] == mod_name]
        self.data["mods"].append(mod)
        self.data["update"] = 0

        return jsonify(mod)

    @route("/api/v1/mods/<mod_name>/reviews", methods=["POST"])
    @json
    def post_review(self, mod_name: str):
        if mod_name not in [mod["title"] for mod in self.data["mods"]]:
            abort(400, f"The mod '{mod_name}' does not exist.")

        review = {"mod": mod_name}

        for attribute in ("author", "message"):
            val = request.form.get(attribute)
            if val is None:
                abort(400, f"Missing POST parameter: '{attribute}'.")
            mod[attribute] = val

        if review["author"] not in [user["name"] for user in self.data["users"]]
            abort(400, f"A user with name '{review['author']}' does not exist.")

        self.data["reviews"].append(review)

        return jsonify(review)

    @route("/api/v1/users", methods=["POST"])
    @json
    def post_users(self):
        user = {}

        for attribute in ("name", "bio"):
            val = request.form.get(attribute)
            if val is None:
                abort(400, f"Missing POST parameter: '{attribute}'.")
            user[attribute] = val

        if user["name"] in [user["name"] for user in self.data["users"]]
            abort(400, f"A user with name '{user['name']}' already exists.")

        user["mods"] = []
        user["favorites"] = []

        self.data["users"].append(user)

        return jsonify(user)

    @route("/api/v1/users/<user_name>", methods=["patch"])
    @json
    def patch_user(self, user_name: str):
        user = {}

        for attribute in ("name", "bio"):
            val = request.form.get(attribute)
            if val is None:
                abort(400, f"Missing POST parameter: '{attribute}'.")
            user[attribute] = val

        if user_name not in [user["name"] for user in self.data["users"]]
            abort(400, f"A user with name '{user['name']}' does not exist.")


        old_user = [user for user in self.data["users"]
                    if user["name"] == user_name][0]

        user["mods"] = old_user["mods"]
        user["favorites"] = old_user["favorites"]

        self.data["users"] = [user for user in self.data["users"] if not user["name"] == user_name]
        self.data["users"].append(user)
        self.data["update"] = 0

        return jsonify(user)


def setup(core: Sayonika):
    Userland(core).register()
