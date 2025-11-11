"""
Global hotkey interface for Termivox toggle control.

Registers keyboard shortcuts for dual toggle control:
- Voice toggle (default: Ctrl+Alt+V)
- Shortcuts toggle (default: Ctrl+Alt+S)

♠️ Nyro: Dual keyboard listeners - two triggers, two rhythms
🎸 JamAI: Press the keys, flip the states - instant control
🌿 Aureon: Like dual guitar pedals - independent control
"""

from pynput import keyboard
from typing import Optional
import threading
from .dual_toggle_controller import DualToggleController


class HotkeyInterface:
    """
    Global hotkey listener for dual toggle control.

    Registers configurable keyboard combinations:
    - Voice toggle hotkey
    - Shortcuts toggle hotkey (if DualToggleController)

    Example:
        controller = DualToggleController(recognizer)
        hotkey = HotkeyInterface(
            controller,
            key_combo="ctrl+alt+v",
            shortcuts_key_combo="ctrl+alt+s"
        )
        hotkey.start()  # Begins listening in background
    """

    def __init__(
        self,
        controller,
        key_combo="ctrl+alt+v",
        shortcuts_key_combo=None
    ):
        """
        Initialize hotkey interface.

        Args:
            controller: ToggleController or DualToggleController instance
            key_combo: Voice toggle keyboard shortcut (e.g., "ctrl+alt+v")
            shortcuts_key_combo: Shortcuts toggle keyboard shortcut (e.g., "ctrl+alt+s")
        """
        self.controller = controller
        self.key_combo = key_combo
        self.shortcuts_key_combo = shortcuts_key_combo
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._running = False

        # Check if dual controller
        self.is_dual_controller = isinstance(controller, DualToggleController)

        # Parse key combinations
        self._hotkey_config = self._parse_hotkeys()

    def _parse_hotkeys(self) -> dict:
        """
        Parse all hotkey strings into pynput format.

        Returns:
            Dictionary mapping hotkeys to callbacks
        """
        config = {}

        # Voice toggle hotkey
        if self.key_combo:
            voice_hotkey = self._format_hotkey(self.key_combo)
            config[voice_hotkey] = self._on_voice_hotkey_press

        # Shortcuts toggle hotkey (if dual controller)
        if self.is_dual_controller and self.shortcuts_key_combo:
            shortcuts_hotkey = self._format_hotkey(self.shortcuts_key_combo)
            config[shortcuts_hotkey] = self._on_shortcuts_hotkey_press

        return config

    def _format_hotkey(self, key_combo: str) -> str:
        """
        Format hotkey string into pynput format.

        Args:
            key_combo: String like "ctrl+alt+v"

        Returns:
            Formatted hotkey string for pynput
        """
        # Convert common names to pynput format
        # Modifier keys (ctrl, alt, shift, cmd) need angle brackets
        # Regular keys (letters, numbers) do NOT use angle brackets
        modifiers = {'ctrl', 'alt', 'shift', 'cmd', 'win', 'super'}

        keys = key_combo.lower().replace(" ", "").split('+')
        formatted_keys = []
        for key in keys:
            if key in modifiers:
                formatted_keys.append(f'<{key}>')
            else:
                formatted_keys.append(key)

        return '+'.join(formatted_keys)

    def _on_voice_hotkey_press(self):
        """
        Called when voice toggle hotkey is pressed.
        """
        try:
            new_state = self.controller.toggle()
            print(f"[Hotkey] Voice toggled to: {new_state.value}")
        except Exception as e:
            print(f"[Hotkey] Error toggling voice: {e}")

    def _on_shortcuts_hotkey_press(self):
        """
        Called when shortcuts toggle hotkey is pressed.
        """
        if not self.is_dual_controller:
            return

        try:
            new_state = self.controller.toggle_shortcuts()
            print(f"[Hotkey] Shortcuts toggled to: {new_state.value}")
        except Exception as e:
            print(f"[Hotkey] Error toggling shortcuts: {e}")

    def start(self):
        """
        Start listening for hotkey presses.
        Runs in background thread.
        """
        if self._running:
            print("[Hotkey] Already running")
            return

        try:
            self._listener = keyboard.GlobalHotKeys(self._hotkey_config)
            self._listener.start()
            self._running = True

            # Print registered hotkeys
            print(f"[Hotkey] Voice toggle: {self.key_combo}")
            if self.is_dual_controller and self.shortcuts_key_combo:
                print(f"[Hotkey] Shortcuts toggle: {self.shortcuts_key_combo}")

        except Exception as e:
            print(f"[Hotkey] Failed to start: {e}")
            raise

    def stop(self):
        """
        Stop listening for hotkey presses.
        """
        if not self._running:
            return

        try:
            if self._listener:
                self._listener.stop()
                self._listener = None
            self._running = False
            print("[Hotkey] Stopped")
        except Exception as e:
            print(f"[Hotkey] Error stopping: {e}")

    def is_running(self) -> bool:
        """
        Check if hotkey listener is active.

        Returns:
            True if listening, False otherwise
        """
        return self._running
