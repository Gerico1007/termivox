"""
Shortcut icon system for Termivox.

Provides visual indicators for different types of shortcuts:
- Voice commands (🎤)
- Keyboard shortcuts (⌨️)
- Mouse actions (🖱️)
- Text formatting (📝)

♠️ Nyro: Visual language - icons speak louder than words
🎸 JamAI: Each icon tells a story - instant recognition
🌿 Aureon: Universal symbols bridging voice and action
"""

from typing import Dict


class ShortcutIcons:
    """
    Icon definitions for shortcut types.

    Each shortcut type has an associated emoji icon for visual clarity
    in the shortcut display panel.
    """

    # Icon mappings
    ICONS: Dict[str, str] = {
        "voice": "🎤",       # Voice commands (punctuation, editing)
        "keyboard": "⌨️",    # Keyboard shortcuts (copy, paste, undo)
        "mouse": "🖱️",       # Mouse actions (click, scroll)
        "text": "📝",        # Text formatting (new line, tab)
    }

    # Fallback icon
    DEFAULT_ICON = "●"

    @classmethod
    def get_icon(cls, icon_type: str) -> str:
        """
        Get icon for a given type.

        Args:
            icon_type: Icon type (voice, keyboard, mouse, text)

        Returns:
            Unicode emoji icon or default icon if type not found
        """
        return cls.ICONS.get(icon_type, cls.DEFAULT_ICON)

    @classmethod
    def get_all_icons(cls) -> Dict[str, str]:
        """
        Get all available icons.

        Returns:
            Dictionary of icon_type -> icon mappings
        """
        return cls.ICONS.copy()


class ShortcutEntry:
    """
    Represents a single shortcut with its metadata.

    Example:
        entry = ShortcutEntry(
            trigger="comma",
            action=",",
            icon_type="voice",
            description="Insert comma",
            enabled=True
        )
    """

    def __init__(
        self,
        trigger: str,
        action: str,
        icon_type: str,
        description: str = "",
        enabled: bool = True,
        category: str = "default"
    ):
        """
        Initialize shortcut entry.

        Args:
            trigger: Voice command that triggers this shortcut
            action: Action to perform (text, key combo, or special action)
            icon_type: Type of icon (voice, keyboard, mouse, text)
            description: Human-readable description
            enabled: Whether shortcut is active
            category: Category grouping (punctuation, editing, system, mouse)
        """
        self.trigger = trigger
        self.action = action
        self.icon_type = icon_type
        self.icon = ShortcutIcons.get_icon(icon_type)
        self.description = description
        self.enabled = enabled
        self.category = category

    def __repr__(self) -> str:
        return f"ShortcutEntry('{self.trigger}' -> '{self.action}', {self.icon})"

    def format_display(self, show_description: bool = True) -> str:
        """
        Format shortcut for display in UI.

        Args:
            show_description: Include description in output

        Returns:
            Formatted string like: "🎤 'comma' → ,"
        """
        base = f"{self.icon} '{self.trigger}' → {self.action}"
        if show_description and self.description:
            return f"{base}  # {self.description}"
        return base
