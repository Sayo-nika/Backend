# External Libraries
from flask import abort, jsonify
from pony.orm import delete, db_session

# Sayonika Internals
from framework.models import Mod
from framework.objects import database_handle
from framework.route import route
from framework.route_wrappers import json, requires_admin
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Admin(RouteCog):
    # === Verify ===

    @staticmethod
    @property
    def unverified():
        return [mod for mod in database_handle.mods if not mod.verified]  # flake8: noqa pylint: disable=not-an-iterable

    @staticmethod
    def as_json(data: list):
        return [item.json for item in data]

    @route("/api/v1/mods/verify_queue")
    @requires_admin
    @json
    def get_queue(self):
        return jsonify(self.as_json(self.unverified))

    @route("/api/v1/<mod_id>/verify", methods=["POST"])
    @requires_admin
    @json
    def post_verify(self, mod_id: str):  # pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        database_handle.edit_mod(mod_id, verified=True)

        return jsonify(f"Mod '{mod_id}' was succesfully verified.")

    @route("/api/v1/<mod_id>/reject", methods=["POST"])
    @requires_admin
    @json
    @db_session
    def post_reject(self, mod_id: str):  # pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        delete(Mod.get_s(mod_id))

        return jsonify(f"Mod '{mod_id}' was succesfully rejected.")


def setup(core: Sayonika):
    Admin(core).register()
