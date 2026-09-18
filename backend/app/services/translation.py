import os

from dotenv import load_dotenv
import argostranslate.translate
from sarvamai import SarvamAI

load_dotenv()


def translate_to_english(text, language):
    if not text or not text.strip():
        return None

    # English does not need translation
    if language == "English":
        return text

    # Hindi → English using Argos Translate
    if language == "Hindi":
        try:
            translated = argostranslate.translate.translate(
                text,
                "hi",
                "en"
            )
            return translated

        except Exception as e:
            print(f"Hindi translation failed: {e}")
            return None

    # Telugu → English using Sarvam AI
    if language == "Telugu":
        try:
            api_key = os.getenv("SARVAM_API_KEY")

            if not api_key:
                print("SARVAM_API_KEY not found")
                return None

            client = SarvamAI(
                api_subscription_key=api_key
            )

            response = client.text.translate(
                input=text,
                source_language_code="te-IN",
                target_language_code="en-IN"
            )

            return response.translated_text

        except Exception as e:
            print(f"Telugu translation failed: {e}")
            return None

    # Unsupported language
    return None
    