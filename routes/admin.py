# External Libraries
from flask import abort, jsonify

# Sayonika Internals
from framework.objects import mods_json
from framework.route import route
from framework.route_wrappers import json, requires_keycloak_admin
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
    @requires_keycloak_admin
    @json
    def get_queue(self):
        return jsonify(self.unverified)

    @route("/api/v1/<mod_id>/verify", methods=["POST"])
    @requires_keycloak_admin
    @json
    def post_verify(self, mod_id: str):
        valid_mods = [mod for mod in self.unverified
                      if mod["id"] == mod_id]

        if not valid_mods:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        valid_mods[0]["verified"] = True
        self.data["update"] = 0

        return jsonify(f"Mod '{mod_id}' was succesfully verified.")

    @route("/api/v1/<mod_id>/reject", methods=["POST"])
    @requires_keycloak_admin
    @json
    def post_reject(self, mod_id: str):
        valid_mods = [mod for mod in self.unverified
                      if mod["id"] == mod_id]

        if not valid_mods:
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        valid_mods[0]["verified"] = True
        self.data["update"] = 0

        return jsonify(f"Mod '{mod_id}' was succesfully rejected.")


def setup(core: Sayonika):
    Admin(core).register()
