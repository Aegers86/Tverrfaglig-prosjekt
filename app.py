# app.py
from flask import Flask, render_template
from api.api import api_blueprint # Importerer den forenklede API-en
from database.database import Database
import logging
import os
from dotenv import load_dotenv

# Last inn miljøvariabler fra .env
load_dotenv()

# Initialiser Flask-applikasjonen
app = Flask(__name__)

# Sett hemmelig nøkkel (valgfritt, men god praksis)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_dev')

# Registrer API-et som blueprint (beholdt for /api/varer)
api_prefix = os.getenv('API_PREFIX', '/api')
app.register_blueprint(api_blueprint, url_prefix=api_prefix)

# Sett opp logging direkte fra .env
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_file = os.getenv('LOG_FILE', 'app.log')
logging.basicConfig(
    level=getattr(logging, log_level.upper(), logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_file
)

# Opprett databaseforbindelse
db = Database() # Denne bruker .env via database.py

@app.route("/") # Startside viser også varer
@app.route("/varer")
def varer():
    """Viser varelageret."""
    try:
        # Henter varer direkte fra DB for initiell sidevisning
        # Bruker korrekte kolonnenavn
        varer_data = db.fetch_all("SELECT VNr, Betegnelse, Pris, Antall FROM vare ORDER BY Betegnelse ASC;")

        # Konvertering av Decimal er sannsynligvis ikke nødvendig her
        # siden Jinja-formatfilteret ("%.2f"|format) i malen håndterer det.

        # Sender data til malen
        return render_template("varer.html", varer=varer_data)
    except Exception as e:
        logging.error(f"⚠ Feil ved henting av varelager for siden: {e}")
        # Du bør lage en enkel feil.html eller bare returnere en tekststreng
        try:
            return render_template("feil.html", error_message="Kunne ikke hente varelager"), 500
        except:
             return "En intern serverfeil oppstod.", 500 # Fallback hvis feil.html mangler

if __name__ == "__main__":
    # Leser direkte fra .env
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logging.info(f"🚀 Flask-server starter på http://{host}:{port} 🚀")
    # Bruker os.getenv for debug, host, port
    app.run(debug=debug, host=host, port=port)
    print(f"🚀 Flask-server starter på http://{host}:{port} 🚀")