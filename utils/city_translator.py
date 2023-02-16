"""Модуль-переводчик ru-en."""
import translators as ts


def translate(text: str) -> str:
    """Переводит текст на английский язык."""
    rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    if text[0].lower() in rus:
        return ts.translate_text(query_text=text, translator="google", to_language="en")
    return text
