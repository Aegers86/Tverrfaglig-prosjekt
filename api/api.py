# api.py
# ✅ API for varelagerstyring (Flask)
from flask import Blueprint, request, jsonify
from database.database import Database
import logging

# Opprett Blueprint for API
api_blueprint = Blueprint("api", __name__)
db = Database()

# Sett opp logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# 🔹 Hente alle varer
@api_blueprint.route("/varer", methods=["GET"])
def get_varer():
    try:
        varer = db.fetch_all("SELECT varenummer, betegnelse, pris, antall FROM vare")
        if not varer:
            logging.warning("Ingen varer funnet i databasen")
            return jsonify({"error": "Ingen varer funnet"}), 404
        return jsonify(varer), 200
    except Exception as e:
        logging.error(f"Feil ved henting av varer: {e}")
        return jsonify({"error": "Kunne ikke hente varer"}), 500


# 🔹 Hente en spesifikk vare
@api_blueprint.route("/varer/<int:varenummer>", methods=["GET"])
def get_vare(varenummer):
    try:
        vare = db.fetch_one("SELECT * FROM vare WHERE varenummer = %s", (varenummer,))
        if not vare:
            logging.warning(f"Vare med varenummer {varenummer} ikke funnet")
            return jsonify({"error": "Varen finnes ikke"}), 404
        return jsonify(vare), 200
    except Exception as e:
        logging.error(f"Feil ved henting av vare {varenummer}: {e}")
        return jsonify({"error": "Kunne ikke hente varen"}), 500


# 🔹 Legge til en ny vare
@api_blueprint.route("/varer", methods=["POST"])
def add_vare():
    try:
        data = request.get_json()
        if not data or "betegnelse" not in data or "pris" not in data or "antall" not in data:
            logging.warning("Manglende data ved forsøk på å legge til vare")
            return jsonify({"error": "Ugyldig inndata"}), 400

        query = "INSERT INTO vare (betegnelse, pris, antall) VALUES (%s, %s, %s)"
        success = db.execute_query(query, (data["betegnelse"], data["pris"], data["antall"]))

        if not success:
            logging.warning("Feil ved innsending av ny vare")
            return jsonify({"error": "Kunne ikke legge til vare"}), 500

        return jsonify({"success": True}), 201
    except Exception as e:
        logging.error(f"Feil ved oppretting av vare: {e}")
        return jsonify({"error": "Kunne ikke legge til vare"}), 500


# 🔹 Oppdatere en vare
@api_blueprint.route("/varer/<int:varenummer>", methods=["PUT"])
def update_vare(varenummer):
    try:
        data = request.get_json()
        if not data:
            logging.warning("Manglende data ved oppdatering av vare")
            return jsonify({"error": "Ugyldig inndata"}), 400

        query = "UPDATE vare SET betegnelse=%s, pris=%s, antall=%s WHERE varenummer=%s"
        success = db.execute_query(query, (data["betegnelse"], data["pris"], data["antall"], varenummer))

        return jsonify({"success": success}), 200 if success else 500
    except Exception as e:
        logging.error(f"Feil ved oppdatering av vare {varenummer}: {e}")
        return jsonify({"error": "Kunne ikke oppdatere vare"}), 500


# 🔹 Slette en vare
@api_blueprint.route("/varer/<int:varenummer>", methods=["DELETE"])
def delete_vare(varenummer):
    try:
        query = "DELETE FROM vare WHERE varenummer=%s"
        success = db.execute_query(query, (varenummer,))

        return jsonify({"success": success}), 200 if success else 500
    except Exception as e:
        logging.error(f"Feil ved sletting av vare {varenummer}: {e}")
        return jsonify({"error": "Kunne ikke slette vare"}), 500


# 🔹 Hente alle kunder via Stored Procedure
@api_blueprint.route("/kunder", methods=["GET"])
def get_kunder():
    try:
        kunder = db.call_procedure("hent_alle_kunder")
        if not kunder:
            logging.warning("Ingen kunder funnet i databasen")
            return jsonify({"error": "Ingen kunder funnet"}), 404
        return jsonify(kunder), 200
    except Exception as e:
        logging.error(f"Feil ved henting av kunder: {e}")
        return jsonify({"error": "Kunne ikke hente kunder"}), 500


# 🔹 Hente alle ordrer
@api_blueprint.route("/ordrer", methods=["GET"])
def get_ordrer():
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
        if not ordrer:
            logging.warning("Ingen ordrer funnet i databasen")
            return jsonify({"error": "Ingen ordrer funnet"}), 404
        return jsonify(ordrer), 200
    except Exception as e:
        logging.error(f"Feil ved henting av ordrer: {e}")
        return jsonify({"error": "Kunne ikke hente ordrer"}), 500
