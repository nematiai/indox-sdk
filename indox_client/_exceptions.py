"""Exception hierarchy for the Indox SDK."""

from __future__ import annotations

from typing import Any, Mapping, Optional


class IndoxError(Exception):
    """Base class for all Indox SDK errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class APIConnectionError(IndoxError):
    """Raised when connection to API fails."""

    pass


class APIStatusError(IndoxError):
    """Raised when API returns non-success status."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: Optional[Mapping[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}
        self.request_id = request_id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"status_code={self.status_code})"
        )


class BadRequestError(APIStatusError):
    """400 Bad Request."""

    pass


class PaymentRequiredError(APIStatusError):
    """402 Payment Required - insufficient credits."""

    pass


class AuthenticationError(APIStatusError):
    """401 Unauthorized."""

    pass


class PermissionDeniedError(APIStatusError):
    """403 Forbidden."""

    pass


class NotFoundError(APIStatusError):
    """404 Not Found."""

    pass


class RateLimitError(APIStatusError):
    """429 Too Many Requests."""

    pass


class InternalServerError(APIStatusError):
    """5xx Server Error."""

    pass


class ConversionError(IndoxError):
    """Raised when a conversion fails."""

    def __init__(self, message: str, *, conversion_id: Optional[str] = None) -> None:
        super().__init__(message)
        self.conversion_id = conversion_id


class ConversionTimeoutError(IndoxError):
    """Raised when conversion polling times out."""

    pass


def raise_for_status(status_code: int, message: str, **kwargs: Any) -> None:
    """Raise appropriate exception based on status code."""
    error_map = {
        400: BadRequestError,
        401: AuthenticationError,
        402: PaymentRequiredError,
        403: PermissionDeniedError,
        404: NotFoundError,
        429: RateLimitError,
    }

    if status_code >= 500:
        raise InternalServerError(message, status_code=status_code, **kwargs)

    error_class = error_map.get(status_code, APIStatusError)
    raise error_class(message, status_code=status_code, **kwargs)
