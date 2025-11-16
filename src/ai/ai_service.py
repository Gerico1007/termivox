"""
AI Service Layer for Termivox

Provides AI-enhanced voice transcription with support for:
- Google Gemini
- OpenAI GPT models
- Custom master prompt for natural, multilingual output

♠️ Nyro: Provider abstraction, clean architecture
🎸 JamAI: Musical AI understanding, natural flow
🌿 Aureon: Breathing life into raw transcription
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


# 🔥 Master Prompt - Le cœur de l'intelligence Termivox
TERMIVOX_MASTER_PROMPT = """Tu es le module d'interprétation vocale avancé de **Termivox**.
Ton rôle est de transformer ma parole — en français, en anglais ou en mélange des deux — en texte clair, cohérent, fluide, fidèle au sens et au ton de ce que je dis.

### 🎯 **TES MISSIONS**

1. **Comprendre la parole naturelle telle qu'elle sort de ma bouche**
   * accents, hésitations, rythme, mélange de langues
   * expressions orales transformées en écriture naturelle

2. **Produire un texte propre, élégant, logique**
   * corriger la grammaire sans changer mes intentions
   * maintenir mon style personnel
   * structurer si nécessaire (phrases complètes, paragraphes si long)

3. **S'adapter automatiquement à la langue que j'emploie**
   * français → grammaire FR
   * anglais → grammaire EN
   * mélange → détecter chaque segment et l'écrire correctement

4. **Comprendre mes commandes vocales Termivox**
   * ponctuation : "virgule", "comma", "point", "period", etc.
   * commandes de mise en forme : "new line", "nouvelle ligne", "new paragraph", etc.
   * toujours les appliquer *intelligemment* dans le texte final.

5. **Reformuler légèrement si je parle de façon chaotique**
   (essoufflé, en marchant, parlant vite, etc.)
   * mais **jamais modifier le sens**

6. **Ignorer tous les bruits, faux départs et parasites**

### 🧠 **RÈGLES DE COMPRÉHENSION**

* Tu comprends les phrases **même si elles arrivent en fragments**.
* Tu reconstruis ce que je voulais dire, pas ce que j'ai dit de façon imparfaite.
* Si une phrase est ambiguë, tu choisis la lecture la plus naturelle.
* Si j'utilise des mots techniques (Termivox, toggle, widget), tu les gardes tels quels.

### 📝 **RÉSULTAT ATTENDU**

* Texte propre
* Fluide
* Structure claire si long
* Ponctuation correcte
* Bilingue parfait selon mon énoncé
* Jamais robotique
* Aucune introduction ni explication
* Uniquement le texte dicté

### 🎤 **EXEMPLES DE TRANSFORMATION**

**Moi (parole):**
« ok là j'suis dans le métro euh attends… oui, bref, fais un paragraphe pour dire que Termivox fonctionne parfaitement virgule et que je vais l'utiliser pour écrire mes notes. »

**Toi (sortie):**
Termivox fonctionne parfaitement, et je vais l'utiliser pour écrire mes notes.

---

**Moi (parole):**
"Okay switch to English now comma I think the widget should be a bit smaller period"

**Toi (sortie):**
Okay, switch to English now. I think the widget should be a bit smaller.

---

**Moi (parole):**
"nouvelle ligne aujourd'hui je suis fier de moi point"

**Toi (sortie):**
Aujourd'hui je suis fier de moi.

---

Maintenant, transforme cette transcription brute :
"""


class AIService(ABC):
    """
    Abstract base class for AI service providers.

    Each provider must implement the refine_transcription method
    to enhance raw voice transcription into natural text.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI service.

        Args:
            api_key: API key for the service (if None, will try environment variable)
            model: Model name to use (provider-specific)
        """
        self.api_key = api_key
        self.model = model
        self.master_prompt = TERMIVOX_MASTER_PROMPT

    @abstractmethod
    def refine_transcription(self, raw_text: str) -> str:
        """
        Refine raw transcription using AI.

        Args:
            raw_text: Raw voice transcription from Vosk

        Returns:
            Refined, natural text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the service is available (API key set, libraries installed).

        Returns:
            True if service can be used, False otherwise
        """
        pass


class GeminiAIService(AIService):
    """
    Google Gemini AI service implementation.

    Uses Gemini models for natural language understanding and refinement.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini AI service.

        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY env var)
            model: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._client = None

    def _get_client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError(
                    "google-generativeai not installed. "
                    "Run: pip install google-generativeai"
                )
        return self._client

    def is_available(self) -> bool:
        """Check if Gemini is available."""
        if not self.api_key:
            return False
        try:
            import google.generativeai
            return True
        except ImportError:
            return False

    def refine_transcription(self, raw_text: str) -> str:
        """
        Refine transcription using Gemini.

        Args:
            raw_text: Raw voice transcription

        Returns:
            AI-refined text
        """
        if not raw_text.strip():
            return raw_text

        try:
            client = self._get_client()

            # Combine master prompt with raw transcription
            full_prompt = self.master_prompt + "\n\n" + raw_text

            # Generate refined text
            response = client.generate_content(full_prompt)
            refined_text = response.text.strip()

            return refined_text

        except Exception as e:
            print(f"[Gemini AI] Error: {e}")
            # Fallback to raw text if AI fails
            return raw_text


class OpenAIService(AIService):
    """
    OpenAI GPT service implementation.

    Uses GPT models for natural language understanding and refinement.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI service.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: GPT model to use (default: gpt-4o-mini)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai not installed. "
                    "Run: pip install openai"
                )
        return self._client

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        if not self.api_key:
            return False
        try:
            import openai
            return True
        except ImportError:
            return False

    def refine_transcription(self, raw_text: str) -> str:
        """
        Refine transcription using OpenAI GPT.

        Args:
            raw_text: Raw voice transcription

        Returns:
            AI-refined text
        """
        if not raw_text.strip():
            return raw_text

        try:
            client = self._get_client()

            # Create chat completion with master prompt
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.master_prompt},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=1000
            )

            refined_text = response.choices[0].message.content.strip()
            return refined_text

        except Exception as e:
            print(f"[OpenAI] Error: {e}")
            # Fallback to raw text if AI fails
            return raw_text


def create_ai_service(provider: str, api_key: Optional[str] = None, model: Optional[str] = None) -> Optional[AIService]:
    """
    Factory function to create AI service instance.

    Args:
        provider: Provider name ("gemini", "openai", or "none")
        api_key: API key for the provider
        model: Model name to use

    Returns:
        AIService instance or None if provider is "none"
    """
    if provider.lower() == "gemini":
        return GeminiAIService(api_key=api_key, model=model or "gemini-2.0-flash-exp")
    elif provider.lower() == "openai":
        return OpenAIService(api_key=api_key, model=model or "gpt-4o-mini")
    elif provider.lower() == "none":
        return None
    else:
        raise ValueError(f"Unknown AI provider: {provider}")
