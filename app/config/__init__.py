from .log import logger
from .config import eva_configuration

LANGUAGE_DICT = {
    "en": "english",
    "zh": "chinese",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "ja": "japanese",
    "ko": "korean",
    "ru": "russian",
    "es": "spanish",
    "multilingual": "multilingual"
}

def validate_language(language: str)-> str:
    if language not in LANGUAGE_DICT:
        logger.error(f"Language {language} is not supported, switching to multilingual mode.")

    return LANGUAGE_DICT.get(language, "multilingual")