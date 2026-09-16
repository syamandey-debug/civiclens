from lingua import Language, LanguageDetectorBuilder


languages = [
    Language.ENGLISH,
    Language.TELUGU,
    Language.HINDI
]


detector = LanguageDetectorBuilder.from_languages(
    *languages
).build()


def detect_language(text):

    if not text or not text.strip():
        return None

    language = detector.detect_language_of(text)

    if language is None:
        return None

    return language.name.title()