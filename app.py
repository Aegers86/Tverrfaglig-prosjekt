# app.py
# Hovedfil for Flask web-applikasjonen som viser varelager.
# Denne versjonen er forenklet for å kun håndtere varer,
# og henter all konfigurasjon fra .env-filen.

# Importerer nødvendige Flask-moduler og egne moduler/klasser
from flask import Flask, render_template       # Flask-kjerne og mal-rendering
from api.api import api_blueprint              # Importerer API-blueprint (for /api/varer)
from database.database import Database         # Importerer vår databaseklasse
import logging                                 # Importerer standard logging
import os                                      # Importerer for å få tilgang til miljøvariabler
from dotenv import load_dotenv                 # Importerer for å laste .env-fil

# Last inn miljøvariabler fra .env
load_dotenv()                                  # Leser .env-filen og gjør variablene tilgjengelige

# Initialiser Flask-applikasjonen
app = Flask(__name__)                          # Oppretter en instans av Flask

# Sett hemmelig nøkkel (brukes for sessions, flash-meldinger etc., god praksis å ha med)
# Henter fra .env, med en fallback for utvikling hvis den mangler.
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_dev_only')

# Registrer API-et som blueprint (beholdt for /api/varer)
# API-et definert i api/api.py blir tilgjengelig under /api (eller hva API_PREFIX er i .env)
api_prefix = os.getenv('API_PREFIX', '/api')   # Henter API prefix fra .env, default er /api
app.register_blueprint(api_blueprint, url_prefix=api_prefix) # Registrerer blueprintet

# Sett opp logging direkte fra .env
log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper() # Henter loggnivå fra .env (INFO som default)
log_file = os.getenv('LOG_FILE', 'app.log')         # Henter loggfilnavn fra .env (app.log som default)
log_level = getattr(logging, log_level_str, logging.INFO) # Finner riktig logging-konstant

# Konfigurerer basis logging til fil
logging.basicConfig(
    level=log_level,                             # Setter loggnivå (f.eks. INFO, DEBUG, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s", # Definerer formatet på loggmeldingene
    filename=log_file                            # Angir filen loggmeldingene skal skrives til
)

# Opprett databaseforbindelse
# Oppretter en instans av vår Database-klasse
# Denne klassen henter selv DB-info fra .env
db = Database()

# Definerer ruter for web-appen
@app.route("/")                                # Definerer at roten (/) skal bruke varer()-funksjonen
@app.route("/varer")                           # Definerer at /varer også skal bruke varer()-funksjonen
def varer():                                   # Funksjon som håndterer requests til / og /varer
    """Viser varelageret ved å rendre varer.html."""
    try:                                       # Starter try-block for feilhåndtering
        # Henter varer direkte fra DB for initiell sidevisning
        # Bruker korrekte kolonnenavn i SQL-spørringen
        varer_data = db.fetch_all("SELECT VNr, Betegnelse, Pris, Antall FROM vare ORDER BY Betegnelse ASC;")

        # Kommenterer ut Decimal-konvertering her, da Jinja-filteret i malen
        # sannsynligvis håndterer formatering av Pris (Decimal) til string greit.
        # varer_data = convert_decimals(varer_data) # Ville trengt import av convert_decimals fra api.py

        # Sender hentede data (varer_data) til HTML-malen 'varer.html'
        # Data blir tilgjengelig i malen via variabelnavnet 'varer'
        return render_template("varer.html", varer=varer_data)
    except Exception as e:                     # Fanger eventuelle feil under databasekall eller rendering
        logging.error(f"⚠ Feil ved henting av varelager for siden: {e}") # Logger feilen
        # Prøver å rendre en dedikert feilside (feil.html må finnes i templates)
        try:
                                               # Sender feilmelding til feilmalen
            return render_template("feil.html", error_message="Kunne ikke hente varelager"), 500
        except:                                # Hvis feil.html også feiler (f.eks. mangler)
                                               # Returner en enkel tekstfeilmelding
             return "En intern serverfeil oppstod under sidevisning.", 500

# Starter Flask-serveren hvis skriptet kjøres direkte
if __name__ == "__main__":                     # Sjekker om dette er hovedfilen som kjøres
    # Leser host, port og debug-modus fra .env, med standardverdier
    host = os.getenv('FLASK_HOST', '127.0.0.1') # Henter vert fra .env (default 127.0.0.1)
    port = int(os.getenv('FLASK_PORT', 5000))   # Henter port fra .env (default 5000)
                                               # Henter debug-flagg fra .env (default False)
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Logger at serveren starter (bruker standard logging konfigurert over)
    logging.info(f"🚀 Flask-server starter på http://{host}:{port} - Debug: {debug} 🚀")
    # Starter Flask sin innebygde utviklingsserver
    app.run(debug=debug, host=host, port=port)
    # Denne linjen nås kun etter at serveren er stoppet
    print(f"Flask-server på http://{host}:{port} er stoppet.")