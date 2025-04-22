# app.py - Flask-applikasjonen for handel og lagerstyring
# Forbedret versjon basert på diskusjon og feilmeldinger

from flask import Flask, render_template, jsonify, current_app # La til current_app for logging
from api.api import api_blueprint
from database.database import Database # Antar denne håndterer .env og tilkobling riktig nå
import logging
import config # Laster konfigurasjon herfra

# Initialiser Flask-applikasjonen
app = Flask(__name__)

# Last inn konfigurasjon
app.config.update(config.FLASK_CONFIG)

# Registrer API-et som blueprint
app.register_blueprint(api_blueprint, url_prefix=config.API_CONFIG["PREFIX"])

# Sett opp logging til fil (som før)
logging.basicConfig(
    level=config.LOGGING_CONFIG["LOG_LEVEL"],
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=config.LOGGING_CONFIG["LOG_FILE"],
    filemode='a' # Legg til 'a' for append, ellers overskrives loggen hver gang
)

# Opprett databaseforbindelse (beholder global for enkelhet, men se kommentar i koden)
# MERK: Global db-instans kan være problematisk i flertrådede miljøer avhengig
# av hvordan Database-klassen håndterer tilkoblinger/pooling. Vurder
# app context eller Flask-extensions for større applikasjoner.
try:
    db = Database()
except Exception as e:
    logging.critical(f"⚠ KRITISK FEIL: Kunne ikke opprette databaseforbindelse ved oppstart: {e}")
    # Applikasjonen vil sannsynligvis ikke fungere, men vi lar den starte
    # slik at feilen logges og kan inspiseres.
    db = None

@app.route("/")
def home():
    """Hovedsiden med nøkkeltall fra databasen."""
    if not db:
        return jsonify({"error": "Databaseforbindelse ikke tilgjengelig"}), 503

    try:
        # Bruker SQL-kolonnenavn fra varehusdb.sql
        # Antar at BetaltDato er riktig case i databasen din.
        query = """
            SELECT
                (SELECT COUNT(*) FROM kunde),
                (SELECT COUNT(*) FROM ordre),
                (SELECT COUNT(*) FROM vare),
                (SELECT COUNT(*) FROM ordre WHERE BetaltDato IS NOT NULL),
                (SELECT COUNT(*) FROM ordre WHERE BetaltDato IS NULL)
            """
        stats = db.fetch_one(query)
        # Konverterer stats (som er en tuple) til en dict for enklere bruk i template
        stats_dict = {
            "antall_kunder": stats[0] if stats else 0,
            "antall_ordrer": stats[1] if stats else 0,
            "antall_varer": stats[2] if stats else 0,
            "antall_betalte": stats[3] if stats else 0,
            "antall_ubetalte": stats[4] if stats else 0,
        }
        return render_template("index.html", stats=stats_dict)
    except Exception as e:
        current_app.logger.error(f"⚠ Feil ved henting av nøkkeltall: {e}", exc_info=True)
        # Viser en feilside i stedet for JSON, da dette er en HTML-rute
        return render_template("error.html", error_message="Kunne ikke hente nøkkeltall fra databasen"), 500

@app.route("/varer")
def varer():
    """Viser varelageret."""
    if not db:
        return jsonify({"error": "Databaseforbindelse ikke tilgjengelig"}), 503

    try:
        # Korrigerte kolonnenavn for å matche varehusdb.sql (VNr, Betegnelse, Pris, Antall)
        # Bruker store forbokstaver som i CREATE TABLE for sikkerhets skyld.
        query = "SELECT VNr, Betegnelse, Pris, Antall FROM vare ORDER BY Betegnelse ASC;"
        varer_data = db.fetch_all(query)
        return render_template("varer.html", varer=varer_data)
    except Exception as e:
        current_app.logger.error(f"⚠ Feil ved henting av varelager: {e}", exc_info=True)
        return render_template("error.html", error_message="Kunne ikke hente varelager"), 500

@app.route("/kunder")
def kunder():
    """Viser kunder via direkte SQL-spørring (erstatter manglende prosedyre)."""
    if not db:
        return jsonify({"error": "Databaseforbindelse ikke tilgjengelig"}), 503

    try:
        # Erstatter kall til db.call_procedure("hent_alle_kunder")
        # Bruker kolonnenavn fra varehusdb.sql (KNr, Fornavn, Etternavn, etc.)
        query = """
            SELECT KNr, Fornavn, Etternavn, Adresse, PostNr
            FROM kunde
            ORDER BY Etternavn ASC, Fornavn ASC;
            """
        kunder_data = db.fetch_all(query)
        return render_template("kunder.html", kunder=kunder_data)
    except Exception as e:
        # Bruker current_app.logger som er standard i Flask
        current_app.logger.error(f"⚠ Feil ved henting av kunder: {e}", exc_info=True) # exc_info=True logger traceback
        return render_template("error.html", error_message="Kunne ikke hente kunder"), 500

@app.route("/ordrer")
def ordrer():
    """Viser alle ordrer."""
    if not db:
        return jsonify({"error": "Databaseforbindelse ikke tilgjengelig"}), 503

    try:
        # Korrigerte kolonnenavn for å matche varehusdb.sql
        # o.OrdreNr, o.OrdreDato, o.SendtDato, o.BetaltDato, k.Fornavn, k.Etternavn, o.KNr, k.KNr
        query = """
            SELECT o.OrdreNr, o.OrdreDato, o.SendtDato, o.BetaltDato,
                   CONCAT(k.Fornavn, ' ', k.Etternavn) AS kundenavn
            FROM ordre o
            JOIN kunde k ON o.KNr = k.KNr
            ORDER BY o.OrdreDato DESC;
            """
        ordrer_data = db.fetch_all(query)
        return render_template("ordrer.html", ordrer=ordrer_data)
    except Exception as e:
        current_app.logger.error(f"⚠ Feil ved henting av ordrer: {e}", exc_info=True)
        return render_template("error.html", error_message="Kunne ikke hente ordrer"), 500

# Enkel feilside-template (bør ligge i templates/error.html)
@app.errorhandler(500)
def internal_error(error):
    # Sikrer at feil logges selv om de ikke fanges i try/except over
    current_app.logger.error(f"Serverfeil: {error}", exc_info=True)
    return render_template("error.html", error_message="En intern serverfeil oppstod"), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    # Fanger opp andre uventede feil
    current_app.logger.error(f"Uhandlet unntak: {e}", exc_info=True)
    return render_template("error.html", error_message="En uventet feil oppstod"), 500

if __name__ == "__main__":
    host = config.FLASK_CONFIG.get('HOST', '127.0.0.1') # Bruk .get med default
    port = config.FLASK_CONFIG.get('PORT', 5000)
    debug = config.FLASK_CONFIG.get('DEBUG', False)

    # Logger *før* serveren starter
    logging.info(f"🚀 Flask-server starter på http://{host}:{port} med DEBUG={debug} 🚀")
    print(f"🚀 Flask-server starter på http://{host}:{port} 🚀") # Kan beholdes for synlighet i terminal

    app.run(debug=debug, host=host, port=port)