"""
TinPyUI v1.7.0 — Internationalization (i18n) & Reactive RTL Engine
Provides dynamic translation hydration, reactive locale switching,
pluralization, currency/number formatting, and automatic Right-to-Left (RTL) layout mirroring.
"""

from typing import Dict, Any, Optional, Union, Callable
import datetime
from ..core.signals import Signal

RTL_LOCALES = {
    "ar", "ara",       # Arabic
    "he", "heb",       # Hebrew
    "fa", "fas", "per",# Persian / Farsi
    "ur", "urd",       # Urdu
    "ps", "pus",       # Pashto
    "syr",             # Syriac
    "yi", "yid",       # Yiddish
    "dv", "div",       # Divehi
}

class I18nEngine:
    """
    Reactive Internationalization & Localization engine for TinPyUI applications.
    """
    def __init__(self, default_locale: str = "en", fallback_locale: str = "en"):
        self.fallback_locale = fallback_locale
        self._locale_signal = Signal(default_locale)
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._listeners: list = []

    @property
    def current_locale(self) -> str:
        return self._locale_signal.value

    def get_locale(self) -> str:
        """Returns the currently active locale code (e.g. 'en', 'ar', 'fr')."""
        return self.current_locale

    def set_locale(self, locale: str) -> str:
        """
        Reactively switch active locale.
        Returns the text direction ('rtl' or 'ltr').
        """
        locale = locale.lower().strip()
        self._locale_signal.value = locale
        direction = self.get_direction(locale)
        for listener in self._listeners:
            try:
                listener(locale, direction)
            except Exception:
                pass
        return direction

    def is_rtl(self, locale: Optional[str] = None) -> bool:
        """Determines if the given or active locale requires Right-to-Left layout."""
        loc = (locale or self.current_locale).lower().split("-")[0].split("_")[0]
        return loc in RTL_LOCALES

    def get_direction(self, locale: Optional[str] = None) -> str:
        """Returns 'rtl' for Right-to-Left locales, or 'ltr' otherwise."""
        return "rtl" if self.is_rtl(locale) else "ltr"

    def on_locale_change(self, callback: Callable[[str, str], None]):
        """Register a hook called whenever the active locale changes."""
        self._listeners.append(callback)

    def load_translations(self, translations: Dict[str, Dict[str, Any]]):
        """
        Hydrates translations dictionary.
        Format:
        {
            "en": { "greeting": "Hello, {name}!", "items": {"one": "{count} item", "other": "{count} items"} },
            "ar": { "greeting": "مرحباً يا {name}!", "items": {"one": "عنصر واحد", "other": "{count} عناصر"} }
        }
        """
        for loc, dict_data in translations.items():
            loc = loc.lower().strip()
            if loc not in self._translations:
                self._translations[loc] = {}
            self._translations[loc].update(dict_data)

    def add_translation(self, locale: str, key: str, value: Any):
        """Register a single key-value translation for a locale."""
        loc = locale.lower().strip()
        if loc not in self._translations:
            self._translations[loc] = {}
        self._translations[loc][key] = value

    def t(self, key: str, default: Optional[str] = None, count: Optional[Union[int, float]] = None, **kwargs) -> str:
        """
        Translate a key with optional pluralization and variable interpolation.
        Example:
            t("welcome", name="Alice")
            t("cart.items", count=5)
        """
        loc = self.current_locale
        # Look up in current locale, then fallback
        val = self._lookup_key(loc, key)
        if val is None and loc != self.fallback_locale:
            val = self._lookup_key(self.fallback_locale, key)

        if val is None:
            val = default if default is not None else key

        # Pluralization resolution
        if count is not None:
            if isinstance(val, dict):
                plural_key = "zero" if count == 0 and "zero" in val else ("one" if count == 1 and "one" in val else "other")
                val = val.get(plural_key, val.get("other", str(val)))
            kwargs["count"] = count

        # Interpolation
        if isinstance(val, str) and kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return str(val)

    def _lookup_key(self, locale: str, key: str) -> Optional[Any]:
        loc_dict = self._translations.get(locale)
        if not loc_dict:
            return None
        if key in loc_dict:
            return loc_dict[key]
        # Nested dot-notation lookup (e.g. 'home.header.title')
        parts = key.split(".")
        curr = loc_dict
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return None
        return curr

    def format_number(self, value: Union[int, float], locale: Optional[str] = None) -> str:
        """Formats numbers with locale-aware thousand separators and decimals."""
        loc = (locale or self.current_locale).lower()
        if loc in {"de", "es", "fr", "it", "ru"}:
            formatted = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
            return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"

    def format_currency(self, amount: Union[int, float], currency: str = "USD", locale: Optional[str] = None) -> str:
        """Formats currency values with appropriate symbol and placement."""
        symbols = {
            "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "INR": "₹",
            "AED": "د.إ", "SAR": "ر.س", "CAD": "CA$", "AUD": "A$"
        }
        sym = symbols.get(currency.upper(), currency)
        formatted_num = self.format_number(amount, locale=locale)
        if self.is_rtl(locale):
            return f"{formatted_num} {sym}"
        if currency.upper() in {"EUR", "RUB"}:
            return f"{formatted_num} {sym}"
        return f"{sym}{formatted_num}"

    def format_date(self, date_val: Union[datetime.date, datetime.datetime, str], format_str: str = "%Y-%m-%d", locale: Optional[str] = None) -> str:
        """Formats a date object."""
        if isinstance(date_val, (datetime.date, datetime.datetime)):
            return date_val.strftime(format_str)
        return str(date_val)

# Global singleton engine
i18n = I18nEngine()
t = i18n.t
set_locale = i18n.set_locale
get_locale = i18n.get_locale
is_rtl = i18n.is_rtl
get_direction = i18n.get_direction
format_currency = i18n.format_currency
format_number = i18n.format_number
