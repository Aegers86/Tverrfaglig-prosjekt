# helpers.py
# Inneholder hjelpefunksjoner for felles logikk i prosjektet

import re
from logs.logs import log_info

def validate_email(email: str) -> bool:
    """Validerer en e-postadresse."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def format_currency(amount: float) -> str:
    """Formaterer en flyttallsverdi som en valuta."""
    return f"{amount:,.2f} NOK"

def log_action(action: str):
    """Logger en handling til systemet."""
    log_info(f"Handling utført: {action}")