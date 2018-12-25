# Stdlib
from datetime import datetime

# External Libraries
import jwt
from pony.orm import db_session

# Sayonika Internals
from framework.models import User

class JWT:
    algorithm = 'HS256'

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        self.secret = settings["JWT_SECET"]

    def make_token(self, id, password_reset):
        payload = {
            "id": id,
            "lr": password_reset,
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)

        return token

    @db_session
    def verify_token(self, token, return_parsed=False):
        try:
            decoded = jwt.decode(token, self.secret, algorithms=self.algorithm)
        except:
            return False # Any errors thrown during decoding probably indicate bad token in some way

        if set(decoded.keys()) != set(["id", "lr", "iat"]):
            return False # Keys should only be the ones we give

        user = User.get_s(decoded["id"])

        if user is None or decoded["lr"] != user.last_pass_reset or decoded["iat"] < datetime.utcnow():
            return False

        return decoded if returned_parsed else True
