"""
Dual toggle controller for Termivox - independent voice and shortcut control.

Extends the base ToggleController with separate state management for:
- Voice recognition (ON/OFF)
- Shortcut display (VISIBLE/HIDDEN)

Enables selective activation modes:
- Voice only: Voice recognition active, shortcuts hidden
- Shortcuts only: Voice recognition paused, shortcuts visible
- Both: Full functionality with visual feedback
- Neither: Paused state

♠️ Nyro: Dual-state orchestration - voice and visuals independently controlled
🎸 JamAI: Two rhythms in harmony - speak or show, or both
🌿 Aureon: Flexibility in the bridge - choose your path
"""

import threading
from enum import Enum
from typing import Callable, List, Tuple
from .toggle_controller import ToggleController, ToggleState


class ShortcutDisplayState(Enum):
    """Shortcut display visibility state."""
    VISIBLE = "visible"
    HIDDEN = "hidden"


class ActivationMode(Enum):
    """Combined activation modes."""
    VOICE_ONLY = "voice_only"
    SHORTCUTS_ONLY = "shortcuts_only"
    BOTH_ACTIVE = "both_active"
    BOTH_INACTIVE = "both_inactive"


class DualToggleController(ToggleController):
    """
    Extended toggle controller with independent voice and shortcut control.

    Manages two independent states:
    1. Voice recognition (ACTIVE/PAUSED) - inherited from ToggleController
    2. Shortcut display (VISIBLE/HIDDEN) - new functionality

    Example:
        recognizer = Recognizer()
        controller = DualToggleController(recognizer)

        # Toggle voice recognition
        controller.toggle_voice()

        # Toggle shortcut display
        controller.toggle_shortcuts()

        # Get current mode
        mode = controller.get_activation_mode()
    """

    def __init__(self, recognizer):
        """
        Initialize dual toggle controller.

        Args:
            recognizer: Voice recognizer instance
        """
        super().__init__(recognizer)
        self._shortcuts_state = ShortcutDisplayState.VISIBLE  # Start visible
        self._shortcut_callbacks: List[Callable[[ShortcutDisplayState], None]] = []

    def register_shortcut_callback(
        self,
        callback: Callable[[ShortcutDisplayState], None]
    ) -> None:
        """
        Register callback for shortcut display state changes.

        Args:
            callback: Function called when shortcut state changes
                     Signature: callback(state: ShortcutDisplayState) -> None
        """
        with self._lock:
            if callback not in self._shortcut_callbacks:
                self._shortcut_callbacks.append(callback)
                # Notify new callback of current state
                callback(self._shortcuts_state)

    def unregister_shortcut_callback(
        self,
        callback: Callable[[ShortcutDisplayState], None]
    ) -> None:
        """
        Unregister shortcut display callback.

        Args:
            callback: Previously registered callback
        """
        with self._lock:
            if callback in self._shortcut_callbacks:
                self._shortcut_callbacks.remove(callback)

    def get_shortcuts_state(self) -> ShortcutDisplayState:
        """
        Get current shortcut display state.

        Returns:
            Current ShortcutDisplayState (VISIBLE or HIDDEN)
        """
        with self._lock:
            return self._shortcuts_state

    def is_shortcuts_visible(self) -> bool:
        """
        Check if shortcuts are currently visible.

        Returns:
            True if VISIBLE, False if HIDDEN
        """
        return self.get_shortcuts_state() == ShortcutDisplayState.VISIBLE

    def toggle_shortcuts(self) -> ShortcutDisplayState:
        """
        Toggle shortcut display visibility.

        Returns:
            New shortcut state after toggle
        """
        with self._lock:
            if self._shortcuts_state == ShortcutDisplayState.VISIBLE:
                return self._hide_shortcuts()
            else:
                return self._show_shortcuts()

    def show_shortcuts(self) -> ShortcutDisplayState:
        """
        Explicitly show shortcuts.

        Returns:
            New state (VISIBLE)
        """
        with self._lock:
            return self._show_shortcuts()

    def hide_shortcuts(self) -> ShortcutDisplayState:
        """
        Explicitly hide shortcuts.

        Returns:
            New state (HIDDEN)
        """
        with self._lock:
            return self._hide_shortcuts()

    def _show_shortcuts(self) -> ShortcutDisplayState:
        """
        Internal show implementation (must be called with lock held).

        Returns:
            New state (VISIBLE)
        """
        if self._shortcuts_state == ShortcutDisplayState.VISIBLE:
            return self._shortcuts_state  # Already visible

        self._shortcuts_state = ShortcutDisplayState.VISIBLE
        self._broadcast_shortcuts_change()
        return self._shortcuts_state

    def _hide_shortcuts(self) -> ShortcutDisplayState:
        """
        Internal hide implementation (must be called with lock held).

        Returns:
            New state (HIDDEN)
        """
        if self._shortcuts_state == ShortcutDisplayState.HIDDEN:
            return self._shortcuts_state  # Already hidden

        self._shortcuts_state = ShortcutDisplayState.HIDDEN
        self._broadcast_shortcuts_change()
        return self._shortcuts_state

    def _broadcast_shortcuts_change(self) -> None:
        """
        Notify all registered callbacks of shortcut state change.
        Called with lock held.
        """
        for callback in self._shortcut_callbacks:
            try:
                callback(self._shortcuts_state)
            except Exception as e:
                print(f"[DualToggleController] Shortcut callback error: {e}")

    def get_activation_mode(self) -> ActivationMode:
        """
        Get current combined activation mode.

        Returns:
            ActivationMode enum value
        """
        with self._lock:
            voice_active = self._state == ToggleState.ACTIVE
            shortcuts_visible = self._shortcuts_state == ShortcutDisplayState.VISIBLE

            if voice_active and shortcuts_visible:
                return ActivationMode.BOTH_ACTIVE
            elif voice_active and not shortcuts_visible:
                return ActivationMode.VOICE_ONLY
            elif not voice_active and shortcuts_visible:
                return ActivationMode.SHORTCUTS_ONLY
            else:
                return ActivationMode.BOTH_INACTIVE

    def get_states(self) -> Tuple[ToggleState, ShortcutDisplayState]:
        """
        Get both states at once.

        Returns:
            Tuple of (voice_state, shortcuts_state)
        """
        with self._lock:
            return (self._state, self._shortcuts_state)

    def set_mode(self, mode: ActivationMode) -> None:
        """
        Set activation mode directly.

        Args:
            mode: Desired ActivationMode
        """
        with self._lock:
            if mode == ActivationMode.BOTH_ACTIVE:
                if self._state != ToggleState.ACTIVE:
                    self._resume()
                if self._shortcuts_state != ShortcutDisplayState.VISIBLE:
                    self._show_shortcuts()

            elif mode == ActivationMode.VOICE_ONLY:
                if self._state != ToggleState.ACTIVE:
                    self._resume()
                if self._shortcuts_state != ShortcutDisplayState.HIDDEN:
                    self._hide_shortcuts()

            elif mode == ActivationMode.SHORTCUTS_ONLY:
                if self._state != ToggleState.PAUSED:
                    self._pause()
                if self._shortcuts_state != ShortcutDisplayState.VISIBLE:
                    self._show_shortcuts()

            elif mode == ActivationMode.BOTH_INACTIVE:
                if self._state != ToggleState.PAUSED:
                    self._pause()
                if self._shortcuts_state != ShortcutDisplayState.HIDDEN:
                    self._hide_shortcuts()

    def shutdown(self) -> None:
        """
        Clean shutdown - unregister all callbacks.
        """
        super().shutdown()
        with self._lock:
            self._shortcut_callbacks.clear()
