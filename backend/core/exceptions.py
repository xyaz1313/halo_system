"""Typed exception hierarchy for service layers.

Services raise these; global FastAPI exception handlers in main.py map them
to the appropriate HTTP status codes.
"""


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Not found"):
        self.detail = detail
        super().__init__(detail)


class AlreadyExistsError(Exception):
    """Raised when a create/link would violate a uniqueness constraint."""

    def __init__(self, detail: str = "Already exists"):
        self.detail = detail
        super().__init__(detail)


class ValidationError(Exception):
    """Raised when a business-rule validation fails (not schema validation)."""

    def __init__(self, detail: str = "Validation error"):
        self.detail = detail
        super().__init__(detail)


class AccessDeniedError(Exception):
    """Raised when an operation is not permitted for the given context."""

    def __init__(self, detail: str = "Access denied"):
        self.detail = detail
        super().__init__(detail)
