"""Public errors contain fixed, credential-free messages."""


class StudioError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


class CredentialsRequiredError(StudioError):
    def __init__(self):
        super().__init__(
            "Reconnect an API key for this operation's original provider and model, then resume. "
            "The session expired, was removed, was rejected, or was lost on server restart.",
            428,
        )
