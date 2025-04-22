# handlers/database_handler.py
# Alle kall mot Database (wrapper rundt database_program.py)

from database.database_program import Database
import logging

class DatabaseHandler:
    def __init__(self):
        self.db = Database()

    def kall_prosedyre(self, navn, parametre=()):
        try:
            return self.db.call_procedure(navn, parametre)
        except Exception as e:
            logging.exception(f"Feil ved kall_prosedyre {navn}")
            raise e

    def hent_alle(self, spørring, parametre=()):
        try:
            return self.db.fetch_all(spørring, parametre)
        except Exception as e:
            logging.exception(f"Feil ved hent_alle: {spørring}")
            raise e

    def hent_en(self, spørring, parametre=()):
        try:
            return self.db.fetch_one(spørring, parametre)
        except Exception as e:
            logging.exception(f"Feil ved hent_en: {spørring}")
            raise e

    def sett_inn_kunde(self, fornavn, etternavn, adresse, postnr, telefon, epost):
        try:
            spørring = """
            INSERT INTO kunde (Fornavn, Etternavn, Adresse, PostNr, Telefon, Epost, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1);
            """
            self.db.execute(spørring, (fornavn, etternavn, adresse, postnr, telefon, epost))
        except Exception as e:
            logging.exception("Feil ved sett_inn_kunde")
            raise e

    def oppdater_kunde(self, knr, fornavn, etternavn, adresse, postnr, telefon, epost):
        try:
            spørring = """
            UPDATE kunde
            SET Fornavn = %s, Etternavn = %s, Adresse = %s, PostNr = %s, Telefon = %s, Epost = %s
            WHERE KNr = %s;
            """
            self.db.execute(spørring, (fornavn, etternavn, adresse, postnr, telefon, epost, knr))
        except Exception as e:
            logging.exception("Feil ved oppdater_kunde")
            raise e