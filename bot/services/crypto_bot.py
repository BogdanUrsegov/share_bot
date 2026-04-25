import aiohttp
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class CryptoBotAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://pay.crypt.bot/api"
        self.headers = {
            "Crypto-Pay-API-Token": self.token,
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, params: dict) -> Any:
        """Единый метод для всех запросов к API CryptoBot."""
        url = f"{self.base_url}/{method}"
        logger.debug(f"🌐 POST {url} | params: {params}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                logger.debug(f"📥 Response: {data}")

                if not data.get("ok"):
                    err = data.get("error", {})
                    msg = err.get("message") or err.get("name") or str(err)
                    raise Exception(f"CryptoBot Error: {msg}")
                return data["result"]

    async def create_invoice(
        self,
        amount: float,
        asset: str = "USDT",
        description: str = "Оплата",
        payload: str = ""
    ) -> dict:
        """
        Создаёт инвойс в CryptoBot.
        Возвращает: dict с bot_invoice_url, invoice_id, payload и др.
        """
        return await self._request("createInvoice", {
            "asset": asset,
            "amount": str(amount),
            "description": description,
            "payload": payload,
            "accepted_assets": [asset],
            "expires_in": 3600
        })

    async def get_invoice_status(self, invoice_id: int) -> Optional[dict]:
        """
        Проверяет статус инвойса.
        Возвращает: dict со статусом или None, если не найден.
        """
        payload = {"invoice_ids": [int(invoice_id)]}
        result = await self._request("getInvoices", payload)
        
        # ✅ API может вернуть {"items": [...]} или [...]
        if isinstance(result, dict):
            items = result.get("items", [])
        elif isinstance(result, list):
            items = result
        else:
            items = []
        
        return items[0] if items else None