from deep_translator import GoogleTranslator


def translate_to_english(text, language):
    if not text or not text.strip():
        return None

    if language == "English":
        return text

    language_codes = {
        "Telugu": "te",
        "Hindi": "hi"
    }

    source_language = language_codes.get(language)

    if not source_language:
        return None

    try:
        translated = GoogleTranslator(
            source=source_language,
            target="en"
        ).translate(text)

        return translated

    except Exception as e:
        print(f"Translation failed: {e}")
        return None