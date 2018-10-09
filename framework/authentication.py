# Stdlib
import json

# External Libraries
from flask import request

from keycloak import KeycloakOpenID


class Authenticator:
    """
    Service to check API key validity

    TODO: Rewrite with keycloak
    """
    def __init__(self, config_path: str):
        self.auth_tokens = []
        with open(config_path) as f:
            self.koid = KeycloakOpenID(json.load(f))

    def has_authorized_access(self, *args, **kwargs) -> bool:
        # TODO: Implement
        # Test if user has access to specified route and arguments
        # -> Does this page belong to this user?
        raise NotImplemented()

    def has_admin_access(self) -> bool:
        # TODO: Implement
        # Test if user has access to specified route and arguments
        # -> Does this user belong to the admin group?
        raise NotImplemented()
