"""Fonts formats sub-resource: client.fonts.formats"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ..._paths import FONTS_PREFIX
from ._common import normalize_format

if TYPE_CHECKING:
    from ..._client import Indox


class Formats:
    """
    Access font format information.

    Usage:
        client.fonts.formats.list()
        client.fonts.formats.get("ttf")
    """

    def __init__(self, client: "Indox") -> None:
        self._client = client

    def list(self) -> dict[str, Any]:
        """Get all engines with their supported formats."""
        return cast(dict[str, Any], self._client._http.get(f"{FONTS_PREFIX}/formats/"))

    def get(self, input_format: str) -> dict[str, Any]:
        """Get available output formats for a specific input format."""
        fmt = normalize_format(input_format)
        if not fmt:
            raise ValueError("input_format is required")
        return cast(
            dict[str, Any],
            self._client._http.get(f"{FONTS_PREFIX}/formats/{fmt}/"),
        )
