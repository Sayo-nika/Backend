# External Libraries
from flask import abort, jsonify, send_file

# Sayonika Internals
from framework.objects import mods_json
from framework.route import route, multiroute
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    def __init__(self, core: Sayonika):
        super().__init__(core)
        self.data = mods_json

        if self.data == {}:
            # Initial setup
            self.data["mods"] = []
            self.data["users"] = []
            self.data["reviews"] = []

    # === Mods ===

    @property
    def verified(self):
        return [mod for mod in self.data["mods"] if mod["verified"]]

    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    def get_mods(self):
        # TODO: Pagination
        return jsonify(self.verified)

    @route("/api/v1/mods/recent_releases")
    @json
    def get_recent_releases(self):
        sorted_mods = reversed(sorted(self.verified,
                                      key=lambda mod: mod["released_at"]))
        return jsonify(list(sorted_mods)[:10])

    @route("/api/v1/mods/popular")
    @json
    def get_popular(self):
        sorted_mods = sorted(self.verified,
                             key=lambda mod: mod["downloads"])  # Generator[Dict[str, Any]]
        return jsonify(list(sorted_mods)[:10])

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    def get_mod(self, mod_id: str):
        valid_mods = [mod for mod in self.verified
                      if mod["id"] == mod_id]

        if not valid_mods:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        return jsonify(valid_mods[0])

    @route("/api/v1/mods/<mod_id>/download")
    @json
    def get_download(self, mod_id: str):
        valid_mods = [mod for mod in self.verified
                      if mod["id"] == mod_id]

        if not valid_mods:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        return send_file(f"mods/{valid_mods[0]['path']}.zip")

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    def get_mod_reviews(self, mod_id: str):
        valid_mods = [mod for mod in self.verified
                      if mod["id"] == mod_id]

        if not valid_mods:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        reviews = [review for review in self.verified
                   if review["mod"] == mod_id]

        return jsonify(reviews)

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    def get_mod_authors(self, mod_id: str):
        valid_mods = [mod for mod in self.verified
                      if mod["id"] == mod_id]

        if not valid_mods:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        authors = [user for user in self.data["users"]
                   if user["id"] in valid_mods[0]["authors"]]

        return jsonify(authors)

    # === Users ===

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    def get_users(self):
        # TODO: Pagination
        return jsonify(self.data["users"])

    @multiroute("/api/v1/users/<user_id>", methods=["GET"], other_methods=["POST"])
    @json
    def get_user(self, user_id: str):
        valid_users = [user for user in self.data["users"]
                       if user["id"] == user_id]

        if not valid_users:
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(valid_users[0])

    @route("/api/v1/users/<user_id>/favorites")
    @json
    def get_favorites(self, user_id: str):
        valid_users = [user for user in self.data["users"]
                       if user["id"] == user_id]

        if not valid_users:
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(valid_users[0]["favorites"])

    @route("/api/v1/users/<user_id>/mods")
    @json
    def get_user_mods(self, user_id: str):
        valid_users = [user for user in self.data["users"]
                       if user["id"] == user_id]

        if not valid_users:
            return abort(404, f"User '{user_id}' not found on the server.")

        mods = [mod for mod in self.verified
                if mod["id"] in valid_users[0]["mods"]]

        return jsonify(mods)

    @route("/api/v1/users/<user_id>/reviews")
    @json
    def get_user_reviews(self, user_id: str):
        valid_users = [user for user in self.data["users"]
                       if user["name"] == user_name]

        if not valid_users:
            return abort(404, f"User '{user_id}' not found on the server.")

        reviews = [review for review in self.data["reviews"]
                   if review["id"] in valid_users[0]["reviews"]]

        return jsonify(reviews)


def setup(core: Sayonika):
    Userland(core).register()
