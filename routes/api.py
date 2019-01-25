# External Libraries
from quart import jsonify, request

# Sayonika Internals
from framework.authentication import Authenticator
from framework.models import User
from framework.objects import jwt_service
from framework.route import route
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import abort


class Userland(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    # === Mods ===

    @route("/api/v1/login", methods=["POST"])
    @json
    async def login(self):
        body = await request.json
        username = body.get("username")
        password = body.get("password")

        if username is None or password is None:
            return abort(400, "Needs `username` and `password`")

        user = await User.get_any(True, username=username, email=username).first()

        if not user:
            return abort(400, "Invalid username or email")

        if Authenticator.hash_password(password) != user.password:
            return abort(400, "Invalid password")

        if not user.email_verified:
            return abort(401, "Email needs to be verified")

        token = jwt_service.make_token(user.id, user.last_pass_reset)

        return jsonify(token=token)


def setup(core: Sayonika):
    Userland(core).register()
