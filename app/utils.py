import unidecode

def normalize_text(text):
    if text is None:
        return ""
    # Usuwanie znaków specjalnych i normalizacja do ASCII
    text = str(text)
    normalized = unidecode.unidecode(text).lower()  # konwersja do ASCII i małych liter
    return ''.join(c for c in normalized if c.isalnum() or c.isspace())
