from flask import jsonify, abort, send_file

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
                                      key=lambda mod: mod["released_at"]))  # Generator[Dict[str, Any]]
        return jsonify(list(sorted_mods)[:10])

    @route("/api/v1/mods/popular")
    @json
    def get_popular(self):
        sorted_mods = sorted(self.verified,
                             key=lambda mod: mod["downloads"])  # Generator[Dict[str, Any]]
        return jsonify(list(sorted_mods)[:10])

    @multiroute("/api/v1/mods/<mod_name>", methods=["GET"], other_methods=["PATCH"])
    @json
    def get_mod(self, mod_name: str):
        valid_mods = [mod for mod in self.verified
                      if mod["title"] == mod_name]

        if not valid_mods:
            abort(404, f"Mod '{mod_name}' not found on the server.")

        return jsonify(valid_mods[0])

    @route("/api/v1/mods/<mod_name>/download")
    @json
    def get_download(self, mod_name: str):
        valid_mods = [mod for mod in self.verified
                      if mod["title"] == mod_name]

        if not valid_mods:
            abort(404, f"Mod '{mod_name}' not found on the server.")

        return send_file(f"mods/{valid_mods[0]['path']}.zip")

    @multiroute("/api/v1/mods/<mod_name>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    def get_mod_reviews(self, mod_name: str):
        valid_mods = [mod for mod in self.verified
                      if mod["title"] == mod_name]

        if not valid_mods:
            abort(404, f"Mod '{mod_name}' not found on the server.")

        reviews = [review for review in self.verified
                   if review["mod"] == mod_name]

        return jsonify(reviews)

    @route("/api/v1/mods/<mod_name>/authors")
    @json
    def get_mod_authors(self, mod_name: str):
        valid_mods = [mod for mod in self.verified
                      if mod["title"] == mod_name]

        if not valid_mods:
            abort(404, f"Mod '{mod_name}' not found on the server.")

        authors = [user for user in self.data["users"]
                   if user["name"] in valid_mods[0]["authors"]]

        return jsonify(authors)

    # === Users ===

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    def get_users(self):
        # TODO: Pagination
        return jsonify(self.data["users"])

    @multiroute("/api/v1/users/<user_name>", methods=["GET"], other_methods=["POST"])
    @json
    def get_user(self, user_name: str):
        valid_users = [user for user in self.data["users"]
                       if user["name"] == user_name]

        if not valid_users:
            abort(404, f"Mod '{user_name}' not found on the server.")

        return jsonify(valid_users[0])

    @route("/api/v1/users/<user_name>/favorites")
    @json
    def get_favorites(self, user_name: str):
        valid_users = [user for user in self.data["users"]
                       if user["name"] == user_name]

        if not valid_users:
            abort(404, f"Mod '{user_name}' not found on the server.")

        return jsonify(valid_users[0]["favorites"])

    @route("/api/v1/users/<user_name>/mods")
    @json
    def get_user_mods(self, user_name: str):
        valid_users = [user for user in self.data["users"]
                       if user["name"] == user_name]

        if not valid_users:
            abort(404, f"Mod '{user_name}' not found on the server.")

        mods = [mod for mod in self.verified
                if mod["title"] in valid_users[0]["mods"]]

        return jsonify(mods)

    @route("/api/v1/users/<user_name>/reviews")
    @json
    def get_user_reviews(self, user_name: str):
        valid_users = [user for user in self.data["users"]
                       if user["name"] == user_name]

        if not valid_users:
            abort(404, f"Mod '{user_name}' not found on the server.")

        reviews = [review for review in self.data["reviews"]
                   if review["id"] in valid_users[0]["reviews"]]

        return jsonify(reviews)


def setup(core: Sayonika):
    Userland(core).register()
