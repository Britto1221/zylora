class ZyloraError(Exception):
    status_code = 400
    code = "zylora_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConflictError(ZyloraError):
    status_code = 409
    code = "conflict"


class InsufficientCreditsError(ZyloraError):
    status_code = 409
    code = "insufficient_credits"


class AuthorizationError(ZyloraError):
    status_code = 403
    code = "forbidden"
