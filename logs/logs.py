# logs/logs.py
# Enkel logging for feilsøking og ytelsesmåling

import logging
import os # For å lage loggmappe

# Definer loggmappe og filnavn (mer robust enn relativ sti)
# Antar at logs.py ligger i en 'logs' mappe under prosjektets rot
# Eller juster stien etter din struktur
LOG_DIR = os.path.dirname(os.path.abspath(__file__)) # Finner mappen logs.py ligger i
# Går ett nivå opp for å legge app.log i prosjekt-roten, eller behold LOG_DIR for å legge den i logs-mappen
LOG_FILE_PATH = os.path.join(os.path.dirname(LOG_DIR), "app.log") # Legger app.log i mappen over logs/
# Alternativt: LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log") # Legger app.log i logs/

# Opprett loggmappen (hvis den ikke er roten) - trenger ikke hvis vi logger til roten
# try:
#     os.makedirs(LOG_DIR, exist_ok=True)
# except OSError as e:
#     print(f"FEIL: Kunne ikke opprette loggmappe '{LOG_DIR}': {e}")

# Konfigurer logging
logging.basicConfig(
    filename=LOG_FILE_PATH, # Bruker full sti
    level=logging.INFO, # Sett til logging.DEBUG for mer detaljer
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s", # Mer detaljert format
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8' # Spesifiser encoding
)

# Logger for å bekrefte at logging er konfigurert
logging.info("--- Logging startet ---")

def log_info(message: str):
    """Logger informasjon (INFO level)."""
    logging.info(message)

# --- OPPDATERT log_error ---
def log_error(message: str, exc_info=False):
    """Logger feil (ERROR level).
       Sett exc_info=True for å inkludere traceback.
    """
    # Sender exc_info videre til logging.error
    logging.error(message, exc_info=exc_info)
# --- Slutt på oppdatering ---

def log_warning(message: str):
    """Logger advarsler (WARNING level)."""
    logging.warning(message)

# Eksempel på bruk hvis filen kjøres direkte
if __name__ == '__main__':
     log_info("Test info-melding fra logs.py.")
     log_warning("Test advarsel-melding fra logs.py.")
     try:
         x = 1 / 0
     except ZeroDivisionError:
         # Logger feil MED traceback
         log_error("Test feilmelding med traceback", exc_info=True)
     print(f"Loggfil skal finnes på: {LOG_FILE_PATH}")