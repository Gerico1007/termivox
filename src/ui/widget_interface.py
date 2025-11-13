"""
Desktop widget interface for Termivox toggle control.

Compact 3-button design:
- Voice Toggle (LISTENING/OFF)
- Expand Arrow (show/hide shortcuts)
- Mode Selector (Vocal/Shortcut)

♠️ Nyro: Three buttons, infinite control
🎸 JamAI: Simple interface, powerful modes
🌿 Aureon: Clarity through simplicity
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import threading
from .toggle_controller import ToggleState
from .dual_toggle_controller import DualToggleController, ShortcutDisplayState, ActivationMode
from .shortcut_display import ShortcutDisplayPanel
from .context_manager import ContextManager, AppContext


class WidgetInterface:
    """
    Compact 3-button widget for Termivox control.

    Layout (180x90):
    ┌──────────────────────────────┐
    │ TERMIVOX              ✕     │
    ├──────────────────────────────┤
    │       LISTENING              │ ← Voice toggle
    ├──────────────────────────────┤
    │ 🎛️ VOCAL          ◀         │ ← Mode + Expand
    └──────────────────────────────┘

    Modes:
    - VOCAL: Listens to all speech (normal mode)
    - SHORTCUT: Only recognizes shortcut commands

    Example:
        controller = DualToggleController(recognizer)
        widget = WidgetInterface(controller, position=(100, 100))
        widget.start()
    """

    def __init__(
        self,
        controller,
        position=(100, 100),
        size=(180, 90),
        always_on_top=True,
        show_shortcuts=True,
        shortcuts_config="config/shortcuts_config.yaml"
    ):
        """
        Initialize compact 3-button widget.

        Args:
            controller: DualToggleController instance
            position: (x, y) window position
            size: (width, height) base window size
            always_on_top: Keep window above other windows
            show_shortcuts: Enable shortcuts panel
            shortcuts_config: Path to shortcuts YAML config
        """
        self.controller = controller
        self.position = position
        self.base_size = size
        self.expanded_size = (380, 420)
        self.always_on_top = always_on_top
        self.show_shortcuts = show_shortcuts
        self.shortcuts_config = shortcuts_config

        # Check if controller supports dual toggle
        self.is_dual_controller = isinstance(controller, DualToggleController)

        # UI state
        self._shortcuts_expanded = False
        self._shortcut_mode = False  # False = Vocal, True = Shortcut-only

        # UI elements
        self._root: Optional[tk.Tk] = None
        self._toggle_button: Optional[tk.Button] = None
        self._mode_button: Optional[tk.Label] = None
        self._expand_button: Optional[tk.Label] = None
        self._shortcut_panel: Optional[ShortcutDisplayPanel] = None
        self._shortcuts_frame: Optional[tk.Frame] = None
        self._context_manager: Optional[ContextManager] = None
        self._running = False

        # Register for state change notifications
        self.controller.register_interface(self._on_voice_state_change)

        if self.is_dual_controller:
            self.controller.register_shortcut_callback(self._on_shortcuts_state_change)

    def _create_window(self):
        """Create compact 3-button window."""
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.geometry(f"{self.base_size[0]}x{self.base_size[1]}+{self.position[0]}+{self.position[1]}")

        if self.always_on_top:
            self._root.attributes('-topmost', True)

        try:
            self._root.attributes('-type', 'utility')
        except:
            pass

        # Title bar (compact)
        title_frame = tk.Frame(self._root, bg='#1a1a1a', cursor='fleur', height=22)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="TERMIVOX",
            bg='#1a1a1a',
            fg='#888888',
            font=('Helvetica', 8, 'bold'),
            pady=2
        )
        title_label.pack(side='left', padx=6)

        # Close button
        close_button = tk.Label(
            title_frame,
            text="✕",
            bg='#1a1a1a',
            fg='#666666',
            font=('Helvetica', 9, 'bold'),
            cursor='hand2',
            padx=4
        )
        close_button.pack(side='right', padx=2)
        close_button.bind('<Button-1>', lambda e: self._on_close())
        close_button.bind('<Enter>', lambda e: close_button.config(fg='#ff6666'))
        close_button.bind('<Leave>', lambda e: close_button.config(fg='#666666'))

        # Make draggable
        title_frame.bind('<Button-1>', self._start_drag)
        title_frame.bind('<B1-Motion>', self._on_drag)
        title_label.bind('<Button-1>', self._start_drag)
        title_label.bind('<B1-Motion>', self._on_drag)

        # Main content frame
        content_frame = tk.Frame(self._root, bg='#2a2a2a')
        content_frame.pack(fill='both', expand=True)

        # Button 1: Voice Toggle (main, large)
        self._toggle_button = tk.Button(
            content_frame,
            text="",
            command=self._on_toggle_click,
            font=("Helvetica", 10, 'bold'),
            cursor='hand2',
            takefocus=0,
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self._toggle_button.pack(fill='both', expand=True, padx=2, pady=(2, 1))

        # Bottom bar with mode selector and expand button
        bottom_bar = tk.Frame(content_frame, bg='#1e1e1e', height=26)
        bottom_bar.pack(fill='x', side='bottom')
        bottom_bar.pack_propagate(False)

        # Button 2: Mode Selector (left)
        self._mode_button = tk.Label(
            bottom_bar,
            text="🎛️ VOCAL",
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Helvetica', 9, 'bold'),
            cursor='hand2',
            padx=8
        )
        self._mode_button.pack(side='left', padx=4, pady=2)
        self._mode_button.bind('<Button-1>', lambda e: self._toggle_mode())
        self._mode_button.bind('<Enter>', lambda e: self._mode_button.config(bg='#2a2a2a'))
        self._mode_button.bind('<Leave>', lambda e: self._mode_button.config(bg='#1e1e1e'))

        # Button 3: Expand Arrow (right)
        if self.show_shortcuts:
            self._expand_button = tk.Label(
                bottom_bar,
                text="◀",
                bg='#1e1e1e',
                fg='#888888',
                font=('Helvetica', 12, 'bold'),
                cursor='hand2',
                padx=8
            )
            self._expand_button.pack(side='right', padx=4, pady=2)
            self._expand_button.bind('<Button-1>', lambda e: self._toggle_shortcuts_panel())
            self._expand_button.bind('<Enter>', lambda e: self._expand_button.config(fg='#4a9eff'))
            self._expand_button.bind('<Leave>', lambda e: self._expand_button.config(fg='#888888'))

        # Shortcuts panel frame (expandable)
        if self.show_shortcuts:
            self._shortcuts_frame = tk.Frame(self._root, bg='#1e1e1e', width=200)

        # Set initial state
        self._update_ui(self.controller.get_state())
        self._update_mode_indicator()

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

    def _on_toggle_click(self):
        """Button 1: Toggle voice on/off."""
        if self.controller.is_active():
            self.controller.pause()
        else:
            self.controller.resume()

    def _toggle_mode(self):
        """Button 2: Toggle between Vocal and Shortcut modes."""
        self._shortcut_mode = not self._shortcut_mode
        self._update_mode_indicator()

        if not self.is_dual_controller:
            return

        # Enable/disable grammar mode in recognizer
        recognizer = self.controller.recognizer
        if hasattr(recognizer, 'enable_grammar_mode'):
            if self._shortcut_mode:
                # Shortcut Mode: Enable grammar for voice-to-key mapping
                recognizer.enable_grammar_mode()

                # Auto-expand shortcuts panel for reference
                if not self._shortcuts_expanded:
                    self._toggle_shortcuts_panel()
            else:
                # Vocal Mode: Disable grammar, return to normal dictation
                recognizer.disable_grammar_mode()

                # Auto-collapse shortcuts if expanded
                if self._shortcuts_expanded:
                    self._toggle_shortcuts_panel()

    def _update_mode_indicator(self):
        """Update mode button appearance."""
        if not self._mode_button:
            return

        if self._shortcut_mode:
            # Shortcut Mode: Blue highlight
            self._mode_button.config(
                text="🎛️ SHORTCUT",
                fg='#4a9eff',
                font=('Helvetica', 8, 'bold')
            )
        else:
            # Vocal Mode: White/default
            self._mode_button.config(
                text="🎛️ VOCAL",
                fg='#ffffff',
                font=('Helvetica', 9, 'bold')
            )

    def _toggle_shortcuts_panel(self):
        """Button 3: Toggle shortcuts panel visibility."""
        if not self._shortcuts_frame:
            return

        self._shortcuts_expanded = not self._shortcuts_expanded

        if self._shortcuts_expanded:
            # Expand window
            self._root.geometry(f"{self.expanded_size[0]}x{self.expanded_size[1]}")
            self._shortcuts_frame.pack(side='right', fill='both', expand=True)

            # Create panel if needed
            if not self._shortcut_panel:
                self._shortcut_panel = ShortcutDisplayPanel(
                    self._shortcuts_frame,
                    config_path=self.shortcuts_config
                )
                self._shortcut_panel.render()

                if self.is_dual_controller:
                    self._context_manager = ContextManager()
                    self._context_manager.register_callback(self._on_context_change)
                    self._context_manager.start()

            # Update arrow
            if self._expand_button:
                self._expand_button.config(text="▶")

        else:
            # Collapse window
            self._root.geometry(f"{self.base_size[0]}x{self.base_size[1]}")
            self._shortcuts_frame.pack_forget()

            # Update arrow
            if self._expand_button:
                self._expand_button.config(text="◀")

    def _on_voice_state_change(self, state: ToggleState):
        """Called when voice state changes."""
        if self._root:
            self._root.after(0, lambda: self._update_ui(state))

    def _on_shortcuts_state_change(self, state: ShortcutDisplayState):
        """Called when shortcuts state changes."""
        pass  # Not used in 3-button design

    def _on_context_change(self, context: AppContext):
        """Called when app context changes."""
        if self._shortcut_panel and self._root:
            self._root.after(0, lambda: self._shortcut_panel.update_context(context.value))

    def _update_ui(self, state: ToggleState):
        """Update main toggle button appearance."""
        if not self._toggle_button:
            return

        if state == ToggleState.ACTIVE:
            self._toggle_button.config(
                text="LISTENING",
                bg="#27ae60",
                activebackground="#2ecc71",
                fg="#ffffff"
            )
        else:
            self._toggle_button.config(
                text="OFF",
                bg="#555555",
                activebackground="#666666",
                fg="#999999"
            )

    def _on_close(self):
        """Close button clicked."""
        self.stop()

    def start(self):
        """Start widget window."""
        if self._running:
            print("[Widget] Already running")
            return

        self._running = True
        self._create_window()

        print(f"[Widget] 3-button compact mode started at {self.position}")

        if self._root:
            self._root.mainloop()

    def start_async(self):
        """Start widget in background thread."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()

    def stop(self):
        """Stop widget and close window."""
        if not self._running:
            return

        if self._context_manager:
            self._context_manager.stop()
            self._context_manager = None

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
        """Check if widget is active."""
        return self._running
