import uuid
import requests
from typing import Optional


class RollyPay:
    BASE_URL = "https://rollypay.io/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _headers(self):
        return {
            "X-API-Key": self.api_key,
            "X-Nonce": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

    def create_payment(
        self,
        amount: float,
        order_id: str,
        description: str = "",
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> dict:

        payload = {
            "amount": f"{amount:.2f}",
            "payment_currency": "RUB",
            "payment_method": "sbp",
            "order_id": order_id,
            "description": description,
        }

        if success_url:
            payload["success_redirect_url"] = success_url

        if fail_url:
            payload["fail_redirect_url"] = fail_url

        if customer_id:
            payload["customer_id"] = customer_id

        response = requests.post(
            f"{self.BASE_URL}/payments",
            json=payload,
            headers=self._headers(),
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    def get_pay_url(
        self,
        amount: float,
        order_id: str,
        description: str = ""
    ) -> tuple[str, str]:

        payment = self.create_payment(
            amount=amount,
            order_id=order_id,
            description=description
        )

        return (
            payment["payment_id"],
            payment["pay_url"]
        )

    def get_payment(self, payment_id: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/payments/{payment_id}",
            headers=self._headers(),
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    def get_payment_status(self, payment_id: str) -> str:
        payment = self.get_payment(payment_id)
        return payment["status"]

    def is_paid(self, payment_id: str) -> bool:
        status = self.get_payment_status(payment_id)
        return status == "paid"