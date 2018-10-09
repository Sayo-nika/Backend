# External Libraries
from flask import abort, jsonify

# Sayonika Internals
from framework.objects import mods_json
from framework.route import route
from framework.route_wrappers import json, auth_only
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Admin(RouteCog):
    def __init__(self, core: Sayonika):
        super().__init__(core)
        self.data = mods_json

        # No setup here, userland will handle it

    # === Verify ===

    @property
    def unverified(self):
        return [mod for mod in self.data["mods"] if not mod["verified"]]

    @route("/api/v1/mods/verify_queue")
    @auth_only
    @json
    def get_queue(self):
        return jsonify(self.unverified)

    @route("/api/v1/<mod_name>/verify", methods=["POST"])
    @auth_only
    @json
    def post_verify(self, mod_name: str):
        valid_mods = [mod for mod in self.unverified
                      if mod["title"] == mod_name]

        if not valid_mods:
            abort(404, f"Mod '{mod_name}' not found on the server.")

        valid_mods[0]["verified"] = True
        self.data["update"] = 0

        return jsonify(f"Mod '{mod_name}' was succesfully verified.")

    @route("/api/v1/<mod_name>/reject", methods=["POST"])
    @auth_only
    @json
    def post_reject(self, mod_name: str):
        valid_mods = [mod for mod in self.unverified
                      if mod["title"] == mod_name]

        if not valid_mods:
            abort(404, f"Mod '{mod_name}' not found on the server.")

        valid_mods[0]["verified"] = True
        self.data["update"] = 0

        return jsonify(f"Mod '{mod_name}' was succesfully rejected.")


def setup(core: Sayonika):
    Admin(core).register()
