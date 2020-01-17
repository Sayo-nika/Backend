# External Libraries
import bcrypt
from quart import abort, request

# Sayonika Internals
from framework.models import Mod, User, ModAuthor
from framework.objects import jwt_service


class Authenticator:
    """
    Class for checking permissions of users, and hashing passwords.
    """

    @classmethod
    async def has_authorized_access(cls, _, **kwargs) -> bool:
        """Checks if a user has a valid token and has verified email."""
        token = request.headers.get("Authorization", request.cookies.get("token"))

        if token is None:
            abort(401, "No token")

        parsed_token = await jwt_service.verify_login_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid token")

        user = await User.get(parsed_token["id"])

        if not user.email_verified:
            abort(401, "User email needs to be verified")

        # XXX: this gives site devs unrestricted access. Limit in v2.
        if user.developer:
            return True

        if request.method != "GET":  # Check all methods other than get
            if "mod_id" in kwargs:
                user_mods = await Mod.query.where(
                    ModAuthor.user_id == user.id
                ).gino.all()

                if not (user.developer or user.moderator) and kwargs["mod_id"] not in (
                    mod.id for mod in user_mods
                ):
                    abort(
                        403,
                        "User does not have the required permissions to fulfill the request.",
                    )

        return True

    @classmethod
    async def has_supporter_features(cls) -> bool:
        """Check if a user is a supporter."""
        token = request.headers.get("Authorization", request.cookies.get("token"))

        if token is None:
            abort(401)

        parsed_token = await jwt_service.verify_login_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid token")

        user = await User.get(parsed_token["id"])

        if not user.supporter:
            abort(
                403,
                "User does not have the required permissions to fulfill the request.",
            )

        return True

    @classmethod
    async def has_admin_access(cls, developer_only: bool = False) -> bool:
        """Check if a user is an admin."""
        token = request.headers.get("Authorization", request.cookies.get("token"))

        if token is None:
            abort(401)

        parsed_token = await jwt_service.verify_login_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid token")

        user = await User.get(parsed_token["id"])

        if (developer_only and not user.developer) or (
            not developer_only and (not user.moderator and not user.developer)
        ):
            abort(
                403,
                "User does not have the required permissions to fulfill the request.",
            )

        return True

    @classmethod
    def hash_password(cls, password: str) -> bytes:
        """Hashes a password and returns the digest."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    @classmethod
    def compare_password(cls, password: str, hash_: bytes):
        """Compares a password against hash_"""
        return bcrypt.checkpw(password.encode(), hash_)
