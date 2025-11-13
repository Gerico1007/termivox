"""
Command Grammar for Termivox - Voice-to-Key Mapping

Interprets spoken commands as direct keyboard actions (Dragon-style).
When in Shortcut Mode, voice commands are parsed and executed as keystrokes.

Supported patterns:
- "Press <key>" → emit key event
- "Type <key>" → emit key event
- "Keypad <digit>" → emit numeric keypad event
- "Function <n>" → emit F1-F12 event
- "Shift <key>", "Control <key>", "Alt <key>" → emit combo keys
- "Control Alt <key>" → emit multi-modifier combos

♠️ Nyro: Structure anchor - grammar defines the syntax
🎸 JamAI: Rhythm of command - every word a keystroke
🌿 Aureon: Trust in the bridge - voice becomes action
"""

import re
from typing import Optional, Dict, List, Tuple
from pynput.keyboard import Controller, Key


class CommandGrammar:
    """
    Parses voice commands and emits corresponding keyboard events.

    Example:
        grammar = CommandGrammar()

        # Parse and execute commands
        grammar.parse("press tab")        # Emits Tab key
        grammar.parse("control alt delete")  # Emits Ctrl+Alt+Del
        grammar.parse("type escape")      # Emits Esc key
    """

    # Key name mappings
    KEY_MAPPINGS: Dict[str, Key] = {
        # Special keys
        "enter": Key.enter,
        "return": Key.enter,
        "tab": Key.tab,
        "space": Key.space,
        "spacebar": Key.space,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "escape": Key.esc,
        "esc": Key.esc,

        # Navigation
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "page up": Key.page_up,
        "page down": Key.page_down,
        "home": Key.home,
        "end": Key.end,

        # Modifiers
        "shift": Key.shift,
        "control": Key.ctrl,
        "ctrl": Key.ctrl,
        "alt": Key.alt,
        "option": Key.alt,
        "command": Key.cmd,
        "cmd": Key.cmd,
        "super": Key.cmd,
        "windows": Key.cmd,

        # Function keys
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,

        # Other
        "caps lock": Key.caps_lock,
        "insert": Key.insert,
        "print screen": Key.print_screen,
        "scroll lock": Key.scroll_lock,
        "pause": Key.pause,
        "menu": Key.menu,
    }

    # Command patterns
    PATTERNS = [
        # "Press <key>" or "Type <key>"
        (r"^(?:press|type)\s+(.+)$", "single_key"),

        # "Keypad <digit>"
        (r"^keypad\s+(\d)$", "numpad"),

        # "Function <n>" or "Type Function <n>"
        (r"^(?:type\s+)?function\s+(\d{1,2})$", "function_key"),

        # "Shift <key>", "Control <key>", "Alt <key>"
        (r"^(shift|control|ctrl|alt)\s+(.+)$", "modifier_key"),

        # "Control Alt <key>", "Control Shift <key>", etc.
        (r"^(control|ctrl)\s+(alt|shift)\s+(.+)$", "double_modifier"),

        # "Control Alt Shift <key>" (triple modifier)
        (r"^(control|ctrl)\s+(alt|shift)\s+(shift|alt)\s+(.+)$", "triple_modifier"),

        # Just a key name
        (r"^(.+)$", "bare_key"),
    ]

    def __init__(self):
        """Initialize command grammar."""
        self.keyboard = Controller()
        self._last_command = None

    def parse(self, utterance: str) -> bool:
        """
        Parse voice utterance and execute keyboard action.

        Args:
            utterance: Spoken command (e.g., "press tab")

        Returns:
            True if command was recognized and executed, False otherwise
        """
        if not utterance:
            return False

        # Normalize utterance
        utterance = utterance.lower().strip()

        # Try each pattern
        for pattern, action_type in self.PATTERNS:
            match = re.match(pattern, utterance, re.IGNORECASE)
            if match:
                return self._execute_action(action_type, match.groups())

        return False

    def _execute_action(self, action_type: str, groups: Tuple[str, ...]) -> bool:
        """
        Execute keyboard action based on matched pattern.

        Args:
            action_type: Type of action (single_key, modifier_key, etc.)
            groups: Regex match groups

        Returns:
            True if action was executed successfully
        """
        try:
            if action_type == "single_key":
                key_name = groups[0]
                return self._press_key(key_name)

            elif action_type == "numpad":
                digit = groups[0]
                return self._press_numpad(digit)

            elif action_type == "function_key":
                number = groups[0]
                return self._press_function_key(number)

            elif action_type == "modifier_key":
                modifier, key_name = groups
                return self._press_with_modifier(modifier, key_name)

            elif action_type == "double_modifier":
                mod1, mod2, key_name = groups
                return self._press_with_modifiers([mod1, mod2], key_name)

            elif action_type == "triple_modifier":
                mod1, mod2, mod3, key_name = groups
                return self._press_with_modifiers([mod1, mod2, mod3], key_name)

            elif action_type == "bare_key":
                key_name = groups[0]
                return self._press_key(key_name)

        except Exception as e:
            print(f"[CommandGrammar] Error executing {action_type}: {e}")
            return False

        return False

    def _press_key(self, key_name: str) -> bool:
        """
        Press a single key.

        Args:
            key_name: Name of key to press

        Returns:
            True if successful
        """
        key = self._resolve_key(key_name)
        if key is None:
            return False

        if isinstance(key, Key):
            self.keyboard.press(key)
            self.keyboard.release(key)
        else:
            self.keyboard.press(key)
            self.keyboard.release(key)

        print(f"[CommandGrammar] Pressed: {key_name}")
        self._last_command = f"press {key_name}"
        return True

    def _press_numpad(self, digit: str) -> bool:
        """
        Press numpad key.

        Args:
            digit: Digit 0-9

        Returns:
            True if successful
        """
        # Numpad keys are not directly available in pynput.keyboard.Key
        # We'll use the keyboard module's mapping or just press the digit
        # For now, just press the digit key
        self.keyboard.press(digit)
        self.keyboard.release(digit)

        print(f"[CommandGrammar] Pressed: Numpad {digit}")
        self._last_command = f"keypad {digit}"
        return True

    def _press_function_key(self, number: str) -> bool:
        """
        Press function key (F1-F12).

        Args:
            number: Function key number (1-12)

        Returns:
            True if successful
        """
        fn_num = int(number)
        if fn_num < 1 or fn_num > 12:
            return False

        key_name = f"f{fn_num}"
        key = self.KEY_MAPPINGS.get(key_name)
        if key is None:
            return False

        self.keyboard.press(key)
        self.keyboard.release(key)

        print(f"[CommandGrammar] Pressed: F{fn_num}")
        self._last_command = f"function {fn_num}"
        return True

    def _press_with_modifier(self, modifier: str, key_name: str) -> bool:
        """
        Press key with single modifier.

        Args:
            modifier: Modifier key (shift, control, alt)
            key_name: Key to press with modifier

        Returns:
            True if successful
        """
        mod_key = self._resolve_key(modifier)
        target_key = self._resolve_key(key_name)

        if mod_key is None or target_key is None:
            return False

        # Press modifier, press key, release key, release modifier
        self.keyboard.press(mod_key)
        if isinstance(target_key, Key):
            self.keyboard.press(target_key)
            self.keyboard.release(target_key)
        else:
            self.keyboard.press(target_key)
            self.keyboard.release(target_key)
        self.keyboard.release(mod_key)

        print(f"[CommandGrammar] Pressed: {modifier} + {key_name}")
        self._last_command = f"{modifier} {key_name}"
        return True

    def _press_with_modifiers(self, modifiers: List[str], key_name: str) -> bool:
        """
        Press key with multiple modifiers.

        Args:
            modifiers: List of modifier keys
            key_name: Key to press with modifiers

        Returns:
            True if successful
        """
        mod_keys = [self._resolve_key(m) for m in modifiers]
        target_key = self._resolve_key(key_name)

        if any(k is None for k in mod_keys) or target_key is None:
            return False

        # Press all modifiers
        for mod_key in mod_keys:
            self.keyboard.press(mod_key)

        # Press target key
        if isinstance(target_key, Key):
            self.keyboard.press(target_key)
            self.keyboard.release(target_key)
        else:
            self.keyboard.press(target_key)
            self.keyboard.release(target_key)

        # Release all modifiers (in reverse order)
        for mod_key in reversed(mod_keys):
            self.keyboard.release(mod_key)

        modifier_str = " + ".join(modifiers)
        print(f"[CommandGrammar] Pressed: {modifier_str} + {key_name}")
        self._last_command = f"{' '.join(modifiers)} {key_name}"
        return True

    def _resolve_key(self, key_name: str) -> Optional[Key]:
        """
        Resolve key name to Key object or character.

        Args:
            key_name: Name of key

        Returns:
            Key object or character, or None if not found
        """
        key_name = key_name.lower().strip()

        # Check special key mappings
        if key_name in self.KEY_MAPPINGS:
            return self.KEY_MAPPINGS[key_name]

        # Single character keys
        if len(key_name) == 1 and key_name.isalnum():
            return key_name

        # Try as literal character
        if len(key_name) == 1:
            return key_name

        print(f"[CommandGrammar] Unknown key: {key_name}")
        return None

    def get_last_command(self) -> Optional[str]:
        """
        Get the last executed command.

        Returns:
            Last command string or None
        """
        return self._last_command

    def is_command(self, utterance: str) -> bool:
        """
        Check if utterance matches a command pattern without executing.

        Args:
            utterance: Spoken text

        Returns:
            True if utterance matches a command pattern
        """
        utterance = utterance.lower().strip()

        for pattern, _ in self.PATTERNS[:-1]:  # Exclude bare_key pattern
            if re.match(pattern, utterance, re.IGNORECASE):
                return True

        return False
