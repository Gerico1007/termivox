"""
Termivox Initialization Wizard

Interactive setup for first-time users:
- Downloads voice models
- Configures AI enhancement
- Creates .env file
- Sets up config

♠️ Nyro: Setup flow orchestration
🎸 JamAI: Smooth onboarding experience
🌿 Aureon: Guiding new users to voice freedom
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional


def get_termivox_home():
    """Get the Termivox home directory."""
    # Check if running from source
    if os.path.exists('config/settings.json'):
        return Path.cwd()
    else:
        # Use user's config directory
        config_dir = Path.home() / '.config' / 'termivox'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir


def show_banner():
    """Show welcome banner."""
    print("\n" + "=" * 60)
    print("🎤 Termivox - First-Time Setup Wizard")
    print("=" * 60)
    print()


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no question."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{question} [{default_str}]: ").strip().lower()
        if response == '':
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")


def prompt_choice(question: str, choices: list, default: int = 0) -> str:
    """Prompt user for choice from list."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, 1):
        marker = "→" if i == default + 1 else " "
        print(f"  {marker} {i}. {choice}")

    while True:
        response = input(f"\nChoice [1-{len(choices)}] (default: {default + 1}): ").strip()
        if response == '':
            return choices[default]
        try:
            choice_idx = int(response) - 1
            if 0 <= choice_idx < len(choices):
                return choices[choice_idx]
        except ValueError:
            pass
        print(f"Please enter a number between 1 and {len(choices)}")


def check_dependencies():
    """Check if required system dependencies are installed."""
    print("\n📦 Checking dependencies...")

    issues = []

    # Check for xdotool
    if os.system('which xdotool > /dev/null 2>&1') != 0:
        issues.append("xdotool not found. Install: sudo apt install xdotool")

    # Check for pyaudio dependencies
    if os.system('pkg-config --exists portaudio-2.0 > /dev/null 2>&1') != 0:
        issues.append("PortAudio not found. Install: sudo apt install portaudio19-dev")

    if issues:
        print("\n⚠️  Missing dependencies:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        if not prompt_yes_no("Continue anyway?", default=False):
            return False
    else:
        print("✓ All dependencies found")

    return True


def download_voice_model(lang: str = 'en'):
    """Download Vosk voice model."""
    print(f"\n📥 Downloading voice model ({lang})...")
    print("This may take a few minutes...")

    try:
        from termivox.download_model import main as download_main
        # Call download model
        sys.argv = ['download_model', '--lang', lang]
        download_main()
        print("✓ Voice model downloaded successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to download model: {e}")
        print("You can download it manually later with: termivox-download-model")
        return False


def setup_ai_enhancement() -> Optional[dict]:
    """
    Interactive AI setup.

    Returns:
        dict with ai_provider and api_key, or None to skip
    """
    print("\n🤖 AI Enhancement Setup")
    print()
    print("AI enhancement refines your voice transcription:")
    print("  • Corrects grammar naturally")
    print("  • Handles bilingual input (French/English)")
    print("  • Removes filler words")
    print("  • Processes voice commands")
    print()

    if not prompt_yes_no("Enable AI enhancement?", default=False):
        return None

    # Choose provider
    provider = prompt_choice(
        "Choose AI provider:",
        ["Google Gemini (recommended, free tier available)",
         "OpenAI GPT (requires paid account)",
         "Skip for now"],
        default=0
    )

    if "Skip" in provider:
        return None

    # Map choice to provider name
    if "Gemini" in provider:
        provider_name = "gemini"
        api_key_name = "GEMINI_API_KEY"
        api_url = "https://makersuite.google.com/app/apikey"
    else:
        provider_name = "openai"
        api_key_name = "OPENAI_API_KEY"
        api_url = "https://platform.openai.com/api-keys"

    print(f"\n📝 {provider_name.upper()} API Key")
    print(f"Get your API key at: {api_url}")
    print()

    api_key = input(f"Enter your {provider_name.upper()} API key (or press Enter to skip): ").strip()

    if not api_key:
        print("⚠️  No API key provided. AI enhancement will be disabled.")
        print(f"You can add it later by running: termivox --ai")
        return None

    return {
        'provider': provider_name,
        'api_key': api_key,
        'api_key_name': api_key_name
    }


def create_env_file(termivox_home: Path, ai_config: Optional[dict] = None):
    """Create .env file with API keys."""
    env_file = termivox_home / '.env'

    env_content = """# Termivox AI Enhancement Configuration
# This file is auto-generated by 'termivox init'

"""

    if ai_config:
        env_content += f"# {ai_config['provider'].upper()} API Key\n"
        env_content += f"{ai_config['api_key_name']}={ai_config['api_key']}\n\n"
    else:
        env_content += """# Google Gemini API Key
# Get your key at: https://makersuite.google.com/app/apikey
# GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Key
# Get your key at: https://platform.openai.com/api-keys
# OPENAI_API_KEY=your_openai_api_key_here
"""

    with open(env_file, 'w') as f:
        f.write(env_content)

    print(f"✓ Created .env file: {env_file}")


def create_config_file(termivox_home: Path, lang: str, ai_enabled: bool, ai_provider: str = 'gemini'):
    """Create or update config file."""
    config_dir = termivox_home / 'config'
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / 'settings.json'

    # Default config
    config = {
        "interfaces": {
            "hotkey": {
                "enabled": True,
                "key": "ctrl+alt+v"
            },
            "tray": {
                "enabled": False
            },
            "widget": {
                "enabled": True,
                "position": {"x": 100, "y": 100},
                "size": {"width": 160, "height": 70},
                "always_on_top": True
            },
            "hardware": {
                "enabled": False,
                "device": None,
                "device_type": "usb"
            }
        },
        "voice": {
            "language": lang,
            "auto_space": True
        },
        "ai": {
            "enabled": ai_enabled,
            "provider": ai_provider,
            "model": None,
            "buffer_mode": "sentence",
            "buffer_size": 50
        },
        "audio_feedback": False
    }

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Created config file: {config_file}")


def run_init_wizard():
    """Run the complete initialization wizard."""
    show_banner()

    print("Welcome to Termivox!")
    print("This wizard will help you set up voice recognition on your system.")
    print()

    # Get Termivox home
    termivox_home = get_termivox_home()
    print(f"📁 Termivox directory: {termivox_home}")

    # Check dependencies
    if not check_dependencies():
        return 1

    # Choose language
    lang = prompt_choice(
        "\n🌍 Choose voice recognition language:",
        ["English (en)", "French (fr)"],
        default=0
    )
    lang_code = 'en' if 'English' in lang else 'fr'

    # Download voice model
    if prompt_yes_no(f"\nDownload {lang} voice model?", default=True):
        download_voice_model(lang_code)

    # AI setup
    ai_config = setup_ai_enhancement()

    # Create .env file
    print("\n📝 Creating configuration files...")
    create_env_file(termivox_home, ai_config)

    # Create config file
    create_config_file(
        termivox_home,
        lang_code,
        ai_enabled=ai_config is not None,
        ai_provider=ai_config['provider'] if ai_config else 'gemini'
    )

    # Final summary
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run: termivox")
    print("  2. Press Ctrl+Alt+V to toggle voice recognition")
    print("  3. Speak naturally - your words will be typed!")
    print()

    if ai_config:
        print(f"🤖 AI Enhancement: {ai_config['provider'].upper()} (enabled)")
    else:
        print("💡 Tip: Enable AI later with: termivox --ai")

    print()
    print("For help: termivox --help")
    print("Documentation: https://github.com/Gerico1007/termivox")
    print()

    return 0


def configure_ai():
    """Configure AI enhancement interactively."""
    show_banner()
    print("🤖 AI Enhancement Configuration\n")

    termivox_home = get_termivox_home()
    env_file = termivox_home / '.env'

    # Run AI setup
    ai_config = setup_ai_enhancement()

    if ai_config is None:
        print("\n⚠️  AI enhancement not configured.")
        return 0

    # Update or create .env
    if env_file.exists():
        # Read existing .env
        with open(env_file, 'r') as f:
            env_lines = f.readlines()

        # Update or add API key
        key_found = False
        new_lines = []
        for line in env_lines:
            if line.startswith(ai_config['api_key_name']):
                new_lines.append(f"{ai_config['api_key_name']}={ai_config['api_key']}\n")
                key_found = True
            else:
                new_lines.append(line)

        if not key_found:
            new_lines.append(f"\n# {ai_config['provider'].upper()} API Key\n")
            new_lines.append(f"{ai_config['api_key_name']}={ai_config['api_key']}\n")

        with open(env_file, 'w') as f:
            f.writelines(new_lines)

        print(f"\n✓ Updated .env file: {env_file}")
    else:
        create_env_file(termivox_home, ai_config)

    # Update config file
    config_file = termivox_home / 'config' / 'settings.json'
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)

        config['ai']['enabled'] = True
        config['ai']['provider'] = ai_config['provider']

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✓ Updated config file: {config_file}")

    print(f"\n✅ AI Enhancement configured: {ai_config['provider'].upper()}")
    print("\nRun 'termivox' to start using AI-enhanced voice recognition!")

    return 0


if __name__ == '__main__':
    sys.exit(run_init_wizard())
