# Stdlib
from datetime import datetime
import os
from secrets import token_hex
from typing import Iterator

# External Libraries
from flask import abort, jsonify, request
from pony.orm import db_session
from simpleflake import simpleflake

# Sayonika Internals
from framework.authentication import Authenticator
from framework.models import Mod, User, ModStatus, Base
from framework.objects import database_handle
from framework.route import multiroute
from framework.route_wrappers import json, requires_login
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Mods(RouteCog):

    @staticmethod
    @db_session
    def new_path() -> str:
        used = [mod.path for mod in database_handle.mods]  # flake8: noqa pylint: disable=not-an-iterable
        path = token_hex(8)
        while path in used:
            path = token_hex(8)

        return path

    @staticmethod
    def new_id() -> str:
        return str(simpleflake())  # easier than converting ID passed to route to int every time

    @staticmethod
    def as_json(data: Iterator[Base]):
        return [item.json for item in data]

    # === Mods ===
    @multiroute("/api/v1/mods", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    @db_session
    def post_mods(self):
        file = request.files.get('file')

        if file is None or not file.filename.endswith(".zip"):
            return abort(400, "Expecting 'file' zipfile multipart.")

        mod = {
            "verified": False,
            "last_updated": round(datetime.utcnow().timestamp()),
            "downloads": 0,
            "path": self.new_path(),
            "id": self.new_id(),
            "reviews": [],
            "favorite_by": [],
        }

        for attribute in ("title", "authors", "tagline", "description", "website"):
            val = request.form.get(attribute)

            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")

            mod[attribute] = val

        mods = Mod.get_any(True, title=mod["title"])

        if mods:
            return abort(400, "A mod with that title already exists")

        mod["authors"] = [User.get_s(id_) for id_ in mod["authors"].split(",") if User.exists(id_)]

        mod["icon"] = request.form.get("icon")
        attr = request.form.get("status", "Planning")
        mod["status"] = getattr(ModStatus, attr) if hasattr(ModStatus, attr) else int(attr)

        mod["released_at"] = mod["last_updated"]

        file.save(f"mods/{mod['path']}.zip")

        print(mod)

        db_mod = database_handle.new_mod(**mod)
        db_mod.authors.add(mod["authors"])

        return jsonify(db_mod.json)

    @multiroute("/api/v1/mods/<mod_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_login
    @json
    @db_session
    def patch_mod(self, mod_id: str):
        file = request.files.get('file')

        if file is None or not file.filename.endswith(".zip"):
            return abort(400, "Expecting 'file' zipfile multipart.")

        mod = {}

        for attribute in ("title", "authors", "tagline", "description", "website", "icon"):
            val = request.form.get(attribute)

            if val is not None:
                mod[attribute] = val

        if not Mod.exists(mod_id):
            return abort(400, f"The mod '{mod_id}' does not exist.")

        if "authors" in mod:
            mod["authors"] = [User.get_s(id_) for id_ in mod["authors"].split(",")
                              if User.exists(id_)]

        old_mod = Mod.get_s(mod_id)

        attr = request.form.get("status", None)
        if attr is None:
            mod["status"] = old_mod.status
        else:
            mod["status"] = getattr(ModStatus, attr) if hasattr(ModStatus, attr) else int(attr)

        mod["path"] = self.new_path()

        os.remove(f"mods/{old_mod.path}.zip")
        file.save(f"mods/{mod['path']}.zip")

        database_handle.edit_mod(old_mod.id, **mod)

        return jsonify(old_mod.json)

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    def post_review(self, mod_id: str):

        if not Mod.exists(mod_id):
            return abort(400, f"The mod '{mod_id}' does not exist.")

        review = {"mod": mod_id}

        for attribute in ("author", "content", "rating"):
            val = request.json.get(attribute)
            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")
            review[attribute] = val

        if not User.exists(review["author"]):
            return abort(400, f"A user with ID '{review['author']}' does not exist.")

        review["id"] = self.new_id()
        return jsonify(database_handle.new_review(**review).json)

    @multiroute("/api/v1/users", methods=["POST"], other_methods=["GET"])
    @json
    @db_session
    def post_users(self):
        user = {
            "mods": [],
            "favorites": [],
            "reviews": [],
            "upvoted": [],
            "downvoted": [],
            "helpful": [],
            "id": self.new_id(),
            "developer": False,
            "moderator": False,
            "donator": False,
            "editor": False
        }

        for attribute in ("username", "password", "email"):
            val = request.json.get(attribute)

            if val is None:
                return abort(400, f"Missing POST parameter: '{attribute}'.")

            user[attribute] = val

        users = User.get_any(True, username=user["username"], email=user["email"])

        if users:
            return abort(400, "Username and/or email already in use")

        user["avatar"] = request.json.get("avatar")
        user["bio"] = request.json.get("bio")
        user["password"] = Authenticator.hash_password(user["password"])

        return jsonify(database_handle.new_user(**user).json)

    @multiroute("/api/v1/users/<user_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_login
    @json
    @db_session
    def patch_user(self, user_id: str):  # pylint: disable=no-self-use
        user = {}

        # Masks password behind new_password, as "password" in the JSON is the password to auth
        # which means we can't just use it to PATCH with.
        for attribute in ("username", "bio", "new_password", "avatar", "email"):
            val = request.json.get(attribute)

            if val is not None:
                if attribute == "new_password":
                    user["password"] = Authenticator.hash_password(val)
                    user["last_pass_reset"] = int(datetime.utcnow().timestamp())
                else:
                    user[attribute] = val

        if not User.exists(user_id):
            return abort(400, f"A user with ID '{user_id}' does not exist.")

        old_user = User.get_s(user_id)

        database_handle.edit_user(user_id, **user)

        return jsonify(old_user.json)

    # This handles PATCH requests to add a mod_content URL.
    # Usually this would be done via a whole entry but this
    # is designed for existing content.
    @route("/api/v1/mods/<mod_id>/upload_content", methods=["PATCH"])
    @json
    @requires_supporter
    @requires_login
    def upload(self, mod_id: str): #pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id} not found on this server'")
        
        return abort(501, "Not implemented. Work In Progress. I blame Mart")

    # --- @me aliases ---
    @route("/api/v1/users/@me", methods=["PATCH"], other_methods=["GET"])
    @requires_login
    @db_session 


def setup(core: Sayonika):
    Mods(core).register()
