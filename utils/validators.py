# utils/validators.py
# Input-validering (tilpasset Norge)

import re
from datetime import datetime

# --- Enkle validatorer ---

def is_valid_postnr(postnr):
    return isinstance(postnr, str) and postnr.isdigit() and len(postnr) == 4

def is_valid_phone(phone):
    if phone is None:
        return False
    phone_digits = "".join(c for c in str(phone) if c.isdigit())
    return phone_digits.isdigit() and 8 <= len(phone_digits) <= 12

def is_valid_email(email):
    if not isinstance(email, str):
        return False
    pattern = r"^[\w.-]+@[\w.-]+\.[a-z]{2,}$"
    return re.match(pattern, email, re.IGNORECASE) is not None

def is_valid_name(name):
    if not isinstance(name, str) or len(name.strip()) < 2:
        return False
    return all(c.isalpha() or c.isspace() or c == '-' for c in name.strip())

def is_valid_address(address):
    if not isinstance(address, str) or len(address.strip()) < 5:
        return False
    return any(c.isdigit() for c in address)

def is_valid_is_active(value):
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.lower() in ("true", "false", "1", "0")
    return False

def is_valid_date(date_str):
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, '%d/%m/%Y')
        year = int(date_str.split('/')[-1])
        return 1900 < year <= 2100
    except (ValueError, ImportError):
        try:
            day, month, year = map(int, date_str.split("/"))
            return 1 <= day <= 31 and 1 <= month <= 12 and 1900 < year <= 2100
        except ValueError:
            return False

def is_valid_number(number_str):
    if isinstance(number_str, (int, float)):
        return True
    if not isinstance(number_str, str):
        return False
    try:
        float(str(number_str).replace(',', '.'))
        return True
    except ValueError:
        return False

def is_nonempty(value):
    return isinstance(value, str) and bool(value.strip())

# --- Feltdefinisjon for kunde ---

FELTDEFINISJONER = {
    "fornavn": (is_valid_name, "Fornavn er ugyldig eller mangler."),
    "etternavn": (is_valid_name, "Etternavn er ugyldig eller mangler."),
    "adresse": (is_valid_address, "Adresse er ugyldig eller mangler (må inneholde tall)."),
    "postnr": (is_valid_postnr, "Postnummer er ugyldig eller mangler (4 siffer)."),
    "telefon": (is_valid_phone, "Telefonnummer er ugyldig (8-12 siffer)."),  # Valgfri
    "epost": (is_valid_email, "E-postadresse er ugyldig."),                  # Valgfri
    "is_active": (is_valid_is_active, "Status (aktiv/passiv) må være gyldig.") # Valgfri
}

# --- Hovedvalideringsfunksjon ---

def valider_kundefelter(felter):
    """ Validerer kundeskjema basert på FELTDEFINISJONER. """
    feil = []
    for felt, (valideringsfunksjon, feilmelding) in FELTDEFINISJONER.items():
        verdi = felter.get(felt)

        if felt in ("telefon", "epost", "is_active"):
            if verdi and not valideringsfunksjon(verdi):
                feil.append(feilmelding)
        else:
            if not verdi or not valideringsfunksjon(verdi):
                feil.append(feilmelding)

    return feil
