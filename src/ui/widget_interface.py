"""
Desktop widget interface for Termivox toggle control.

Displays a small always-on-top window with a large toggle button
and status indicator. Ideal for accessibility and visual clarity.

♠️ Nyro: Visible control surface - direct, tangible interaction
🎸 JamAI: Click the button, change the rhythm - visual and tactile
🌿 Aureon: A gentle presence on your desktop, always ready
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import threading
from .toggle_controller import ToggleState


class WidgetInterface:
    """
    Desktop widget for toggle control.

    Shows a floating window with toggle button and status label.
    Window stays on top and can be positioned anywhere on screen.

    Example:
        controller = ToggleController(recognizer)
        widget = WidgetInterface(controller, position=(100, 100))
        widget.start()  # Blocks until window closed
    """

    def __init__(
        self,
        controller,
        position=(100, 100),
        size=(200, 100),
        always_on_top=True
    ):
        """
        Initialize widget interface.

        Args:
            controller: ToggleController instance
            position: (x, y) window position
            size: (width, height) window size
            always_on_top: Keep window above other windows
        """
        self.controller = controller
        self.position = position
        self.size = size
        self.always_on_top = always_on_top

        self._root: Optional[tk.Tk] = None
        self._status_label: Optional[tk.Label] = None
        self._toggle_button: Optional[tk.Button] = None
        self._running = False

        # Register for state change notifications
        self.controller.register_interface(self._on_state_change)

    def _create_window(self):
        """
        Create and configure tkinter window.
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

        # Add a title bar manually since we removed decorations
        title_frame = tk.Frame(self._root, bg='#333333', cursor='fleur')
        title_frame.pack(fill='x', side='top')

        title_label = tk.Label(
            title_frame,
            text="Termivox",
            bg='#333333',
            fg='white',
            font=('Arial', 9),
            pady=2
        )
        title_label.pack(side='left', padx=5)

        # Make window draggable
        title_frame.bind('<Button-1>', self._start_drag)
        title_frame.bind('<B1-Motion>', self._on_drag)
        title_label.bind('<Button-1>', self._start_drag)
        title_label.bind('<B1-Motion>', self._on_drag)

        # Main content frame
        content_frame = tk.Frame(self._root)
        content_frame.pack(fill='both', expand=True)

        # Configure grid
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=2)

        # Status label
        self._status_label = tk.Label(
            content_frame,
            text="",
            font=("Arial", 14, "bold"),
            pady=10
        )
        self._status_label.grid(row=0, column=0, sticky="ew")

        # Toggle button
        self._toggle_button = tk.Button(
            content_frame,
            text="TOGGLE",
            command=self._on_button_click,
            font=("Arial", 16, "bold"),
            cursor="hand2",
            takefocus=0  # Never receive keyboard focus
        )
        self._toggle_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Set initial state
        self._update_ui(self.controller.get_state())

        # Handle window close (right-click to close since no decorations)
        self._root.bind('<Button-3>', lambda e: self._on_close())

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

    def _on_button_click(self):
        """
        Called when toggle button is clicked.

        With overrideredirect, this window can't steal focus,
        so cursor stays exactly where it was!
        """
        try:
            self.controller.toggle()
        except Exception as e:
            print(f"[Widget] Error toggling: {e}")

    def _on_state_change(self, state: ToggleState):
        """
        Called when controller state changes.
        Updates widget appearance.

        Args:
            state: New ToggleState
        """
        if self._root:
            # Schedule UI update on main thread
            self._root.after(0, lambda: self._update_ui(state))

    def _update_ui(self, state: ToggleState):
        """
        Update widget appearance based on state.

        Args:
            state: Current ToggleState
        """
        if not self._status_label or not self._toggle_button:
            return

        if state == ToggleState.ACTIVE:
            # Green theme for ACTIVE
            self._status_label.config(
                text="🎤 ACTIVE (Listening)",
                bg="#4CAF50",  # Material green
                fg="white"
            )
            self._toggle_button.config(
                bg="#66BB6A",
                activebackground="#81C784",
                fg="white"
            )
        else:
            # Red theme for PAUSED
            self._status_label.config(
                text="🔇 PAUSED (Muted)",
                bg="#F44336",  # Material red
                fg="white"
            )
            self._toggle_button.config(
                bg="#EF5350",
                activebackground="#E57373",
                fg="white"
            )

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
