import base64
import hashlib
import hmac
import json
import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.conf import settings

logger = logging.getLogger(__name__)

LIQPAY_CHECKOUT_URL = "https://www.liqpay.ua/api/3/checkout"
_AMOUNT_STEP = Decimal("0.01")
LIQPAY_SUCCESS_STATUSES = frozenset({"success", "sandbox"})
LIQPAY_PENDING_STATUSES = frozenset(
    {"processing", "wait_secure", "wait_accept", "wait_card", "prepared"}
)


def quantize_amount(value) -> Decimal:
    return Decimal(str(value)).quantize(_AMOUNT_STEP, rounding=ROUND_HALF_UP)


def amounts_match(expected: Decimal, raw) -> bool:
    try:
        return quantize_amount(expected) == quantize_amount(raw)
    except (InvalidOperation, TypeError, ValueError):
        return False


class LiqPayService:
    """LiqPay Acquiring API v3."""

    def __init__(self, public_key: str, private_key: str):
        self.public_key = public_key
        self.private_key = private_key

    def _encode(self, payload: dict) -> str:
        return base64.b64encode(
            json.dumps(payload, ensure_ascii=False).encode()
        ).decode()

    def _sign(self, data_b64: str) -> str:
        raw = (self.private_key + data_b64 + self.private_key).encode()
        return base64.b64encode(hashlib.sha1(raw).digest()).decode()

    def decode_data(self, data_b64: str) -> dict:
        try:
            parsed = json.loads(base64.b64decode(data_b64).decode())
        except Exception as exc:
            logger.error("LiqPay decode_data: %s", exc)
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def verify_callback(self, data_b64: str, signature: str) -> bool:
        expected = self._sign(data_b64)
        ok = hmac.compare_digest(expected, signature or "")
        if not ok:
            logger.warning("LiqPay signature mismatch")
        return ok

    def create_checkout_data(
        self,
        *,
        order_id: str,
        amount: Decimal | float | int | str,
        description: str,
        result_url: str,
        server_url: str,
        currency: str = "UAH",
    ) -> dict:
        payload = {
            "public_key": self.public_key,
            "version": "3",
            "action": "pay",
            "amount": str(quantize_amount(amount)),
            "currency": currency,
            "description": description,
            "order_id": order_id,
            "result_url": result_url,
            "server_url": server_url,
            "sandbox": 1 if getattr(settings, "LIQPAY_SANDBOX", False) else 0,
        }
        data_b64 = self._encode(payload)
        return {
            "data": data_b64,
            "signature": self._sign(data_b64),
            "checkout_url": LIQPAY_CHECKOUT_URL,
        }


def liqpay_configured() -> bool:
    return bool(settings.LIQPAY_PUBLIC_KEY and settings.LIQPAY_PRIVATE_KEY)


def get_liqpay_service() -> LiqPayService | None:
    if not liqpay_configured():
        return None
    return LiqPayService(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
