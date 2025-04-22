# utils/validators.py
# Input-validering (tilpasset Norge)
import re

def is_valid_postnr(postnr):
    return postnr.isdigit() and len(postnr) == 4

def is_valid_phone(phone):
    return phone.isdigit() and 8 <= len(phone) <= 12

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.[a-z]{2,}$", email, re.IGNORECASE) is not None

def is_valid_zip(zip_code):
    return is_valid_postnr(zip_code)

def is_valid_name(name):
    return all(part.isalpha() for part in name.split()) and len(name.strip()) >= 2

def is_valid_address(address):
    return len(address.strip()) >= 5 and any(c.isdigit() for c in address)

def is_valid_city(city):
    return all(part.isalpha() for part in city.split()) and len(city.strip()) >= 2

def is_valid_country(country):
    return all(part.isalpha() for part in re.split(r"[- ]", country)) and len(country.strip()) >= 2

def is_valid_date(date_str):
    try:
        day, month, year = map(int, date_str.split("/"))
        return 1 <= day <= 31 and 1 <= month <= 12 and 1900 < year <= 2100
    except ValueError:
        return False

def is_valid_number(number):
    try:
        float(number)
        return True
    except ValueError:
        return False

def is_nonempty(value):
    return bool(value.strip())

def valider_kundefelter(felter):
    feil = []
    if not is_valid_name(felter.get("fornavn", "")):
        feil.append("Ugyldig fornavn")
    if not is_valid_name(felter.get("etternavn", "")):
        feil.append("Ugyldig etternavn")
    if not is_valid_address(felter.get("adresse", "")):
        feil.append("Ugyldig adresse")
    if not is_valid_postnr(felter.get("postnr", "")):
        feil.append("Ugyldig postnummer")
    if not is_valid_phone(felter.get("telefon", "")):
        feil.append("Ugyldig telefonnummer")
    if not is_valid_email(felter.get("epost", "")):
        feil.append("Ugyldig e-postadresse")
    return feil
