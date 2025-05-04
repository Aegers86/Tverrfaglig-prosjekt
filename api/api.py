# api/api.py
# Definerer API-endepunkter for varer ved bruk av Flask Blueprint.

from flask import Blueprint, request, jsonify  # Importerer nødvendige Flask-komponenter
from database.database import Database         # Importerer databaseklassen
import logging                                 # Importerer standard logging
import mysql.connector                         # Importerer for å fange spesifikke DB-feil
import decimal                                 # Importerer for å håndtere Decimal-typen fra DB

# Opprett Blueprint for API
# Blueprint brukes for å organisere routes i moduler
api_blueprint = Blueprint("api", __name__)
db = Database()                                # Initialiserer en instans av databaseklassen

# --- Hjelpefunksjoner ---
def convert_decimals(data):                    # Funksjon for å konvertere Decimal til float
    """Konverterer rekursivt Decimal-objekter til float for JSON-serialisering."""
    if isinstance(data, list):                 # Sjekker om data er en liste
                                               # Går gjennom hvert element i listen
        return [convert_decimals(item) for item in data]
    if isinstance(data, dict):                 # Sjekker om data er en dictionary
                                               # Går gjennom nøkkel/verdi-par i ordboken
        new_dict = {}
        for key, value in data.items():        # Itererer gjennom dictionary
            if isinstance(value, decimal.Decimal): # Sjekker om verdien er Decimal
                new_dict[key] = float(value)   # Konverterer Decimal til float
            else:
                                               # Kall rekursivt for nestede strukturer
                new_dict[key] = convert_decimals(value)
        return new_dict                        # Returnerer den konverterte dictionary
                                               # Returner uendret hvis ikke liste/dict/Decimal
    return data

# --- Vare-Endepunkter (Kun disse beholdes) ---

# Hente alle varer
@api_blueprint.route("/varer", methods=["GET"]) # Definerer route for GET /api/varer
def get_varer():                               # Funksjon for å hente alle varer
    try:                                       # Starter try-block for feilhåndtering
                                               # Henter alle varer fra DB, sortert etter betegnelse
        varer = db.fetch_all("SELECT VNr, Betegnelse, Pris, Antall FROM vare ORDER BY Betegnelse")
                                               # Konverterer evt. Decimal-verdier i resultatet
        varer = convert_decimals(varer)
                                               # Returnerer JSON-respons med varene (eller tom liste), status 200 OK
        return jsonify(varer or []), 200
    except Exception as e:                     # Fanger generelle feil
        logging.error(f"Feil ved henting av varer: {e}") # Logger feilen
                                               # Returnerer JSON-feilmelding, status 500 Internal Server Error
        return jsonify({"error": "Kunne ikke hente varer"}), 500

# Hente en spesifikk vare
@api_blueprint.route("/varer/<string:vnr>", methods=["GET"]) # Definerer route for GET /api/varer/<varenummer>
def get_vare(vnr):                             # Funksjon for å hente én vare, tar 'vnr' fra URL
    try:                                       # Starter try-block
                                               # Henter én vare basert på VNr
        vare = db.fetch_one("SELECT VNr, Betegnelse, Pris, Antall, KatNr, Hylle FROM vare WHERE VNr = %s", (vnr,))
        if not vare:                           # Sjekker om varen ble funnet
            logging.warning(f"Vare med VNr {vnr} ikke funnet") # Logger en advarsel
                                               # Returnerer JSON-feilmelding, status 404 Not Found
            return jsonify({"error": "Varen finnes ikke"}), 404
                                               # Konverterer evt. Decimal-verdier
        vare = convert_decimals(vare)
                                               # Returnerer JSON-respons med varen, status 200 OK
        return jsonify(vare), 200
    except Exception as e:                     # Fanger generelle feil
        logging.error(f"Feil ved henting av vare {vnr}: {e}") # Logger feilen
                                               # Returnerer JSON-feilmelding, status 500
        return jsonify({"error": "Kunne ikke hente varen"}), 500

# Legge til en ny vare
@api_blueprint.route("/varer", methods=["POST"]) # Definerer route for POST /api/varer
def add_vare():                                # Funksjon for å legge til en ny vare
    data = None                                # Initialiserer data for sikker bruk i feilhåndtering
    try:                                       # Starter try-block
        data = request.get_json()              # Henter JSON-data fra request body
                                               # Definerer påkrevde felt
        required_fields = ["vnr", "betegnelse", "pris", "antall"]
                                               # Validerer at data finnes og inneholder påkrevde felt
        if not data or not all(field in data and data[field] is not None for field in required_fields):
            logging.warning(f"Manglende data ved forsøk på å legge til vare. Fikk: {data}. Krever: {required_fields}")
                                               # Returnerer JSON-feilmelding, status 400 Bad Request
            return jsonify({"error": "Ugyldig inndata", "required": required_fields}), 400

                                               # SQL-spørring for å sette inn ny vare
        query = "INSERT INTO vare (VNr, Betegnelse, Pris, Antall) VALUES (%s, %s, %s, %s)"
                                               # Utfører spørringen med data fra request
        success = db.execute_query(query, (data["vnr"], data["betegnelse"], data["pris"], data["antall"]))

        if not success:                        # Sjekker om execute_query feilet
            logging.warning("db.execute_query returnerte False ved innsending av ny vare")
                                               # Returnerer JSON-feilmelding, status 500
            return jsonify({"error": "Kunne ikke legge til vare (ukjent databasefeil)"}), 500

                                               # Henter den nylig innsatte varen for å returnere den
        new_vare = db.fetch_one("SELECT VNr, Betegnelse, Pris, Antall FROM vare WHERE VNr = %s", (data["vnr"],))
                                               # Konverterer evt. Decimal-verdier
        new_vare = convert_decimals(new_vare)
                                               # Returnerer JSON-respons med den nye varen, status 201 Created
        return jsonify(new_vare or {"message": "Vare lagt til, men kunne ikke hentes umiddelbart"}), 201

    except mysql.connector.Error as err:       # Fanger spesifikke MySQL-feil
        vnr_value = data.get('vnr', 'N/A') if data else 'N/A' # Sikker henting av VNr for logging
        if err.errno == 1062:                  # Sjekker om feilen er "Duplicate entry" (unik nøkkel brutt)
            logging.warning(f"Forsøk på å legge til vare med eksisterende VNr: {vnr_value}")
                                               # Returnerer JSON-feilmelding, status 409 Conflict
            return jsonify({"error": f"Vare med VNr {vnr_value} finnes allerede"}), 409
        else:                                  # Andre databasefeil
            logging.error(f"Databasefeil ved oppretting av vare (VNr={vnr_value}): {err}")
                                               # Returnerer JSON-feilmelding, status 500
            return jsonify({"error": "Databasefeil ved oppretting av vare"}), 500
    except Exception as e:                     # Fanger andre generelle feil
        vnr_value = data.get('vnr', 'N/A') if data else 'N/A'
        logging.error(f"Generell feil ved oppretting av vare (VNr={vnr_value}): {e}")
                                               # Returnerer JSON-feilmelding, status 500
        return jsonify({"error": "Serverfeil ved oppretting av vare"}), 500

# Oppdatere en vare
@api_blueprint.route("/varer/<string:vnr>", methods=["PUT"]) # Definerer route for PUT /api/varer/<varenummer>
def update_vare(vnr):                          # Funksjon for å oppdatere en vare
    try:                                       # Starter try-block
        data = request.get_json()              # Henter JSON-data fra request body
        if not data:                           # Sjekker om data ble sendt med
            logging.warning(f"Manglende data ved oppdatering av vare {vnr}")
                                               # Returnerer JSON-feilmelding, status 400
            return jsonify({"error": "Ugyldig inndata, ingen data mottatt"}), 400

                                               # Definerer påkrevde felt for oppdatering
        required_fields = ["betegnelse", "pris", "antall"]
                                               # Validerer at påkrevde felt finnes
        if not all(field in data for field in required_fields):
             logging.warning(f"Manglende data ved oppdatering av vare {vnr}. Fikk: {data}. Krever: {required_fields}")
                                               # Returnerer JSON-feilmelding, status 400
             return jsonify({"error": "Ugyldig inndata", "required": required_fields}), 400

                                               # SQL-spørring for å oppdatere varen
        query = "UPDATE vare SET Betegnelse=%s, Pris=%s, Antall=%s WHERE VNr=%s"
                                               # Utfører spørringen
        success = db.execute_query(query, (data["betegnelse"], data["pris"], data["antall"], vnr))

        if not success:                        # Sjekker om execute_query feilet
             logging.warning(f"Kunne ikke oppdatere vare med VNr {vnr} (execute_query feilet)")
                                               # Returnerer JSON-feilmelding, status 500
             return jsonify({"error": "Kunne ikke oppdatere vare (databasefeil)"}), 500

                                               # Henter den oppdaterte varen for å returnere den
        updated_vare = db.fetch_one("SELECT VNr, Betegnelse, Pris, Antall FROM vare WHERE VNr = %s", (vnr,))
                                               # Konverterer evt. Decimal-verdier
        updated_vare = convert_decimals(updated_vare)
                                               # Returnerer JSON-respons med oppdatert vare, status 200 OK
        return jsonify(updated_vare or {"message": "Vare oppdatert, men kunne ikke hentes umiddelbart"}), 200

    except Exception as e:                     # Fanger generelle feil
        logging.error(f"Feil ved oppdatering av vare {vnr}: {e}") # Logger feilen
                                               # Returnerer JSON-feilmelding, status 500
        return jsonify({"error": "Serverfeil ved oppdatering av vare"}), 500

# Slette en vare
@api_blueprint.route("/varer/<string:vnr>", methods=["DELETE"]) # Definerer route for DELETE /api/varer/<varenummer>
def delete_vare(vnr):                          # Funksjon for å slette en vare
    try:                                       # Starter try-block
                                               # SQL-spørring for å slette varen
        query = "DELETE FROM vare WHERE VNr=%s"
                                               # Utfører spørringen
        success = db.execute_query(query, (vnr,))

        if success:                            # Sjekker om execute_query var vellykket
            logging.info(f"Sletteforespørsel for VNr {vnr} utført.") # Logger info
                                               # Returnerer tom respons, status 204 No Content (standard for DELETE)
            return '', 204
        else:                                  # Hvis execute_query feilet
            logging.warning(f"Databasefeil under sletting av VNr {vnr} (execute_query returnerte False).")
                                               # Returnerer JSON-feilmelding, status 500
            return jsonify({"error": "Kunne ikke slette vare (databasefeil)"}), 500

    except Exception as e:                     # Fanger generelle feil
        logging.error(f"Feil ved sletting av vare {vnr}: {e}") # Logger feilen
                                               # Returnerer JSON-feilmelding, status 500
        return jsonify({"error": "Serverfeil ved sletting av vare"}), 500

# --- Kunde- og Ordre-Endepunkter er fjernet i denne forenklede versjonen ---