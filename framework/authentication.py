# Stdlib
import hashlib

# External Libraries
from flask import abort, request
from pony.orm import db_session

# Sayonika Internals
from framework.models import User


class Authenticator:

    hash_class = hashlib.sha3_512

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        pass

    @db_session
    def has_authorized_access(self, _, **kwargs) -> bool:
        id_ = (request.json or request.form).get("id")
        pass_ = (request.json or request.form).get("password")
        if id_ is None or pass_ is None:
            abort(401, "User not authorized")

        user = User.get_s(id_)

        if user is None:
            abort(401, "Unknown user ID!")

        if not user.email_verified:
            abort(401, "Account needs verification")

        if self.hash_password(pass_) != user.password:
            abort(401, "Invalid login credentials!")

        if request.method == "PATCH":  # only check editing
            if "mod_id" in kwargs:
                if kwargs["mod_id"] not in (mod.id for mod in user.mods):
                    abort(403, "User does not have permission to access this resource")
            elif "user_id" in kwargs:
                if kwargs["user_id"] != user.id:
                    abort(403, "User does not have permission to access this resource")
            else:
                abort(400, "Nothing specified to edit.")
        return True

    def has_admin_access(self) -> bool:
        id_ = (request.json or request.form or request.args).get("id")
        pass_ = (request.json or request.form or request.args).get("password")

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
