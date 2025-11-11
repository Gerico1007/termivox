"""
Context manager for Termivox - detects active application context.

Monitors the active window to provide context-aware shortcuts.
Enables different shortcut sets for different applications:
- Terminal: Shell-specific commands
- Browser: Web navigation shortcuts
- IDE/Editor: Code-specific shortcuts
- Default: General-purpose shortcuts

♠️ Nyro: Context awareness - adapt to the user's flow
🎸 JamAI: Different rhythms for different spaces
🌿 Aureon: The bridge knows where you are
"""

import subprocess
import threading
import time
from typing import Optional, Callable, List
from enum import Enum


class AppContext(Enum):
    """Application context types."""
    DEFAULT = "default"
    TERMINAL = "terminal"
    BROWSER = "browser"
    IDE = "ide"
    EDITOR = "editor"
    OFFICE = "office"


class ContextManager:
    """
    Manages application context detection for context-aware shortcuts.

    Monitors the active window and detects application type to enable
    context-specific shortcut sets.

    Example:
        manager = ContextManager()
        manager.register_callback(on_context_change)
        manager.start()

        # Later...
        current_context = manager.get_context()
    """

    # Mapping of window classes/names to contexts
    CONTEXT_MAPPING = {
        # Terminals
        "gnome-terminal": AppContext.TERMINAL,
        "konsole": AppContext.TERMINAL,
        "xterm": AppContext.TERMINAL,
        "alacritty": AppContext.TERMINAL,
        "kitty": AppContext.TERMINAL,
        "terminator": AppContext.TERMINAL,

        # Browsers
        "firefox": AppContext.BROWSER,
        "chrome": AppContext.BROWSER,
        "chromium": AppContext.BROWSER,
        "brave": AppContext.BROWSER,
        "opera": AppContext.BROWSER,
        "vivaldi": AppContext.BROWSER,

        # IDEs
        "code": AppContext.IDE,  # VS Code
        "pycharm": AppContext.IDE,
        "intellij": AppContext.IDE,
        "eclipse": AppContext.IDE,
        "netbeans": AppContext.IDE,

        # Editors
        "gedit": AppContext.EDITOR,
        "kate": AppContext.EDITOR,
        "sublime_text": AppContext.EDITOR,
        "atom": AppContext.EDITOR,
        "vim": AppContext.EDITOR,
        "emacs": AppContext.EDITOR,

        # Office
        "libreoffice": AppContext.OFFICE,
        "soffice": AppContext.OFFICE,
        "writer": AppContext.OFFICE,
        "calc": AppContext.OFFICE,
    }

    def __init__(self, poll_interval: float = 2.0):
        """
        Initialize context manager.

        Args:
            poll_interval: Seconds between context checks
        """
        self.poll_interval = poll_interval
        self._current_context = AppContext.DEFAULT
        self._callbacks: List[Callable[[AppContext], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def register_callback(self, callback: Callable[[AppContext], None]) -> None:
        """
        Register callback for context changes.

        Args:
            callback: Function called when context changes
                     Signature: callback(context: AppContext) -> None
        """
        with self._lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)
                # Immediately notify of current context
                callback(self._current_context)

    def unregister_callback(self, callback: Callable[[AppContext], None]) -> None:
        """
        Unregister context change callback.

        Args:
            callback: Previously registered callback
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def get_context(self) -> AppContext:
        """
        Get current application context.

        Returns:
            Current AppContext
        """
        with self._lock:
            return self._current_context

    def _detect_context(self) -> AppContext:
        """
        Detect context from active window.

        Uses xdotool on Linux to get active window information.

        Returns:
            Detected AppContext
        """
        try:
            # Get active window ID
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode != 0:
                return AppContext.DEFAULT

            window_id = result.stdout.strip()

            # Get window class
            result = subprocess.run(
                ['xdotool', 'getwindowclassname', window_id],
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode != 0:
                return AppContext.DEFAULT

            window_class = result.stdout.strip().lower()

            # Match against known contexts
            for app_name, context in self.CONTEXT_MAPPING.items():
                if app_name.lower() in window_class:
                    return context

            return AppContext.DEFAULT

        except subprocess.TimeoutExpired:
            return AppContext.DEFAULT
        except FileNotFoundError:
            # xdotool not available
            return AppContext.DEFAULT
        except Exception as e:
            print(f"[ContextManager] Detection error: {e}")
            return AppContext.DEFAULT

    def _monitor_loop(self) -> None:
        """
        Background monitoring loop.
        """
        while self._running:
            try:
                new_context = self._detect_context()

                with self._lock:
                    if new_context != self._current_context:
                        self._current_context = new_context
                        self._notify_callbacks(new_context)

            except Exception as e:
                print(f"[ContextManager] Monitor error: {e}")

            time.sleep(self.poll_interval)

    def _notify_callbacks(self, context: AppContext) -> None:
        """
        Notify all callbacks of context change.
        Called with lock held.

        Args:
            context: New context
        """
        for callback in self._callbacks:
            try:
                callback(context)
            except Exception as e:
                print(f"[ContextManager] Callback error: {e}")

    def start(self) -> None:
        """
        Start context monitoring in background thread.
        """
        if self._running:
            print("[ContextManager] Already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print("[ContextManager] Started")

    def stop(self) -> None:
        """
        Stop context monitoring.
        """
        if not self._running:
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

        print("[ContextManager] Stopped")

    def is_running(self) -> bool:
        """
        Check if context monitoring is active.

        Returns:
            True if running, False otherwise
        """
        return self._running
