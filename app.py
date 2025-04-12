# app.py - Flask-applikasjonen for handel og lagerstyring
from flask import Flask, render_template, jsonify
from api.api import api_blueprint
from database.database import Database
import logging
import config
from database.populate_database import populate_database  # ✅ Importer og kjør

# ✅ Initialiser Flask-applikasjonen
app = Flask(__name__)

# ✅ Last inn konfigurasjon
app.config.update(config.FLASK_CONFIG)

# ✅ Registrer API-et som blueprint
app.register_blueprint(api_blueprint, url_prefix=config.API_CONFIG["PREFIX"])

# ✅ Sett opp logging
logging.basicConfig(
    level=config.LOGGING_CONFIG["LOG_LEVEL"],
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=config.LOGGING_CONFIG["LOG_FILE"]
)

# ✅ Opprett databaseforbindelse
db = Database()

# ✅ Kjør populate_database ved oppstart
try:
    logging.info("🔄 Kjører `populate_database.py` for å sikre testdata...")
    populate_database()
    logging.info("✅ Databasen er fylt med testdata!")
except Exception as e:
    logging.error(f"⚠ Feil ved kjøring av `populate_database.py`: {e}")

@app.route("/")
def home():
    """Hovedsiden med nøkkeltall fra databasen."""
    try:
        stats = db.fetch_one(
            """
            SELECT 
                (SELECT COUNT(*) FROM kunde),
                (SELECT COUNT(*) FROM ordre),
                (SELECT COUNT(*) FROM vare),
                (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NOT NULL),
                (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NULL)
            """
        )
        return render_template("index.html", stats=stats)
    except Exception as e:
        logging.error(f"⚠ Feil ved henting av nøkkeltall: {e}")
        return jsonify({"error": "Kunne ikke hente nøkkeltall fra databasen"}), 500

@app.route("/varer")
def varer():
    """Viser varelageret."""
    try:
        varer = db.fetch_all("SELECT varenummer, betegnelse, pris, antall FROM vare ORDER BY betegnelse ASC;")
        return render_template("varer.html", varer=varer)
    except Exception as e:
        logging.error(f"⚠ Feil ved henting av varelager: {e}")
        return jsonify({"error": "Kunne ikke hente varelager"}), 500

@app.route("/kunder")
def kunder():
    """Viser kunder via Stored Procedure."""
    try:
        kunder = db.call_procedure("hent_alle_kunder")
        return render_template("kunder.html", kunder=kunder)
    except Exception as e:
        logging.error(f"⚠ Feil ved henting av kunder: {e}")
        return jsonify({"error": "Kunne ikke hente kunder"}), 500

@app.route("/ordrer")
def ordrer():
    """Viser alle ordrer."""
    try:
        ordrer = db.fetch_all(
            """
            SELECT o.ordrenummer, o.ordre_dato, o.dato_sendt, o.betalt_dato, 
                   CONCAT(k.fornavn, ' ', k.etternavn) AS kundenavn 
            FROM ordre o 
            JOIN kunde k ON o.kundenummer = k.knr
            ORDER BY o.ordre_dato DESC;
            """
        )
        return render_template("ordrer.html", ordrer=ordrer)
    except Exception as e:
        logging.error(f"⚠ Feil ved henting av ordrer: {e}")
        return jsonify({"error": "Kunne ikke hente ordrer"}), 500

if __name__ == "__main__":
    logging.info(f"🚀 Flask-server starter på http://{config.FLASK_CONFIG['HOST']}:{config.FLASK_CONFIG['PORT']} 🚀")
    app.run(debug=config.FLASK_CONFIG["DEBUG"], host=config.FLASK_CONFIG["HOST"], port=config.FLASK_CONFIG["PORT"])
    print(f"🚀 Flask-server starter på http://{config.FLASK_CONFIG['HOST']}:{config.FLASK_CONFIG['PORT']} 🚀")
