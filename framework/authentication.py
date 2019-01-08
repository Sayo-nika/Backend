# Stdlib
import hashlib

# External Libraries
from quart import abort, request

# Sayonika Internals
from framework.models import User
import framework.objects


class Authenticator:
    hash_class = hashlib.sha3_512

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        pass

    async def has_authorized_access(self, _, **kwargs) -> bool:
        token = request.headers.get("Authorization", request.cookies.get('token'))

        if token is None:
            abort(401, "No token")

        # I blame py's abhorrent handling of circular dependencies for this
        parsed_token = await framework.objects.jwt_service.verify_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid token")

        user = await User.get(parsed_token.id)

        if not user.email_verified:
            abort(401, "User email needs to be verified")

        if request.method == "PATCH":  # only check editing
            if "mod_id" in kwargs:
                if kwargs["mod_id"] not in (mod.id for mod in user.mods):
                    abort(403, "User does not have the required permissions to fulfill the request.")
            elif "user_id" in kwargs:
                if kwargs["user_id"] != user.id:
                    abort(403, "User does not have the required permissions to fulfill the request.")
            else:
                abort(400, "Nothing specified to edit")

        return True

    async def has_supporter_features(self) -> bool:
        token = request.headers.get("Authorization", request.cookies.get('token'))

        if token is None:
            abort(401)

        parsed_token = await framework.objects.jwt_service.verify_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid Token")

        user = await User.get(parsed_token.id)

        if not user.supporter:
            abort(403, "User does not have the required permissions to fulfill the request.")

        return True

    async def has_admin_access(self) -> bool:
        token = request.headers.get("Authorization", request.cookies.get('token'))

        if token is None:
            abort(401)

        parsed_token = await framework.objects.jwt_service.verify_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid token.")

        user = await User.get(parsed_token.id)

        if not user.moderator or not user.developer:
            abort(403, "User does not have the required permissions to fulfill the request.")

        return True

    @classmethod
    async def hash_password(cls, password: str) -> bytes:
        inst = cls.hash_class()
        inst.update(password.encode())
        return inst.digest()
