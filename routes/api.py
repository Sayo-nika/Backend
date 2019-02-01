# External Libraries
from quart import jsonify, request, abort, Response

# Sayonika Internals
from framework.authentication import Authenticator
from framework.models import User
from framework.objects import jwt_service
from framework.route import route
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


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
            abort(400, "Needs `username` and `password`")

        user = await User.get_any(True, username=username, email=username).first()

        if not user:
            abort(400, "Invalid username or email")

        if Authenticator.hash_password(password) != user.password:
            abort(400, "Invalid password")

        if not user.email_verified:
            abort(401, "Email needs to be verified")

        token = jwt_service.make_login_token(user.id, user.last_pass_reset)

        return jsonify(token=token)

    @route("/api/v1/verify", methods=["POST"])
    async def verify_email():
        token = request.args.get("token")

        if token is None:
            abort(400, "missing required parameter 'token'.")

        parsed_token = jwt_service.verify_token(token, True)

        if parsed_token is False:
            abort(403, "Incorrect token.")

        user = User.get(parsed_token.id)

        if user is None:
            abort(410, "Valid token, but user to validate does not exist.")

        await user.update(email_verified=True).apply()

        return Response(response="OK.", status=200, content_type="text/plain")


def setup(core: Sayonika):
    Userland(core).register()
