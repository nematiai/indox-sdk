"""
Indox Python SDK (API v1)

Usage:
    >>> from indox_client import Indox
    >>> client = Indox(api_key="your-api-key")
    >>> client.fonts.formats.list()
    >>> client.pdf.formats()
    >>> client.images.formats()
    >>> client.user.me()
    >>> client.billing.credits_balance()
"""

from ._client import Indox
from ._exceptions import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConversionError,
    ConversionTimeoutError,
    IndoxError,
    InternalServerError,
    NotFoundError,
    PaymentRequiredError,
    PermissionDeniedError,
    RateLimitError,
)
from ._version import __version__

__all__ = [
    "__version__",
    "Indox",
    "IndoxError",
    "APIConnectionError",
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "PaymentRequiredError",
    "PermissionDeniedError",
    "NotFoundError",
    "RateLimitError",
    "InternalServerError",
    "ConversionError",
    "ConversionTimeoutError",
]
