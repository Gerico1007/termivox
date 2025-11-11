"""
Desktop widget interface for Termivox toggle control.

Compact widget with mode selector and expandable shortcuts panel.
Shows a small floating window with:
- Main toggle button (voice status)
- Mode selector (3 scenarios)
- Expandable shortcuts reference panel

♠️ Nyro: Compact control surface - small but powerful
🎸 JamAI: Choose your rhythm - three modes, one interface
🌿 Aureon: Minimal presence, maximum control
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
    Compact desktop widget with mode selector and expandable shortcuts.

    Modes:
    1. Voice + Shortcuts: Full functionality
    2. Voice Only: Voice active, shortcuts hidden
    3. Shortcuts Only: Voice off, shortcuts visible as reference

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
        Initialize compact widget interface.

        Args:
            controller: DualToggleController instance
            position: (x, y) window position
            size: (width, height) base window size (expandable)
            always_on_top: Keep window above other windows
            show_shortcuts: Enable shortcuts panel feature
            shortcuts_config: Path to shortcuts YAML config
        """
        self.controller = controller
        self.position = position
        self.base_size = size  # Compact size
        self.expanded_size = (380, 420)  # Expanded with shortcuts
        self.always_on_top = always_on_top
        self.show_shortcuts = show_shortcuts
        self.shortcuts_config = shortcuts_config

        # Check if controller supports dual toggle
        self.is_dual_controller = isinstance(controller, DualToggleController)

        # UI state
        self._shortcuts_expanded = False
        self._current_mode = ActivationMode.BOTH_ACTIVE

        # UI elements
        self._root: Optional[tk.Tk] = None
        self._status_label: Optional[tk.Label] = None
        self._toggle_button: Optional[tk.Button] = None
        self._mode_buttons = []
        self._expand_button: Optional[tk.Label] = None
        self._shortcut_panel: Optional[ShortcutDisplayPanel] = None
        self._shortcuts_frame: Optional[tk.Frame] = None
        self._context_manager: Optional[ContextManager] = None
        self._running = False

        # Register for state change notifications
        self.controller.register_interface(self._on_voice_state_change)

        # Register for shortcut state changes if dual controller
        if self.is_dual_controller:
            self.controller.register_shortcut_callback(self._on_shortcuts_state_change)

    def _create_window(self):
        """
        Create compact window with mode selector and expandable shortcuts.
        """
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

        # Toggle button (compact)
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
        self._toggle_button.pack(fill='both', expand=True, padx=2, pady=2)

        # Bottom bar with mode selector and expand button
        bottom_bar = tk.Frame(content_frame, bg='#1e1e1e', height=26)
        bottom_bar.pack(fill='x', side='bottom')
        bottom_bar.pack_propagate(False)

        # Mode selector (3 icon buttons)
        mode_frame = tk.Frame(bottom_bar, bg='#1e1e1e')
        mode_frame.pack(side='left', padx=4)

        # Mode 1: Voice + Shortcuts
        mode1_btn = tk.Label(
            mode_frame,
            text="🎤📋",
            bg='#1e1e1e',
            fg='#4a9eff',
            font=('Helvetica', 9),
            cursor='hand2',
            padx=3
        )
        mode1_btn.pack(side='left', padx=1)
        mode1_btn.bind('<Button-1>', lambda e: self._set_mode(ActivationMode.BOTH_ACTIVE))
        mode1_btn.bind('<Enter>', lambda e: mode1_btn.config(bg='#2a2a2a'))
        mode1_btn.bind('<Leave>', lambda e: mode1_btn.config(bg='#1e1e1e'))
        self._mode_buttons.append(mode1_btn)

        # Mode 2: Voice Only
        mode2_btn = tk.Label(
            mode_frame,
            text="🎤",
            bg='#1e1e1e',
            fg='#888888',
            font=('Helvetica', 11),
            cursor='hand2',
            padx=3
        )
        mode2_btn.pack(side='left', padx=1)
        mode2_btn.bind('<Button-1>', lambda e: self._set_mode(ActivationMode.VOICE_ONLY))
        mode2_btn.bind('<Enter>', lambda e: mode2_btn.config(bg='#2a2a2a'))
        mode2_btn.bind('<Leave>', lambda e: mode2_btn.config(bg='#1e1e1e'))
        self._mode_buttons.append(mode2_btn)

        # Mode 3: Shortcuts Only
        mode3_btn = tk.Label(
            mode_frame,
            text="📋",
            bg='#1e1e1e',
            fg='#888888',
            font=('Helvetica', 11),
            cursor='hand2',
            padx=3
        )
        mode3_btn.pack(side='left', padx=1)
        mode3_btn.bind('<Button-1>', lambda e: self._set_mode(ActivationMode.SHORTCUTS_ONLY))
        mode3_btn.bind('<Enter>', lambda e: mode3_btn.config(bg='#2a2a2a'))
        mode3_btn.bind('<Leave>', lambda e: mode3_btn.config(bg='#1e1e1e'))
        self._mode_buttons.append(mode3_btn)

        # Expand/Collapse button for shortcuts
        if self.show_shortcuts:
            self._expand_button = tk.Label(
                bottom_bar,
                text="◀",
                bg='#1e1e1e',
                fg='#888888',
                font=('Helvetica', 10),
                cursor='hand2',
                padx=4
            )
            self._expand_button.pack(side='right', padx=4)
            self._expand_button.bind('<Button-1>', lambda e: self._toggle_shortcuts_panel())
            self._expand_button.bind('<Enter>', lambda e: self._expand_button.config(fg='#4a9eff'))
            self._expand_button.bind('<Leave>', lambda e: self._expand_button.config(fg='#888888'))

        # Shortcuts panel (initially hidden, slides out to the right)
        if self.show_shortcuts:
            self._shortcuts_frame = tk.Frame(self._root, bg='#1e1e1e', width=200)
            # Don't pack yet - will be shown on expand

        # Set initial state
        self._update_ui(self.controller.get_state())
        self._update_mode_indicators()

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
        """Main toggle button clicked - behavior depends on current mode."""
        if not self.is_dual_controller:
            # Simple toggle
            self.controller.toggle()
            return

        current_mode = self.controller.get_activation_mode()

        if current_mode == ActivationMode.BOTH_ACTIVE:
            # Pause voice
            self.controller.pause()
        elif current_mode == ActivationMode.VOICE_ONLY:
            # Pause voice
            self.controller.pause()
        elif current_mode == ActivationMode.SHORTCUTS_ONLY:
            # Activate voice
            self.controller.resume()
        else:  # BOTH_INACTIVE
            # Resume voice
            self.controller.resume()

    def _set_mode(self, mode: ActivationMode):
        """Set activation mode."""
        if not self.is_dual_controller:
            return

        self._current_mode = mode
        self.controller.set_mode(mode)
        self._update_mode_indicators()

        # Auto-expand shortcuts if shortcuts-only mode
        if mode == ActivationMode.SHORTCUTS_ONLY and not self._shortcuts_expanded:
            self._toggle_shortcuts_panel()
        elif mode == ActivationMode.VOICE_ONLY and self._shortcuts_expanded:
            self._toggle_shortcuts_panel()

    def _update_mode_indicators(self):
        """Update mode button highlights."""
        if not self._mode_buttons:
            return

        modes = [
            ActivationMode.BOTH_ACTIVE,
            ActivationMode.VOICE_ONLY,
            ActivationMode.SHORTCUTS_ONLY
        ]

        for i, btn in enumerate(self._mode_buttons):
            if self._current_mode == modes[i]:
                btn.config(fg='#4a9eff')  # Highlight active mode
            else:
                btn.config(fg='#888888')  # Dim inactive modes

    def _toggle_shortcuts_panel(self):
        """Toggle shortcuts panel visibility (expand/collapse)."""
        if not self._shortcuts_frame:
            return

        self._shortcuts_expanded = not self._shortcuts_expanded

        if self._shortcuts_expanded:
            # Expand window and show shortcuts
            new_width = self.expanded_size[0]
            new_height = self.expanded_size[1]
            self._root.geometry(f"{new_width}x{new_height}")

            # Show shortcuts panel
            self._shortcuts_frame.pack(side='right', fill='both', expand=True)

            # Create shortcut panel if not exists
            if not self._shortcut_panel:
                self._shortcut_panel = ShortcutDisplayPanel(
                    self._shortcuts_frame,
                    config_path=self.shortcuts_config
                )
                self._shortcut_panel.render()

                # Start context manager
                if self.is_dual_controller:
                    self._context_manager = ContextManager()
                    self._context_manager.register_callback(self._on_context_change)
                    self._context_manager.start()

            # Update expand button
            if self._expand_button:
                self._expand_button.config(text="▶")

        else:
            # Collapse window
            self._root.geometry(f"{self.base_size[0]}x{self.base_size[1]}")

            # Hide shortcuts panel
            self._shortcuts_frame.pack_forget()

            # Update expand button
            if self._expand_button:
                self._expand_button.config(text="◀")

    def _on_voice_state_change(self, state: ToggleState):
        """Called when voice recognition state changes."""
        if self._root:
            self._root.after(0, lambda: self._update_ui(state))

    def _on_shortcuts_state_change(self, state: ShortcutDisplayState):
        """Called when shortcut display state changes."""
        if self._root:
            self._root.after(0, lambda: self._update_mode_indicators())

    def _on_context_change(self, context: AppContext):
        """Called when application context changes."""
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
                text="MUTED",
                bg="#555555",
                activebackground="#666666",
                fg="#999999"
            )

    def _on_close(self):
        """Called when window close button clicked."""
        self.stop()

    def start(self):
        """Start widget window. Blocks until window is closed."""
        if self._running:
            print("[Widget] Already running")
            return

        self._running = True
        self._create_window()

        print(f"[Widget] Compact mode started at {self.position}")

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
        """Check if widget is active."""
        return self._running
