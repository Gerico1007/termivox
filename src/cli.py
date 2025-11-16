"""
Termivox CLI - Command Line Interface

Handles all CLI commands:
- termivox              → Run normally
- termivox init         → First-time setup wizard
- termivox --ai         → Configure AI enhancement
- termivox --help       → Show help

♠️ Nyro: CLI orchestration - clean entry points
🎸 JamAI: User-friendly command flow
🌿 Aureon: Guiding users from installation to activation
"""

import sys
import argparse
import os
from pathlib import Path


def get_termivox_dir():
    """Get the Termivox directory (where .env should be stored)."""
    # Check if running from installed package or source
    if os.path.exists('config/settings.json'):
        # Running from source
        return Path.cwd()
    else:
        # Running from installed package - use user's home config dir
        config_dir = Path.home() / '.config' / 'termivox'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir


def show_welcome():
    """Show welcome banner."""
    print("=" * 60)
    print("🎤 Termivox - Voice Recognition Bridge")
    print("=" * 60)
    print()


def show_enhanced_help():
    """Show enhanced help with all available commands."""
    show_welcome()
    print("USAGE:")
    print("  termivox [OPTIONS] [COMMAND]")
    print()
    print("COMMANDS:")
    print("  init              First-time setup wizard")
    print("                    - Downloads voice models")
    print("                    - Configures AI (optional)")
    print("                    - Creates config files")
    print()
    print("OPTIONS:")
    print("  --lang LANG       Language code (en, fr)")
    print("  --config PATH     Path to config file (default: config/settings.json)")
    print("  --no-toggle       Disable toggle interfaces")
    print("  --ai              Configure AI enhancement")
    print("  --help, -h        Show this help message")
    print("  --version, -v     Show version")
    print()
    print("AI ENHANCEMENT:")
    print("  Enable AI-powered transcription refinement")
    print("  Providers: Gemini, OpenAI")
    print()
    print("  Setup:")
    print("    1. Run: termivox init")
    print("    2. Choose AI provider (optional)")
    print("    3. Add API key when prompted")
    print()
    print("  Manual setup:")
    print("    termivox --ai     → Configure AI interactively")
    print()
    print("EXAMPLES:")
    print("  termivox init              # First-time setup")
    print("  termivox                   # Run normally")
    print("  termivox --lang fr         # Use French")
    print("  termivox --ai              # Configure AI")
    print()
    print("DOCUMENTATION:")
    print("  https://github.com/Gerico1007/termivox#readme")
    print()


def main_cli():
    """
    Main CLI entry point.

    Handles command routing for:
    - init command
    - --ai flag
    - normal operation
    """
    # Check for init command first (before argparse)
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        from termivox.init_wizard import run_init_wizard
        sys.exit(run_init_wizard())

    # Check for --help or -h
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_enhanced_help()
        sys.exit(0)

    # Check for --version
    if len(sys.argv) > 1 and sys.argv[1] in ['--version', '-v', 'version']:
        print("Termivox version 0.1.3")
        sys.exit(0)

    # Check for --ai flag
    if '--ai' in sys.argv:
        from termivox.init_wizard import configure_ai
        sys.exit(configure_ai())

    # Normal operation - delegate to main.py
    from termivox.main import main
    main()


if __name__ == '__main__':
    main_cli()
