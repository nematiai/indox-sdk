"""Billing / subscription resource (P3 non-admin): client.billing"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._paths import SUBSCRIPTION_PREFIX
from ._helpers import as_dict

if TYPE_CHECKING:
    from .._client import Indox


class Billing:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def credits_balance(self) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{SUBSCRIPTION_PREFIX}/credits/balance/")
        )

    def redeem_promo(self, code: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{SUBSCRIPTION_PREFIX}/credits/promo-code/",
                json_body={"code": code},
            )
        )

    def pricing_plans(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{SUBSCRIPTION_PREFIX}/pricing_plan/"))

    def purchase_initiate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{SUBSCRIPTION_PREFIX}/purchase_initiate/",
                json_body=payload,
            )
        )

    def purchase_pay_as_you_go(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{SUBSCRIPTION_PREFIX}/purchase_initiate/pay-as-you-go/",
                json_body=payload,
            )
        )

    def purchase_history(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{SUBSCRIPTION_PREFIX}/purchase_history/",
                params=params or None,
            )
        )

    def storage_initiate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{SUBSCRIPTION_PREFIX}/storage/initiate/",
                json_body=payload,
            )
        )

    def task_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{SUBSCRIPTION_PREFIX}/tasks/task-completion/",
                json_body=payload,
            )
        )

    def task_history(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{SUBSCRIPTION_PREFIX}/tasks/task-history/",
                params=params or None,
            )
        )

    def purchase_callback(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{SUBSCRIPTION_PREFIX}/purchase_initiate/callback/",
                params=params or None,
            )
        )

    def storage_callback(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{SUBSCRIPTION_PREFIX}/storage/callback/",
                params=params or None,
            )
        )
