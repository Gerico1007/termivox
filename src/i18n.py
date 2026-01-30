"""Internationalization (i18n) module for Termivox UI strings.

Supports French (fr) and English (en) language modes.
"""

# Translation dictionary: {language_code: {key: translated_string}}
TRANSLATIONS = {
    "en": {
        "window_title": "TERMIVOX",
        "status_listening": "LISTENING",
        "status_muted": "MUTED",
        "tray_tooltip_active": "Termivox - ACTIVE (listening)",
        "tray_tooltip_paused": "Termivox - PAUSED (muted)",
        "tray_menu_toggle": "Toggle Voice Recognition",
        "tray_menu_exit": "Exit",
        "banner_title": "Termivox - Voice Recognition Bridge",
    },
    "fr": {
        "window_title": "TERMIVOX (FR)",
        "status_listening": "ÉCOUTE",
        "status_muted": "MUET",
        "tray_tooltip_active": "Termivox - ACTIF (écoute active)",
        "tray_tooltip_paused": "Termivox - PAUSE (muet)",
        "tray_menu_toggle": "Activer la reconnaissance vocale",
        "tray_menu_exit": "Quitter",
        "banner_title": "Termivox - Pont de Reconnaissance Vocale",
    },
}


def get_string(language: str, key: str, default: str = "") -> str:
    """Get translated string for the given language and key.

    Args:
        language: Language code ('en' or 'fr')
        key: Translation key
        default: Default string if translation not found

    Returns:
        Translated string or default value
    """
    lang = language.lower()
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]

    # Fallback to English if language not found
    if key in TRANSLATIONS["en"]:
        return TRANSLATIONS["en"][key]

    return default
