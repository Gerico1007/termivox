"""
Desktop widget interface for Termivox toggle control.

Enhanced widget with dual toggle (voice/shortcuts) and visual shortcut display.
Shows available voice commands with icons for easy reference.

♠️ Nyro: Enhanced control surface - voice and visuals unite
🎸 JamAI: Dual rhythm control - see and speak
🌿 Aureon: Your command center - always visible, always ready
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import threading
from .toggle_controller import ToggleState
from .dual_toggle_controller import DualToggleController, ShortcutDisplayState
from .shortcut_display import ShortcutDisplayPanel
from .context_manager import ContextManager, AppContext


class WidgetInterface:
    """
    Enhanced desktop widget with dual toggle and shortcut display.

    Shows a floating window with:
    - Dual toggle buttons (voice recognition and shortcut display)
    - Visual shortcut panel with icons
    - Context-aware shortcut display
    - Status indicators

    Example:
        controller = DualToggleController(recognizer)
        widget = WidgetInterface(
            controller,
            position=(100, 100),
            show_shortcuts=True
        )
        widget.start()  # Blocks until window closed
    """

    def __init__(
        self,
        controller,
        position=(100, 100),
        size=(420, 500),
        always_on_top=True,
        show_shortcuts=True,
        shortcuts_config="config/shortcuts_config.yaml"
    ):
        """
        Initialize enhanced widget interface.

        Args:
            controller: DualToggleController instance (or ToggleController for compatibility)
            position: (x, y) window position
            size: (width, height) window size
            always_on_top: Keep window above other windows
            show_shortcuts: Enable shortcut display panel
            shortcuts_config: Path to shortcuts YAML config
        """
        self.controller = controller
        self.position = position
        self.size = size
        self.always_on_top = always_on_top
        self.show_shortcuts = show_shortcuts
        self.shortcuts_config = shortcuts_config

        # Check if controller supports dual toggle
        self.is_dual_controller = isinstance(controller, DualToggleController)

        self._root: Optional[tk.Tk] = None
        self._status_label: Optional[tk.Label] = None
        self._voice_button: Optional[tk.Button] = None
        self._shortcuts_button: Optional[tk.Button] = None
        self._shortcut_panel: Optional[ShortcutDisplayPanel] = None
        self._context_manager: Optional[ContextManager] = None
        self._running = False

        # Register for state change notifications
        self.controller.register_interface(self._on_voice_state_change)

        # Register for shortcut state changes if dual controller
        if self.is_dual_controller:
            self.controller.register_shortcut_callback(self._on_shortcuts_state_change)

    def _create_window(self):
        """
        Create and configure enhanced tkinter window with dual toggle and shortcuts.
        """
        self._root = tk.Tk()

        # Remove window decorations and make it unfocusable
        # This prevents the widget from EVER stealing focus
        self._root.overrideredirect(True)

        self._root.geometry(f"{self.size[0]}x{self.size[1]}+{self.position[0]}+{self.position[1]}")

        if self.always_on_top:
            self._root.attributes('-topmost', True)

        # Make window stay on top and never grab keyboard focus
        try:
            self._root.attributes('-type', 'utility')
        except:
            pass

        # Minimal title bar
        title_frame = tk.Frame(self._root, bg='#1a1a1a', cursor='fleur', height=28)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="TERMIVOX v0.2",
            bg='#1a1a1a',
            fg='#888888',
            font=('Helvetica', 9, 'bold'),
            pady=4
        )
        title_label.pack(side='left', padx=10)

        # Close button (X)
        close_button = tk.Label(
            title_frame,
            text="✕",
            bg='#1a1a1a',
            fg='#666666',
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            padx=6
        )
        close_button.pack(side='right', padx=4)
        close_button.bind('<Button-1>', lambda e: self._on_close())
        close_button.bind('<Enter>', lambda e: close_button.config(fg='#ff6666'))
        close_button.bind('<Leave>', lambda e: close_button.config(fg='#666666'))

        # Make window draggable
        title_frame.bind('<Button-1>', self._start_drag)
        title_frame.bind('<B1-Motion>', self._on_drag)
        title_label.bind('<Button-1>', self._start_drag)
        title_label.bind('<B1-Motion>', self._on_drag)

        # Main content frame
        content_frame = tk.Frame(self._root, bg='#2a2a2a')
        content_frame.pack(fill='both', expand=True)

        # Control panel with dual toggle buttons
        control_panel = tk.Frame(content_frame, bg='#252525', height=100)
        control_panel.pack(fill='x', side='top', padx=4, pady=4)
        control_panel.pack_propagate(False)

        # Voice toggle button
        self._voice_button = tk.Button(
            control_panel,
            text="",
            command=self._on_voice_button_click,
            font=("Helvetica", 10, 'bold'),
            cursor='hand2',
            takefocus=0,
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            width=18
        )
        self._voice_button.pack(side='top', padx=4, pady=(6, 3), fill='x')

        # Shortcuts toggle button (if dual controller)
        if self.is_dual_controller and self.show_shortcuts:
            self._shortcuts_button = tk.Button(
                control_panel,
                text="",
                command=self._on_shortcuts_button_click,
                font=("Helvetica", 9, 'normal'),
                cursor='hand2',
                takefocus=0,
                relief='flat',
                borderwidth=0,
                highlightthickness=0,
                width=18
            )
            self._shortcuts_button.pack(side='top', padx=4, pady=(3, 6), fill='x')

        # Status indicator
        self._status_label = tk.Label(
            control_panel,
            text="● Ready",
            font=("Helvetica", 8),
            bg='#252525',
            fg='#888888'
        )
        self._status_label.pack(side='bottom', pady=2)

        # Shortcut display panel (if enabled)
        if self.show_shortcuts:
            shortcuts_frame = tk.Frame(content_frame, bg='#1e1e1e')
            shortcuts_frame.pack(fill='both', expand=True, padx=0, pady=0)

            self._shortcut_panel = ShortcutDisplayPanel(
                shortcuts_frame,
                config_path=self.shortcuts_config
            )
            self._shortcut_panel.render()

            # Start context manager for context-aware shortcuts
            if self.is_dual_controller:
                self._context_manager = ContextManager()
                self._context_manager.register_callback(self._on_context_change)
                self._context_manager.start()

        # Set initial states
        self._update_voice_ui(self.controller.get_state())
        if self.is_dual_controller:
            self._update_shortcuts_ui(self.controller.get_shortcuts_state())

        # Drag variables
        self._drag_x = 0
        self._drag_y = 0

    def _start_drag(self, event):
        """Start dragging the window."""
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        """Handle window dragging."""
        x = self._root.winfo_x() + event.x - self._drag_x
        y = self._root.winfo_y() + event.y - self._drag_y
        self._root.geometry(f"+{x}+{y}")

    def _on_voice_button_click(self):
        """
        Called when voice toggle button is clicked.
        """
        try:
            self.controller.toggle()
        except Exception as e:
            print(f"[Widget] Error toggling voice: {e}")

    def _on_shortcuts_button_click(self):
        """
        Called when shortcuts toggle button is clicked.
        """
        if not self.is_dual_controller:
            return

        try:
            self.controller.toggle_shortcuts()
        except Exception as e:
            print(f"[Widget] Error toggling shortcuts: {e}")

    def _on_voice_state_change(self, state: ToggleState):
        """
        Called when voice recognition state changes.

        Args:
            state: New ToggleState
        """
        if self._root:
            self._root.after(0, lambda: self._update_voice_ui(state))

    def _on_shortcuts_state_change(self, state: ShortcutDisplayState):
        """
        Called when shortcut display state changes.

        Args:
            state: New ShortcutDisplayState
        """
        if self._root:
            self._root.after(0, lambda: self._update_shortcuts_ui(state))

    def _on_context_change(self, context: AppContext):
        """
        Called when application context changes.

        Args:
            context: New AppContext
        """
        if self._shortcut_panel and self._root:
            self._root.after(0, lambda: self._shortcut_panel.update_context(context.value))

    def _update_voice_ui(self, state: ToggleState):
        """
        Update voice button appearance based on state.

        Args:
            state: Current ToggleState
        """
        if not self._voice_button:
            return

        if state == ToggleState.ACTIVE:
            self._voice_button.config(
                text="🎤 VOICE: ON",
                bg="#27ae60",
                activebackground="#2ecc71",
                fg="#ffffff"
            )
            if self._status_label:
                self._status_label.config(text="● Listening", fg="#27ae60")
        else:
            self._voice_button.config(
                text="🎤 VOICE: OFF",
                bg="#555555",
                activebackground="#666666",
                fg="#999999"
            )
            if self._status_label:
                self._status_label.config(text="● Muted", fg="#555555")

    def _update_shortcuts_ui(self, state: ShortcutDisplayState):
        """
        Update shortcuts button and panel visibility.

        Args:
            state: Current ShortcutDisplayState
        """
        if not self._shortcuts_button:
            return

        if state == ShortcutDisplayState.VISIBLE:
            self._shortcuts_button.config(
                text="📋 SHORTCUTS: ON",
                bg="#3498db",
                activebackground="#5dade2",
                fg="#ffffff"
            )
            if self._shortcut_panel:
                self._shortcut_panel.show()
        else:
            self._shortcuts_button.config(
                text="📋 SHORTCUTS: OFF",
                bg="#555555",
                activebackground="#666666",
                fg="#999999"
            )
            if self._shortcut_panel:
                self._shortcut_panel.hide()

    def _on_close(self):
        """
        Called when window close button clicked.
        """
        self.stop()

    def start(self):
        """
        Start widget window.
        Blocks until window is closed.
        """
        if self._running:
            print("[Widget] Already running")
            return

        self._running = True
        self._create_window()

        print(f"[Widget] Started at position {self.position}")

        # Run tkinter main loop (blocks)
        if self._root:
            self._root.mainloop()

    def start_async(self):
        """
        Start widget in background thread.
        Returns immediately.
        """
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()

    def stop(self):
        """
        Stop widget and close window.
        """
        if not self._running:
            return

        # Stop context manager
        if self._context_manager:
            self._context_manager.stop()
            self._context_manager = None

        # Destroy shortcut panel
        if self._shortcut_panel:
            self._shortcut_panel.destroy()
            self._shortcut_panel = None

        if self._root:
            self._root.quit()
            self._root.destroy()
            self._root = None

        self._running = False
        print("[Widget] Stopped")

    def is_running(self) -> bool:
        """
        Check if widget is active.

        Returns:
            True if running, False otherwise
        """
        return self._running
