import vosk
import pyaudio
import json
from pathlib import Path
from typing import Optional
from termivox.ai.ai_service import create_ai_service, AIService

##**Mia + Miette + JeremyAI Activate!**

##🧠 **Mia's Neural Circuit**: The `recognizer.py` file will encapsulate the `Recognizer` class, which is pivotal for managing voice recognition through the Vosk library. This class will need methods for initializing the microphone, processing audio streams, and converting spoken words into text. The structure will follow object-oriented principles, ensuring clarity and maintainability.

##🌸 **Miette's Sparkle Echo**: Imagine a voice that listens, interprets, and transforms sound into meaning! The `Recognizer` class will be like a bridge between the spoken word and the digital realm, capturing whispers of intent and translating them into actions. Each method will be a step in a dance, gracefully moving from sound to understanding.

##🎵 **JeremyAI's Melodic Encoding**: Picture a symphony where each note represents a voice command, resonating through the air and landing softly on the digital canvas. The `Recognizer` will orchestrate this melody, capturing the essence of speech and converting it into a harmonious flow of text.

## 🔄 **Trinity Response to recognizer.py**

class Recognizer:
    def __init__(self, lang="en", auto_space=True, ai_service: Optional[AIService] = None,
                 ai_buffer_mode="sentence", ai_buffer_size=50):
        self.lang = lang  # Store the language for use in listen()
        self.auto_space = auto_space  # Option to add space after each yielded text
        self._paused = False  # Toggle control: when True, voice recognition is muted

        # AI enhancement settings
        self.ai_service = ai_service  # AIService instance for text refinement
        self.ai_buffer_mode = ai_buffer_mode  # "realtime", "sentence", or "paragraph"
        self.ai_buffer_size = ai_buffer_size  # Max characters before forcing AI refinement
        self._ai_buffer = []  # Buffer for accumulating text before AI refinement
        self._ai_buffer_chars = 0  # Character count in buffer

        # Find the model using search paths
        model_path = self._find_model(lang)
        if not model_path:
            raise FileNotFoundError(
                f"Vosk model for '{lang}' not found!\n"
                f"Please run: termivox-download-model --lang {lang}"
            )

        self.model = vosk.Model(str(model_path))
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        self.stream.start_stream()

    def _find_model(self, lang):
        """Search for voice model in multiple locations.

        Search order:
        1. User's home directory: ~/.termivox/models/
        2. Current working directory: ./voice_models/
        3. Package directory: <package>/voice_models/

        Args:
            lang: Language code (en or fr)

        Returns:
            Path to model directory or None if not found
        """
        model_names = {
            "en": "vosk-model-small-en-us-0.15",
            "fr": "vosk-model-small-fr-0.22"
        }

        model_name = model_names.get(lang)
        if not model_name:
            return None

        search_paths = [
            # User's home directory
            Path.home() / ".termivox" / "models" / model_name,
            # Current working directory
            Path.cwd() / "voice_models" / model_name,
            # Package directory
            Path(__file__).parent.parent.parent / "voice_models" / model_name,
        ]

        for path in search_paths:
            if path.exists() and path.is_dir():
                return path

        return None

    def listen(self, trigger_word_start=None, trigger_word_end=None, stop_on_keyboard_interrupt=True):
        # Listen to microphone and yield transcribed text with voice editing, punctuation, and system command support
        import subprocess
        import threading
        import sys
        stop_flag = {'stop': False}

        def keyboard_listener():
            try:
                import termios, tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setcbreak(fd)
                    while True:
                        ch = sys.stdin.read(1)
                        if ch == '\x03' or ch == '\x04' or ch == 'q':  # Ctrl+C, Ctrl+D, or 'q'
                            stop_flag['stop'] = True
                            break
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

        if stop_on_keyboard_interrupt:
            t = threading.Thread(target=keyboard_listener, daemon=True)
            t.start()

        # English and French punctuation and edit command mappings
        punctuation_map_en = {
            "period": ".",
            "comma": ",",
            "question mark": "?",
            "exclamation mark": "!",
            "exclamation": "!",
            "colon": ":",
            "semicolon": ";",
            "dash": "-",
            "hyphen": "-",
            "quote": '"',
            "quotation": '"',
            "apostrophe": "'",
        }
        edit_map_en = {
            "new paragraph": "\n\n",
            "next paragraph": "\n\n",
            "new line": "\n",
            "next line": "\n",
            "tab": "\t",
        }
        system_command_map_en = {
            "select all": ["xdotool", "key", "ctrl+a"],
            "copy": ["xdotool", "key", "ctrl+c"],
            "paste": ["xdotool", "key", "ctrl+v"],
            "cut": ["xdotool", "key", "ctrl+x"],
            "undo": ["xdotool", "key", "ctrl+z"],
            "click": ["xdotool", "click", "1"],
            "double click": ["xdotool", "click", "--repeat", "2", "1"],
            "right click": ["xdotool", "click", "3"],
            "scroll up": ["xdotool", "click", "4"],
            "scroll down": ["xdotool", "click", "5"],
        }
        punctuation_map_fr = {
            "point": ".",
            "virgule": ",",
            "point d'interrogation": "?",
            "point d exclamation": "!",
            "exclamation": "!",
            "deux points": ":",
            "point virgule": ";",
            "tiret": "-",
            "trait d'union": "-",
            "guillemet": '"',
            "guillemets": '"',
            "apostrophe": "'",
        }
        edit_map_fr = {
            "nouveau paragraphe": "\n\n",
            "paragraphe suivant": "\n\n",
            "nouvelle ligne": "\n",
            "ligne suivante": "\n",
            "tabulation": "\t",
            "tab": "\t",
        }
        system_command_map_fr = {
            "tout sélectionner": ["xdotool", "key", "ctrl+a"],
            "copier": ["xdotool", "key", "ctrl+c"],
            "coller": ["xdotool", "key", "ctrl+v"],
            "couper": ["xdotool", "key", "ctrl+x"],
            "annuler": ["xdotool", "key", "ctrl+z"],
            "cliquer": ["xdotool", "click", "1"],
            "double clic": ["xdotool", "click", "--repeat", "2", "1"],
            "clic droit": ["xdotool", "click", "3"],
            "défiler vers le haut": ["xdotool", "click", "4"],
            "défiler vers le bas": ["xdotool", "click", "5"],
        }
        # Choose mapping based on language
        lang = getattr(self, 'lang', 'en')
        if lang == 'fr':
            punctuation_map = punctuation_map_fr
            edit_map = edit_map_fr
            system_command_map = system_command_map_fr
        else:
            punctuation_map = punctuation_map_en
            edit_map = edit_map_en
            system_command_map = system_command_map_en
        listening = trigger_word_start is None  # If no trigger, always listen
        while True:
            if stop_flag['stop']:
                break
            data = self.stream.read(4000, exception_on_overflow=False)

            # Skip processing if paused (toggle control)
            if self._paused:
                continue

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "")
                if not text:
                    continue
                lowered = text.lower().strip()
                # Handle trigger to start recognition
                if trigger_word_start and not listening:
                    if lowered == trigger_word_start.lower():
                        listening = True
                        continue
                # Handle trigger to end recognition
                if trigger_word_end and listening:
                    if lowered == trigger_word_end.lower():
                        break
                if not listening:
                    continue
                # System command trigger
                if lowered in system_command_map:
                    subprocess.run(system_command_map[lowered])
                    continue
                # Check for edit commands
                if lowered in edit_map:
                    yield edit_map[lowered]
                    continue
                # Replace spoken punctuation inline (preserve spacing)
                words = lowered.split()
                transformed = []
                i = 0
                while i < len(words):
                    matched = False
                    for n in (3, 2, 1):
                        if i + n - 1 < len(words):
                            phrase = " ".join(words[i:i+n])
                            if phrase in punctuation_map:
                                transformed.append(punctuation_map[phrase])
                                i += n
                                matched = True
                                break
                    if not matched:
                        transformed.append(words[i])
                        i += 1
                final_text = " ".join(transformed)
                # Only add space if not a single punctuation or edit command
                if self.auto_space and final_text not in punctuation_map.values() and final_text not in edit_map.values():
                    final_text += " "

                # AI enhancement mode: buffer and refine
                if self.ai_service:
                    self._add_to_ai_buffer(final_text)

                    # Check if we should flush the buffer
                    if self._should_flush_ai_buffer(final_text):
                        refined_text = self._flush_ai_buffer()
                        if refined_text:
                            # Add space after AI-refined text if auto_space is enabled
                            if self.auto_space and not refined_text.endswith(" "):
                                refined_text += " "
                            yield refined_text
                else:
                    # No AI: yield text immediately (original behavior)
                    yield final_text

    def pause(self):
        """
        Pause voice recognition (mute).
        Audio stream continues running but no processing occurs.
        """
        self._paused = True

    def resume(self):
        """
        Resume voice recognition (unmute).
        Audio processing resumes immediately.
        """
        self._paused = False

    def is_paused(self):
        """
        Check if voice recognition is currently paused.

        Returns:
            True if paused, False if active
        """
        return self._paused

    def _should_flush_ai_buffer(self, new_text: str) -> bool:
        """
        Determine if AI buffer should be flushed based on buffer mode.

        Args:
            new_text: Text just added to buffer

        Returns:
            True if buffer should be sent to AI, False otherwise
        """
        if not self.ai_service:
            return False

        # Realtime mode: flush immediately
        if self.ai_buffer_mode == "realtime":
            return True

        # Sentence mode: flush on sentence-ending punctuation
        if self.ai_buffer_mode == "sentence":
            sentence_enders = ['.', '!', '?', '。', '！', '？']
            if any(new_text.strip().endswith(ender) for ender in sentence_enders):
                return True

        # Paragraph mode: flush on paragraph breaks
        if self.ai_buffer_mode == "paragraph":
            if '\n\n' in new_text:
                return True

        # Size-based flushing: buffer too large
        if self._ai_buffer_chars >= self.ai_buffer_size:
            return True

        return False

    def _flush_ai_buffer(self):
        """
        Send buffered text to AI for refinement and return result.

        Returns:
            Refined text from AI, or buffered text if AI fails
        """
        if not self._ai_buffer:
            return ""

        # Combine buffer into single text
        raw_text = "".join(self._ai_buffer)

        # Clear buffer
        self._ai_buffer.clear()
        self._ai_buffer_chars = 0

        # Refine through AI if available
        if self.ai_service:
            try:
                print(f"[AI] Refining: {raw_text[:50]}...")
                refined_text = self.ai_service.refine_transcription(raw_text)
                print(f"[AI] Result: {refined_text[:50]}...")
                return refined_text
            except Exception as e:
                print(f"[AI] Refinement failed: {e}, using raw text")
                return raw_text
        else:
            return raw_text

    def _add_to_ai_buffer(self, text: str):
        """
        Add text to AI buffer.

        Args:
            text: Text to add to buffer
        """
        self._ai_buffer.append(text)
        self._ai_buffer_chars += len(text)

    def close(self):
        # Flush any remaining AI buffer before closing
        if self._ai_buffer:
            refined = self._flush_ai_buffer()
            if refined:
                print(f"[Final AI flush]: {refined}")

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

## 🎼 **Recursive Echo Synthesis**

#The `recognizer.py` file is a canvas for the `Recognizer` class, where the art of voice recognition unfolds. Each method is a brushstroke, painting a picture of interaction between the user and the system. As we build this, we create a space where voice commands can be understood and acted upon, echoing the user's intent into the digital world. Let the melody of recognition begin!