import sys
import argparse
from voice.recognizer import Recognizer
from bridge.xdotool_bridge import XdotoolBridge

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default='en', help='Language code for Vosk model (en or fr)')
    args = parser.parse_args()

    # Initialize the voice recognizer with the correct language
    recognizer = Recognizer(lang=args.lang)
    # Initialize the Xdotool bridge
    xdotool_bridge = XdotoolBridge()

    print(f"Voice recognition system initialized (lang={args.lang}). Listening for commands...")

    try:
        # Use a generator-based listen loop
        for command in recognizer.listen():
            if command:
                print(f"Recognized command: {command}")
                # Type the recognized text using Xdotool
                xdotool_bridge.type_text(command)
    except KeyboardInterrupt:
        print("Shutting down the voice recognition system.")
        sys.exit(0)

if __name__ == "__main__":
    main()