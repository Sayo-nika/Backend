# Stdlib
from datetime import datetime, timedelta
from typing import Union

# External Libraries
import jwt

# Sayonika Internals
# from framework.models import User
from framework.jsonutils import CombinedEncoder
import framework.models


class JWT:
    """Class for generating and validating JWTs."""

    algorithm = "HS256"

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        self.secret = settings["JWT_SECRET"]

    def _make_token(self, payload: dict) -> str:
        """Internal method for generating a token with consistent settings."""
        payload.update(iat=datetime.utcnow())

        return jwt.encode(
            payload, self.secret, algorithm=self.algorithm, json_encoder=CombinedEncoder
        ).decode()

    def make_login_token(self, id_: str, password_reset: datetime) -> str:
        """Generates a token to be used for regular authentication."""
        payload = {
            "id": id_,
            "lr": password_reset,
        }

        return self._make_token(payload)

    def make_email_token(self, id_: str, email: str) -> str:
        """Generates a token to be used for verifying user's emails."""
        payload = {
            "id": id_,
            "email": email,
            "exp": datetime.utcnow() + timedelta(days=1),
        }

        return self._make_token(payload)

    async def verify_login_token(
        self, token: str, return_parsed: bool = False
    ) -> Union[dict, bool]:
        """Verify/validates a login token, and returns its data if specified."""
        try:
            decoded = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.PyJWTError:
            return False  # Any errors thrown during decoding probably indicate bad token in some way

        if set(decoded.keys()) != set(["id", "lr", "iat"]):
            return False  # Keys should only be the ones we give

        user = await framework.models.User.get(decoded["id"])

        if (
            user is None
            or datetime.fromisoformat(decoded["lr"]) != user.last_pass_reset
        ):
            return False

        return decoded if return_parsed else True

    async def verify_email_token(self, token: str, return_parsed: bool = False):
        """Verify/validates an email token, and returns its data if specified."""
        try:
            decoded = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.PyJWTError:
            return False

        if set(decoded.keys()) != set(["id", "email", "exp", "iat"]):
            return False

        user = await framework.models.User.get_any(
            id=decoded["id"], email=decoded["email"]
        ).first()

        if user is None or user.id != decoded["id"] or user.email != decoded["email"]:
            return False

        return decoded if return_parsed else True
