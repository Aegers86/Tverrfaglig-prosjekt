# api.py
# API for varelagerstyring (Flask)
from flask import Blueprint, request, jsonify
from database.database import Database # Antar denne er korrekt satt opp med dictionary=True
import logging
import mysql.connector # Brukes for å fange spesifikke DB-feil som Duplicate entry
import decimal # Brukes for å konvertere Decimal fra DB til JSON-vennlig format

# Opprett Blueprint for API
api_blueprint = Blueprint("api", __name__)
db = Database() # Initialiser database-objektet

# Logging konfigureres vanligvis sentralt i app.py, men kan settes her om nødvendig
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Hjelpefunksjoner ---
def convert_decimals(data):
    """Konverterer rekursivt Decimal-objekter til float for JSON-serialisering."""
    if isinstance(data, list):
        # Gå gjennom hvert element i listen
        return [convert_decimals(item) for item in data]
    if isinstance(data, dict):
        # Gå gjennom nøkkel/verdi-par i ordboken
        new_dict = {}
        for key, value in data.items():
            if isinstance(value, decimal.Decimal):
                new_dict[key] = float(value) # Konverter Decimal til float
            else:
                new_dict[key] = convert_decimals(value) # Kall rekursivt for nestede strukturer
        return new_dict
    # Returner uendret hvis det ikke er liste, ordbok eller Decimal
    return data

# --- Vare-Endepunkter ---

# Hente alle varer
@api_blueprint.route("/varer", methods=["GET"])
def get_varer():
    try:
        # Bruker korrekte kolonnenavn fra varehusdb.sql
        varer = db.fetch_all("SELECT VNr, Betegnelse, Pris, Antall FROM vare ORDER BY Betegnelse")
        # Konverter Decimal før JSON-respons
        varer = convert_decimals(varer)
        # Returnerer liste (kan være tom) med 200 OK
        return jsonify(varer or []), 200
    except Exception as e:
        logging.error(f"Feil ved henting av varer: {e}")
        return jsonify({"error": "Kunne ikke hente varer"}), 500

# Hente en spesifikk vare
# Bruker <string:vnr> for å matche VNr CHAR(5)
@api_blueprint.route("/varer/<string:vnr>", methods=["GET"])
def get_vare(vnr):
    try:
        # Bruker korrekt kolonnenavn VNr
        # Velger spesifikke kolonner for klarhet
        vare = db.fetch_one("SELECT VNr, Betegnelse, Pris, Antall, KatNr, Hylle FROM vare WHERE VNr = %s", (vnr,))
        if not vare:
            # Varen finnes ikke -> 404
            logging.warning(f"Vare med VNr {vnr} ikke funnet")
            return jsonify({"error": "Varen finnes ikke"}), 404
        # Konverter Decimal før JSON-respons
        vare = convert_decimals(vare)
        return jsonify(vare), 200
    except Exception as e:
        logging.error(f"Feil ved henting av vare {vnr}: {e}")
        return jsonify({"error": "Kunne ikke hente varen"}), 500

# Legge til en ny vare
@api_blueprint.route("/varer", methods=["POST"])
def add_vare():
    data = None # Initialiser data for sikker bruk i except-blokk
    try:
        data = request.get_json()
        # Krever VNr i tillegg (må sendes fra frontend)
        required_fields = ["vnr", "betegnelse", "pris", "antall"]
        if not data or not all(field in data and data[field] is not None for field in required_fields):
            logging.warning(f"Manglende data ved forsøk på å legge til vare. Fikk: {data}. Krever: {required_fields}")
            return jsonify({"error": "Ugyldig inndata", "required": required_fields}), 400

        # Bruker korrekte kolonnenavn og inkluderer VNr
        query = "INSERT INTO vare (VNr, Betegnelse, Pris, Antall) VALUES (%s, %s, %s, %s)"
        success = db.execute_query(query, (data["vnr"], data["betegnelse"], data["pris"], data["antall"]))

        if not success:
            # Anta databasefeil siden execute_query returnerte False (bør egentlig kaste exception)
            logging.warning("db.execute_query returnerte False ved innsending av ny vare")
            return jsonify({"error": "Kunne ikke legge til vare (ukjent databasefeil)"}), 500

        # Hent den nye varen for å returnere den
        new_vare = db.fetch_one("SELECT VNr, Betegnelse, Pris, Antall FROM vare WHERE VNr = %s", (data["vnr"],))
        new_vare = convert_decimals(new_vare)
        return jsonify(new_vare or {"message": "Vare lagt til, men kunne ikke hentes umiddelbart"}), 201 # 201 Created

    except mysql.connector.Error as err: # Spesifikk databasefeil
        vnr_value = data.get('vnr', 'N/A') if data else 'N/A' # Sikker tilgang til data
        if err.errno == 1062: # Duplicate entry
            logging.warning(f"Forsøk på å legge til vare med eksisterende VNr: {vnr_value}")
            return jsonify({"error": f"Vare med VNr {vnr_value} finnes allerede"}), 409 # Conflict
        else:
            logging.error(f"Databasefeil ved oppretting av vare (VNr={vnr_value}): {err}")
            return jsonify({"error": "Databasefeil ved oppretting av vare"}), 500
    except Exception as e: # Andre feil (f.eks. JSON parsing)
        vnr_value = data.get('vnr', 'N/A') if data else 'N/A'
        logging.error(f"Generell feil ved oppretting av vare (VNr={vnr_value}): {e}")
        return jsonify({"error": "Serverfeil ved oppretting av vare"}), 500

# Oppdatere en vare
# Bruker <string:vnr> for å matche VNr CHAR(5)
@api_blueprint.route("/varer/<string:vnr>", methods=["PUT"])
def update_vare(vnr):
    try:
        data = request.get_json()
        # Valider at data finnes
        if not data:
            logging.warning(f"Manglende data ved oppdatering av vare {vnr}")
            return jsonify({"error": "Ugyldig inndata, ingen data mottatt"}), 400

        # Krever at nødvendige felter er med for oppdatering
        required_fields = ["betegnelse", "pris", "antall"]
        if not all(field in data for field in required_fields):
             logging.warning(f"Manglende data ved oppdatering av vare {vnr}. Fikk: {data}. Krever: {required_fields}")
             return jsonify({"error": "Ugyldig inndata", "required": required_fields}), 400

        # Bruker korrekte kolonnenavn
        query = "UPDATE vare SET Betegnelse=%s, Pris=%s, Antall=%s WHERE VNr=%s"
        success = db.execute_query(query, (data["betegnelse"], data["pris"], data["antall"], vnr))

        if not success:
             logging.warning(f"Kunne ikke oppdatere vare med VNr {vnr} (execute_query feilet)")
             # Sjekk om varen finnes før man returnerer 500?
             # test_vare = db.fetch_one("SELECT VNr FROM vare WHERE VNr=%s", (vnr,))
             # if not test_vare: return jsonify({"error": "Varen finnes ikke"}), 404
             return jsonify({"error": "Kunne ikke oppdatere vare (databasefeil)"}), 500

        # Returner den oppdaterte varen
        updated_vare = db.fetch_one("SELECT VNr, Betegnelse, Pris, Antall FROM vare WHERE VNr = %s", (vnr,))
        updated_vare = convert_decimals(updated_vare)
        return jsonify(updated_vare or {"message": "Vare oppdatert, men kunne ikke hentes umiddelbart"}), 200

    except Exception as e:
        logging.error(f"Feil ved oppdatering av vare {vnr}: {e}")
        return jsonify({"error": "Serverfeil ved oppdatering av vare"}), 500

# Slette en vare
# Bruker <string:vnr> for å matche VNr CHAR(5)
@api_blueprint.route("/varer/<string:vnr>", methods=["DELETE"])
def delete_vare(vnr):
    try:
        # Bruker korrekt kolonnenavn VNr
        query = "DELETE FROM vare WHERE VNr=%s"
        # Fjerner det ugyldige return_rowcount-argumentet
        success = db.execute_query(query, (vnr,))

        if success:
            # Returnerer 204 No Content ved suksess (ingen body)
            logging.info(f"Sletteforespørsel for VNr {vnr} utført.")
            return '', 204
        else:
            # execute_query returnerte False -> databasefeil
            logging.warning(f"Databasefeil under sletting av VNr {vnr} (execute_query returnerte False).")
            # Vi vet ikke om feilen skyldes at varen ikke fantes eller annen DB-feil.
            return jsonify({"error": "Kunne ikke slette vare (databasefeil)"}), 500

    except Exception as e:
        logging.error(f"Feil ved sletting av vare {vnr}: {e}")
        return jsonify({"error": "Serverfeil ved sletting av vare"}), 500

# --- Kunde-Endepunkter ---

# Hente alle kunder via Stored Procedure
@api_blueprint.route("/kunder", methods=["GET"])
def get_kunder():
    try:
        # Antar at Stored Procedure 'hent_alle_kunder' returnerer riktig format
        # og at database.py's call_procedure håndterer dictionary=True korrekt
        kunder = db.call_procedure("hent_alle_kunder")
        # Konverter eventuelle Decimal-verdier (hvis noen returneres)
        kunder = convert_decimals(kunder)
        return jsonify(kunder or []), 200
    except Exception as e:
        logging.error(f"Feil ved henting av kunder: {e}")
        return jsonify({"error": "Kunne ikke hente kunder"}), 500

# --- Ordre-Endepunkter ---

# Hente alle ordrer
@api_blueprint.route("/ordrer", methods=["GET"])
def get_ordrer():
    try:
        ordrer = db.fetch_all("""
            SELECT 
                o.OrdreNr, 
                o.OrdreDato, 
                o.SendtDato, 
                o.BetaltDato,
                CONCAT(k.Fornavn, ' ', k.Etternavn) AS Kundenavn
            FROM ordre o
            JOIN kunde k ON o.KNr = k.KNr
            ORDER BY o.OrdreDato DESC;
        """)
        ordrer = convert_decimals(ordrer)
        return jsonify(ordrer or []), 200
    except Exception as e:
        logging.error(f"Feil ved henting av ordrer: {e}")
        return jsonify({"error": "Kunne ikke hente ordrer"}), 500
