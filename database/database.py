# database/database.py
# Databasehåndtering med MySQL
# ----------------------------------------------
# Denne klassen håndterer tilkobling til MySQL-databasen,
# utfører spørringer på en sikker måte og sikrer SQL-injection-beskyttelse.

import mysql.connector                           # Importerer MySQL Connector
from dotenv import load_dotenv                   # Importerer dotenv for å laste miljøvariabler
import os                                        # Importerer os for å hente miljøvariabler
import logging                                   # Importerer standard logging-modul

# Last inn miljøvariabler fra .env
load_dotenv()                                    # Laster variabler fra .env-filen

# Databasekonfigurasjon
# Henter databasekonfigurasjon fra miljøvariabler som er i .env-filen
DB_NAME = os.getenv("DB_NAME")                   # Henter databasenavn fra .env
DB_USER = os.getenv("DB_USER")                   # Henter databasebruker fra .env
DB_PASSWORD = os.getenv("DB_PASSWORD")           # Henter databasepassord fra .env
DB_HOST = os.getenv("DB_HOST")                   # Henter databasevert fra .env
DB_PORT = int(os.getenv("DB_PORT", 3306))       # Henter databaseport fra .env (standard 3306)


# Databasehåndtering med MySQL
class Database:

    # Initialiserer databasen
    def __init__(self):                          # Initialiserer databasen
        self.db = None                           # Setter db til None ved oppstart

    # Tilkobling til databasen
    def connect(self):                           # Kobler til databasen
        try:                                     # Prøver å koble til databasen
            self.db = mysql.connector.connect(   # Kobler til databasen med konfigurasjon fra miljøvariabler
                host=DB_HOST,                    # Vert for databasen
                user=DB_USER,                    # Brukernavn for databasen
                passwd=DB_PASSWORD,              # Passord for databasen
                database=DB_NAME,                # Navn på databasen
                port=DB_PORT                     # Port for databasen
            )
            # Bruker standard logging for info
            logging.info("Tilkobling til databasen vellykket.") # Logger at tilkoblingen er vellykket
        except mysql.connector.Error as err:     # Håndterer eventuelle feil ved tilkobling
            # Bruker standard logging for feil
            logging.error(f"⚠ Database Connection Error: {err}") # Logger feilen
            self.db = None                       # Setter db til None hvis tilkoblingen feiler

    # Lukker tilkoblingen til databasen
    def close(self):                             # Lukker tilkoblingen til databasen
        if self.db:                              # Sjekker om tilkoblingen eksisterer
            self.db.close()                      # Lukker tilkoblingen
            # Bruker standard logging for info
            logging.info("🔌 Databaseforbindelse lukket.") # Logger at tilkoblingen er lukket

    # Henter alle rader fra spørring
    def fetch_all(self, query, params=()):       # Henter alle rader fra spørring
        self.connect()                           # Kobler til databasen
        if not self.db:                          # Sjekker om tilkoblingen er vellykket
            return []                            # Returnerer tom liste hvis ikke

        try:
            # Bruker dictionary=True for å hente resultater som dictionary
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)    # Kjør spørringen med parametere
                results = cursor.fetchall()      # Henter alle rader fra resultatene
                return results                   # Returnerer resultatene (som liste av dicts)
        except mysql.connector.Error as err:     # Håndterer eventuelle feil
             # Bruker standard logging for feil
            logging.error(f"⚠ Database Query Error (fetch_all): {err}") # Logger feilen
            return []                            # Returnerer tom liste ved feil
        finally:                                 # Lukker tilkoblingen uansett hva
            self.close()                         # Tilkoblingen lukkes

    # Henter ein rad fra spørring
    def fetch_one(self, query, params=()):       # Henter en enkelt rad fra spørring
        self.connect()                           # Kobler til databasen
        if not self.db:                          # Sjekker om tilkoblingen er vellykket
            return None                          # Returnerer None hvis ikke

        try:                                     # Prøver å kjøre spørringen
            # Bruker dictionary=True for å hente resultater som dictionary
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)    # Kjør spørringen med parametere
                result = cursor.fetchone()       # Henter en enkelt rad fra resultatene
                return result                    # Returnerer resultatet (som dict eller None)
        except mysql.connector.Error as err:     # Håndterer eventuelle feil
             # Bruker standard logging for feil
            logging.error(f"⚠ Database Query Error (fetch_one): {err}") # Logger feilen
            return None                          # Returnerer None ved feil
        finally:                                 # Lukker tilkoblingen uansett hva
            self.close()                         # Tilkoblingen lukkes

    # Utfører spørring med parametere (INSERT, UPDATE, DELETE)
    def execute_query(self, query, params=()): # Utfører endringsspørringer
        self.connect()                           # Kobler til databasen
        if not self.db:                          # Sjekker om tilkoblingen er vellykket
            return False                         # Returnerer False hvis ikke

        try:                                     # Prøver å kjøre spørringen
            # Trenger ikke dictionary=True her, da vi ikke henter resultatsett
            with self.db.cursor() as cursor:
                cursor.execute(query, params)    # Kjør spørringen med parametere
                self.db.commit()                 # Bekreft endringer i databasen
                return True                      # Returnerer True ved suksess
        except mysql.connector.Error as err:     # Håndterer eventuelle feil
             # Bruker standard logging for feil
            logging.error(f"⚠ Database Query Error (execute_query): {err}") # Logger feilen
            self.db.rollback()                   # Tilbakestill transaksjonen ved feil
            return False                         # Returnerer False ved feil
        finally:                                 # Lukker tilkoblingen uansett hva
            self.close()                         # Tilkoblingen lukkes

    # Henter resultatet av en lagret prosedyre
    def call_procedure(self, procedure, args=()): # Kaller en lagret prosedyre
        self.connect()                           # Kobler til databasen
        if not self.db:                          # Sjekker om tilkoblingen er vellykket
            return []                            # Returnerer tom liste hvis ikke

        try:                                     # Prøver å kjøre lagret prosedyre
            # Bruker dictionary=True for å hente resultater som dictionary
            with self.db.cursor(dictionary=True) as cursor:
                cursor.callproc(procedure, args) # Kaller den lagrede prosedyren med argumenter
                results = []                     # Tom liste for å lagre resultatene
                # Går gjennom alle resultatsett returnert av prosedyren
                for result in cursor.stored_results():
                    results.extend(result.fetchall()) # Legger til radene fra hvert resultatsett
                return results                   # Returnerer samlet liste med resultater
        except mysql.connector.Error as err:     # Håndterer eventuelle feil
             # Bruker standard logging for feil
            logging.error(f"⚠ Stored Procedure Error: {err}") # Logger feilen
            return []                            # Returnerer tom liste ved feil
        finally:                                 # Til slutt lukkes tilkoblingen uansett hva
            self.close()                         # Tilkoblingen lukkes


# Kjør databaseoppsett hvis filen kjøres direkte
if __name__ == "__main__":                       # Sjekker om filen kjøres som hovedskript
    db = Database()                              # Oppretter en instans (kan brukes for testing)
