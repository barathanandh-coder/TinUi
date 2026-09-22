"""
Unit tests for TinPyUI Internationalization (i18n) & Reactive RTL Engine
"""

import unittest
from tinpyui.utils.i18n import (
    I18nEngine, i18n, t, set_locale, get_locale,
    is_rtl, get_direction, format_currency, format_number
)

class TestI18nEngine(unittest.TestCase):

    def setUp(self):
        # Reset i18n instance
        i18n._translations = {}
        i18n.set_locale("en")

    def test_basic_translation_and_fallback(self):
        i18n.load_translations({
            "en": {"greeting": "Hello, {name}!", "welcome": "Welcome"},
            "fr": {"greeting": "Bonjour, {name}!"}
        })
        # Default is en
        self.assertEqual(t("greeting", name="Alice"), "Hello, Alice!")
        # French translation
        set_locale("fr")
        self.assertEqual(t("greeting", name="Bob"), "Bonjour, Bob!")
        # Fallback to English when key missing in French
        self.assertEqual(t("welcome"), "Welcome")
        # Missing key returns key itself
        self.assertEqual(t("non_existent_key"), "non_existent_key")

    def test_nested_dot_notation(self):
        i18n.load_translations({
            "en": {
                "nav": {
                    "header": {
                        "title": "Control Panel"
                    }
                }
            }
        })
        self.assertEqual(t("nav.header.title"), "Control Panel")

    def test_pluralization(self):
        i18n.load_translations({
            "en": {
                "items": {
                    "zero": "No items found",
                    "one": "1 item in your cart",
                    "other": "{count} items in your cart"
                }
            }
        })
        self.assertEqual(t("items", count=0), "No items found")
        self.assertEqual(t("items", count=1), "1 item in your cart")
        self.assertEqual(t("items", count=12), "12 items in your cart")

    def test_rtl_detection_and_direction(self):
        # LTR languages
        self.assertFalse(is_rtl("en"))
        self.assertFalse(is_rtl("fr"))
        self.assertFalse(is_rtl("es"))
        self.assertFalse(is_rtl("zh"))
        self.assertEqual(get_direction("en"), "ltr")

        # RTL languages
        self.assertTrue(is_rtl("ar"))
        self.assertTrue(is_rtl("he"))
        self.assertTrue(is_rtl("fa"))
        self.assertTrue(is_rtl("ur"))
        self.assertEqual(get_direction("ar"), "rtl")
        self.assertEqual(get_direction("he"), "rtl")

        # Dynamic locale setting triggers RTL
        dir_result = set_locale("ar")
        self.assertEqual(dir_result, "rtl")
        self.assertTrue(is_rtl())
        self.assertEqual(get_direction(), "rtl")

    def test_number_and_currency_formatting(self):
        set_locale("en")
        self.assertEqual(format_number(1234567.89), "1,234,567.89")
        self.assertEqual(format_currency(49.99, "USD"), "$49.99")
        self.assertEqual(format_currency(1000, "JPY"), "¥1,000")

        # RTL currency
        set_locale("ar")
        self.assertIn("د.إ", format_currency(150, "AED"))

    def test_locale_change_listener(self):
        events = []
        i18n.on_locale_change(lambda loc, d: events.append((loc, d)))
        set_locale("de")
        set_locale("ar")
        self.assertEqual(events, [("de", "ltr"), ("ar", "rtl")])

if __name__ == "__main__":
    unittest.main()
