# utils/validators.py
# Input-validering (tilpasset Norge)
import re

def is_valid_postnr(postnr):
    """ Sjekker om strengen er et gyldig 4-sifret norsk postnummer. """
    return isinstance(postnr, str) and postnr.isdigit() and len(postnr) == 4

# Antar norsk mobil/fasttelefon lengde
def is_valid_phone(phone):
    """ Sjekker om strengen er et gyldig norsk telefonnummer (kun sifre, 8-12 siffer). """
    if phone is None: # Håndterer None input
        return False
    # --- ENDRET HER: Bruker generator expression istedenfor filter ---
    phone_digits = "".join(c for c in str(phone) if c.isdigit())
    # --- Slutt på endring ---
    return phone_digits.isdigit() and 8 <= len(phone_digits) <= 12

def is_valid_email(email):
    """ Sjekker om strengen ser ut som en gyldig e-postadresse. """
    if not isinstance(email, str):
        return False
    # --- ENDRET HER: Fjernet \ før . inne i [] ---
    # \w matcher bokstaver, tall, _
    # . - matcher bokstavelig punktum eller bindestrek inne i []
    # \. matcher bokstavelig punktum utenfor []
    # + betyr en eller flere
    # {2,} betyr to eller flere
    pattern = r"^[\w.-]+@[\w.-]+\.[a-z]{2,}$"
    # --- Slutt på endring ---
    return re.match(pattern, email, re.IGNORECASE) is not None

def is_valid_name(name):
    """ Sjekker om navnet inneholder minst to tegn og kun bokstaver/mellomrom. """
    if not isinstance(name, str) or len(name.strip()) < 2:
        return False
    # Tillater bokstaver (inkl. æøå), bindestrek og mellomrom
    return all(c.isalpha() or c.isspace() or c == '-' for c in name.strip())

def is_valid_address(address):
    """ Sjekker om adressen har minst 5 tegn og inneholder minst ett tall (husnummer). """
    if not isinstance(address, str) or len(address.strip()) < 5:
        return False
    # Enkel sjekk - bør kanskje være mer robust
    return any(c.isdigit() for c in address)

# is_valid_city og is_valid_country er ikke brukt i valider_kundefelter per nå
def is_valid_city(city):
    """ Sjekker om bynavnet inneholder minst to tegn og kun bokstaver/mellomrom. """
    if not isinstance(city, str) or len(city.strip()) < 2:
        return False
    # Tillater bokstaver, bindestrek og mellomrom
    return all(c.isalpha() or c.isspace() or c == '-' for c in city.strip())

def is_valid_country(country):
    """ Sjekker om land inneholder minst to tegn og kun bokstaver/mellomrom/bindestrek. """
    if not isinstance(country, str) or len(country.strip()) < 2:
        return False
    # Tillater bokstaver, bindestrek og mellomrom
    return all(c.isalpha() or c.isspace() or c == '-' for c in country.strip())

# is_valid_date er ikke brukt per nå
def is_valid_date(date_str):
    """ Sjekker om strengen er en gyldig dato på format DD/MM/YYYY (enkel sjekk). """
    if not isinstance(date_str, str): return False
    try:
        # Bruker datetime for mer robust sjekk (hvis tilgjengelig)
        from datetime import datetime
        datetime.strptime(date_str, '%d/%m/%Y')
        # Sjekk fornuftig årstall hvis nødvendig
        year = int(date_str.split('/')[-1])
        return 1900 < year <= 2100 # Eksempel på avgrensning
    except (ValueError, ImportError):
        # Fallback til enkel sjekk hvis datetime feiler eller ikke finnes
        try:
            day, month, year = map(int, date_str.split("/"))
            # Veldig enkel sjekk - validerer ikke dager i måneden etc.
            return 1 <= day <= 31 and 1 <= month <= 12 and 1900 < year <= 2100
        except ValueError:
            return False

# is_valid_number er ikke brukt per nå
def is_valid_number(number_str):
    """ Sjekker om strengen kan konverteres til et tall (int eller float). """
    if isinstance(number_str, (int, float)): return True
    if not isinstance(number_str, str): return False
    try:
        float(str(number_str).replace(',', '.')) # Håndter komma som desimaltegn
        return True
    except ValueError:
        return False

def is_nonempty(value):
    """ Sjekker om strengen ikke er tom etter fjerning av whitespace. """
    return isinstance(value, str) and bool(value.strip())

# --- Valideringsfunksjon for kundeskjema ---
def valider_kundefelter(felter):
    """ Validerer feltene som typisk kommer fra et kundeskjema.
        Returnerer en liste med feilmeldinger, eller en tom liste hvis alt er OK.
    """
    feil = []
    # Bruker .get for å unngå KeyError hvis et felt mangler i dict
    # Bruker is_nonempty for felt som må fylles ut
    if not felter.get("fornavn") or not is_valid_name(felter.get("fornavn", "")):
        feil.append("Fornavn er ugyldig eller mangler.")
    if not felter.get("etternavn") or not is_valid_name(felter.get("etternavn", "")):
        feil.append("Etternavn er ugyldig eller mangler.")
    if not felter.get("adresse") or not is_valid_address(felter.get("adresse", "")):
        feil.append("Adresse er ugyldig eller mangler (må inneholde tall).")
    if not felter.get("postnr") or not is_valid_postnr(felter.get("postnr", "")):
        feil.append("Postnummer er ugyldig eller mangler (4 siffer).")

    # Gjør telefon og epost valgfrie - sjekk kun hvis de er oppgitt
    telefon = felter.get("telefon")
    if telefon and not is_valid_phone(telefon): # Sjekk kun hvis feltet har en verdi
        feil.append("Telefonnummer er ugyldig (8-12 siffer).")

    epost = felter.get("epost")
    if epost and not is_valid_email(epost): # Sjekk kun hvis feltet har en verdi
        feil.append("E-postadresse er ugyldig.")