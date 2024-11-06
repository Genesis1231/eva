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
        raise ValueError(f"Language {language} is not supported.")
    
    return LANGUAGE_DICT.get(language, "multilingual") 