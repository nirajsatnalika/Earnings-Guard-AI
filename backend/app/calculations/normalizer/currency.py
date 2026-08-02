"""Currency detection — identifies currency symbols and codes in financial data.

Supports common currency symbols and ISO 4217 codes found in financial
statements from various regions.
"""

from __future__ import annotations

import re

# Currency symbol -> ISO code mapping
CURRENCY_SYMBOLS: dict[str, str] = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "₩": "KRW",
    "₽": "RUB",
    "₹": "INR",
    "R$": "BRL",
    "C$": "CAD",
    "A$": "AUD",
    "₺": "TRY",
    "₱": "PHP",
    "₨": "PKR",
    "₴": "UAH",
    "₸": "KZT",
    "₡": "CRC",
    "₦": "NGN",
    "₪": "ILS",
    "₫": "VND",
    "₭": "LAK",
    "₮": "MNT",
    "₲": "PYG",
    "₳": "ARA",
    "₶": "ITL",
    "₷": "SHP",
    "₾": "GEL",
    "₿": "BTC",
}

# ISO 4217 currency codes (common ones)
CURRENCY_CODES: set[str] = {
    "USD", "EUR", "GBP", "JPY", "INR", "KRW", "CNY", "RUB", "BRL", "CAD",
    "AUD", "NZD", "CHF", "SEK", "NOK", "DKK", "SGD", "HKD", "THB", "TRY",
    "ZAR", "MXN", "PHP", "PKR", "UAH", "KZT", "CRC", "NGN", "ILS", "VND",
    "LAK", "MNT", "PYG", "GEL", "AED", "SAR", "EGP", "COP", "CLP", "PEN",
    "MYR", "IDR", "TWD", "KZT", "BDT", "LKR", "NPR", "IRR", "IQD", "KWD",
    "BHD", "QAR", "OMR", "JOD", "LBP", "SYP", "AFN", "TZS", "KES", "UGX",
    "RWF", "GHS", "MAD", "DZD", "TND", "LYD", "SDG", "ETB", "AOA", "MZN",
}

_SYMBOL_PATTERN = re.compile(
    r"(\$|€|£|¥|₹|₩|₽|₺|₱|₨|₴|₸|₡|₦|₪|₫|₭|₮|₲|₳|₶|₷|₾|₿|R\$|C\$|A\$)"
)

_CODE_PATTERN = re.compile(r"\b(USD|EUR|GBP|JPY|INR|KRW|CNY|RUB|BRL|CAD|AUD|NZD|CHF|SEK|NOK|DKK|SGD|HKD|THB|TRY|ZAR|MXN|PHP|PKR|UAH|KZT|CRC|NGN|ILS|VND|LAK|MNT|PYG|GEL|AED|SAR|EGP|COP|CLP|PEN|MYR|IDR|TWD|BDT|LKR|NPR|IRR|IQD|KWD|BHD|QAR|OMR|JOD|LBP|SYR|AFN|TZS|KES|UGX|RWF|GHS|MAD|DZD|TND|LYD|SDG|ETB|AOA|MZN)\b")


def detect_currency(text: str) -> str | None:
    """Detect currency from a text string.

    Checks for ISO currency codes first (more specific), then falls back to
    currency symbols. Returns the ISO 4217 code or None.
    """
    if not text:
        return None

    code_match = _CODE_PATTERN.search(text.upper())
    if code_match:
        return code_match.group(1)

    symbol_match = _SYMBOL_PATTERN.search(text)
    if symbol_match:
        symbol = symbol_match.group(1)
        return CURRENCY_SYMBOLS.get(symbol)

    return None


def strip_currency_symbols(text: str) -> str:
    """Remove currency symbols and codes from a text string."""
    result = _SYMBOL_PATTERN.sub("", text)
    result = _CODE_PATTERN.sub("", result)
    return result.strip()
