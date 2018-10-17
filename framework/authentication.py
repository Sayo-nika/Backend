import hashlib

from flask import request, abort

from framework.models import User


class Authenticator:
    """
    Service to check API key validity

    TODO: Add OAuth2
    """

    hash_class = hashlib.sha3_512

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        pass

    def has_authorized_access(self, resource_id: str = None) -> bool:
        id_ = (request.json or request.form).get("id")
        pass_ = (request.json or request.form).get("password")

        if id_ is None or pass_ is None:
            abort(401, "User not authorized")

        user = User.get_s(id_)

        if user is None:
            abort(401, "Unknown user ID!")

        if self.hash_password(pass_) != user.password:
            abort(401, "Invalid login credentials!")

        if (request.method == "PATCH" and  # only check editing
            not any(resource_id in collection
                    for collection in (
                        (mod.id for mod in user.mods),  # User can edit their own mods
                        (review.id for review in user.reviews),  # User can edit their own reviews
                        (user.id,)  # User can edit themselves
                    ))):
            abort(403, "User does not have permission to access this resource")

        return True

    def has_admin_access(self) -> bool:
        id_ = (request.json or request.form).get("id")
        pass_ = (request.json or request.form).get("password")

        if id_ is None or pass_ is None:
            abort(401, "User not authorized")
        user = User.get_s(id_)

        if user is None:
            abort(401, "Unknown user ID!")

        if self.hash_password(pass_) != user.password:
            abort(401, "Invalid login credentials!")

        if not user.moderator:
            abort(403, "User does not have required permissions!")

        return True

    @classmethod
    def hash_password(cls, password: str) -> bytes:
        inst = cls.hash_class()
        inst.update(password.encode())
        return inst.digest()
