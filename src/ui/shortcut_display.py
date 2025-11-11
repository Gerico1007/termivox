"""
Shortcut display panel for Termivox.

Renders visual shortcuts with icons, organized by category.
Supports real-time updates and context-aware display.

♠️ Nyro: Visual command center - see all your voice powers
🎸 JamAI: Dynamic display - adapts to your rhythm
🌿 Aureon: The guide - showing the way from voice to action
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, List, Optional
import yaml
import os
from .shortcut_icons import ShortcutEntry, ShortcutIcons


class ShortcutDisplayPanel:
    """
    Visual panel displaying available shortcuts with icons.

    Loads shortcuts from YAML config and renders them in a scrollable panel
    grouped by category with icons indicating shortcut type.

    Example:
        panel = ShortcutDisplayPanel(parent_frame, config_path)
        panel.render()
        panel.update_context("terminal")
    """

    def __init__(
        self,
        parent_frame: tk.Frame,
        config_path: str = "config/shortcuts_config.yaml"
    ):
        """
        Initialize shortcut display panel.

        Args:
            parent_frame: Parent tkinter frame to render into
            config_path: Path to shortcuts YAML config file
        """
        self.parent_frame = parent_frame
        self.config_path = config_path
        self.shortcuts: Dict[str, List[ShortcutEntry]] = {}
        self.current_context = "default"
        self.display_config = {}

        # UI elements
        self._container: Optional[tk.Frame] = None
        self._text_widget: Optional[tk.Text] = None
        self._scrollbar: Optional[tk.Scrollbar] = None

        # Load shortcuts from config
        self._load_shortcuts()

    def _load_shortcuts(self) -> None:
        """
        Load shortcuts from YAML configuration file.
        """
        try:
            # Handle relative paths from project root
            if not os.path.isabs(self.config_path):
                # Try to find project root by looking for pyproject.toml
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = current_dir
                while project_root != '/':
                    if os.path.exists(os.path.join(project_root, 'pyproject.toml')):
                        break
                    project_root = os.path.dirname(project_root)
                self.config_path = os.path.join(project_root, self.config_path)

            if not os.path.exists(self.config_path):
                print(f"[ShortcutDisplay] Config not found: {self.config_path}")
                self._load_default_shortcuts()
                return

            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Load display settings
            self.display_config = config.get('display', {})

            # Parse shortcuts by category
            shortcuts_data = config.get('shortcuts', {})
            for category, shortcuts_list in shortcuts_data.items():
                self.shortcuts[category] = []
                for shortcut_def in shortcuts_list:
                    entry = ShortcutEntry(
                        trigger=shortcut_def['trigger'],
                        action=shortcut_def['action'],
                        icon_type=shortcut_def['icon'],
                        description=shortcut_def.get('description', ''),
                        enabled=shortcut_def.get('enabled', True),
                        category=category
                    )
                    self.shortcuts[category].append(entry)

            print(f"[ShortcutDisplay] Loaded {sum(len(s) for s in self.shortcuts.values())} shortcuts")

        except Exception as e:
            print(f"[ShortcutDisplay] Error loading config: {e}")
            self._load_default_shortcuts()

    def _load_default_shortcuts(self) -> None:
        """
        Load minimal default shortcuts as fallback.
        """
        self.shortcuts = {
            "punctuation": [
                ShortcutEntry("comma", ",", "voice", "Insert comma"),
                ShortcutEntry("period", ".", "voice", "Insert period"),
            ],
            "editing": [
                ShortcutEntry("new line", "\\n", "text", "Insert new line"),
            ],
            "system": [
                ShortcutEntry("copy", "ctrl+c", "keyboard", "Copy selection"),
                ShortcutEntry("paste", "ctrl+v", "keyboard", "Paste clipboard"),
            ]
        }
        self.display_config = {
            "show_icons": True,
            "compact_mode": False,
            "show_descriptions": False,
            "group_by_category": True
        }

    def render(self) -> None:
        """
        Render the shortcut display panel.
        """
        # Create container frame
        self._container = tk.Frame(
            self.parent_frame,
            bg='#1e1e1e',
            relief='flat',
            borderwidth=0
        )
        self._container.pack(fill='both', expand=True, padx=0, pady=0)

        # Header
        header_frame = tk.Frame(self._container, bg='#252525', height=32)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="VOICE SHORTCUTS",
            bg='#252525',
            fg='#888888',
            font=('Helvetica', 9, 'bold'),
            pady=6
        )
        header_label.pack(side='left', padx=10)

        # Create text widget for shortcuts display
        text_frame = tk.Frame(self._container, bg='#1e1e1e')
        text_frame.pack(fill='both', expand=True)

        # Scrollbar
        self._scrollbar = tk.Scrollbar(text_frame, bg='#2a2a2a', troughcolor='#1e1e1e')
        self._scrollbar.pack(side='right', fill='y')

        # Text widget with custom styling
        self._text_widget = tk.Text(
            text_frame,
            bg='#1e1e1e',
            fg='#cccccc',
            font=('Consolas', 9),
            wrap='word',
            relief='flat',
            borderwidth=0,
            padx=12,
            pady=8,
            yscrollcommand=self._scrollbar.set,
            state='disabled',
            cursor='arrow',
            takefocus=0
        )
        self._text_widget.pack(side='left', fill='both', expand=True)

        self._scrollbar.config(command=self._text_widget.yview)

        # Configure text tags for styling
        self._text_widget.tag_config('category', foreground='#4a9eff', font=('Helvetica', 9, 'bold'))
        self._text_widget.tag_config('icon', foreground='#ffcc00')
        self._text_widget.tag_config('trigger', foreground='#88cc88')
        self._text_widget.tag_config('action', foreground='#ffffff', font=('Consolas', 9, 'bold'))
        self._text_widget.tag_config('arrow', foreground='#666666')
        self._text_widget.tag_config('description', foreground='#777777', font=('Helvetica', 8, 'italic'))

        # Populate with shortcuts
        self._populate_shortcuts()

    def _populate_shortcuts(self) -> None:
        """
        Populate text widget with formatted shortcuts.
        """
        if not self._text_widget:
            return

        self._text_widget.config(state='normal')
        self._text_widget.delete('1.0', 'end')

        group_by_category = self.display_config.get('group_by_category', True)
        show_descriptions = self.display_config.get('show_descriptions', False)

        if group_by_category:
            for category, shortcuts in self.shortcuts.items():
                if not shortcuts:
                    continue

                # Category header
                category_title = category.upper().replace('_', ' ')
                self._text_widget.insert('end', f'\n{category_title}\n', 'category')

                # Shortcuts in category
                for shortcut in shortcuts:
                    if not shortcut.enabled:
                        continue

                    # Icon
                    self._text_widget.insert('end', f'  {shortcut.icon} ', 'icon')

                    # Trigger
                    self._text_widget.insert('end', f'"{shortcut.trigger}"', 'trigger')

                    # Arrow
                    self._text_widget.insert('end', ' → ', 'arrow')

                    # Action
                    action_display = shortcut.action.replace('\n', '↵').replace('\t', '⇥')
                    self._text_widget.insert('end', action_display, 'action')

                    # Description (optional)
                    if show_descriptions and shortcut.description:
                        self._text_widget.insert('end', f'\n     {shortcut.description}', 'description')

                    self._text_widget.insert('end', '\n')
        else:
            # Flat list
            all_shortcuts = []
            for shortcuts_list in self.shortcuts.values():
                all_shortcuts.extend(shortcuts_list)

            for shortcut in all_shortcuts:
                if not shortcut.enabled:
                    continue

                self._text_widget.insert('end', f'{shortcut.icon} ', 'icon')
                self._text_widget.insert('end', f'"{shortcut.trigger}"', 'trigger')
                self._text_widget.insert('end', ' → ', 'arrow')
                action_display = shortcut.action.replace('\n', '↵').replace('\t', '⇥')
                self._text_widget.insert('end', action_display, 'action')

                if show_descriptions and shortcut.description:
                    self._text_widget.insert('end', f' # {shortcut.description}', 'description')

                self._text_widget.insert('end', '\n')

        self._text_widget.config(state='disabled')

    def update_context(self, context: str = "default") -> None:
        """
        Update displayed shortcuts based on context.

        Args:
            context: Context name (default, terminal, browser, etc.)
        """
        self.current_context = context
        # For now, just refresh the display
        # Future: Load context-specific shortcuts
        if self._text_widget:
            self._populate_shortcuts()

    def show(self) -> None:
        """Show the shortcut panel."""
        if self._container:
            self._container.pack(fill='both', expand=True)

    def hide(self) -> None:
        """Hide the shortcut panel."""
        if self._container:
            self._container.pack_forget()

    def destroy(self) -> None:
        """Clean up the panel."""
        if self._container:
            self._container.destroy()
            self._container = None
            self._text_widget = None
            self._scrollbar = None
