
class Authenticator:
    """
    Service to check API key validity

    TODO: Rewrite with keycloak
    """

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        pass

    def has_authorized_access(self, *args, **kwargs) -> bool:
        # TODO: Implement
        # Test if user has access to specified route and arguments
        # -> Does this page belong to this user?
        raise NotImplementedError()

    def has_admin_access(self) -> bool:
        # TODO: Implement
        # Test if user has access to specified route and arguments
        # -> Does this user belong to the admin group?
        raise NotImplementedError()
