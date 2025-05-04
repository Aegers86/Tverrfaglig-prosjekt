# database/database.py
# Databasehåndtering med MySQL
# ----------------------------------------------
# Denne klassen håndterer tilkobling til MySQL-databasen,
# utfører spørringer på en sikker måte og sikrer SQL-injection-beskyttelse.

import mysql.connector
from dotenv import load_dotenv
import os

# Last inn miljøvariabler fra .env
load_dotenv()

# Databasekonfigurasjon
# Henter databasekonfigurasjon fra miljøvariabler som er i .env-filen
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Standard MySQL-port er 3306


# Databasehåndtering med MySQL
class Database:

    # Initialiserer databasen
    def __init__(self):                                                 # Initialiserer databasen
        self.db = None                                                  # Setter db til None ved oppstart

    # Tilkobling til databasen
    def connect(self):                                                  # Kobler til databasen
        try:                                                            # Prøver å koble til databasen
            self.db = mysql.connector.connect(                          # Kobler til databasen med konfigurasjon fra miljøvariabler
                host=DB_HOST,                                           # Vert for databasen
                user=DB_USER,                                           # Brukernavn for databasen
                passwd=DB_PASSWORD,                                     # Passord for databasen
                database=DB_NAME,                                       # Navn på databasen
                port=DB_PORT                                            # Port for databasen
            )

        except mysql.connector.Error as err:                            # Håndterer eventuelle feil ved tilkobling

            self.db = None                                              # Setter db til None hvis tilkoblingen feiler

    # Lukker tilkoblingen til databasen
    def close(self):                                                    # Lukker tilkoblingen til databasen
        if self.db:                                                     # Sjekker om tilkoblingen eksisterer
            self.db.close()                                             # Lukker tilkoblingen


    # Henter alle rader fra spørring
    def fetch_all(self, query, params=()):                              # Henter alle rader fra spørring
        self.connect()                                                  # Kobler til databasen
        if not self.db:                                                 # Sjekker om tilkoblingen er vellykket
            return []                                                   # Returnerer tom liste hvis ikke

        try:
            with self.db.cursor(dictionary=True) as cursor:             # Bruker dictionary for å hente resultater som dictionary
                cursor.execute(query, params)                           # Kjør spørringen med parametere
                results = cursor.fetchall()                             # Henter alle rader fra resultatene
                return results                                          # Returnerer riktig struktur
        except mysql.connector.Error as err:                            # Håndterer eventuelle feil

            return []                                                   # Returnerer tom liste ved feil
        finally:                                                        # Lukker tilkoblingen uansett hva
            self.close()                                                # Tilkoblingen lukkes

    # Henter ein rad fra spørring
    def fetch_one(self, query, params=()):                              # Henter en enkelt rad fra spørring
        self.connect()                                                  # Kobler til databasen
        if not self.db:                                                 # Sjekker om tilkoblingen er vellykket
            return None                                                 # Returnerer None hvis ikke

        try:                                                            # Prøver å kjøre spørringen
            with self.db.cursor(dictionary=True) as cursor:             # Bruker cursor() for å hente resultater som dictionary
                cursor.execute(query, params)                           # Kjør spørringen med parametere
                result = cursor.fetchone()                              # Henter en enkelt rad fra resultatene
                return result                                           # Returnerer resultatet
        except mysql.connector.Error as err:                            # Håndterer eventuelle feil

            return None                                                 # Returnerer None ved feil
        finally:                                                        # Lukker tilkoblingen uansett hva
            self.close()                                                # Tilkoblingen lukkes

    # Utfører spørring med parametere
    def execute_query(self, query, params=()):
        self.connect()                                                  # Kobler til databasen
        if not self.db:                                                 # Sjekker om tilkoblingen er vellykket
            return False                                                # Returnerer False hvis ikke

        try:                                                            # Prøver å kjøre spørringen
            with self.db.cursor() as cursor:                            # Bruker cursor() for ikke-dictionary resultater
                cursor.execute(query, params)                           # Kjør spørringen med parametere
                self.db.commit()                                        # Bekreft endringer i databasen
                return True
        except mysql.connector.Error as err:                            # Håndterer eventuelle feil

            self.db.rollback()                                          # Tilbakestill transaksjonen
            return False                                                # Returnerer False ved feil
        finally:                                                        # Lukker tilkoblingen uansett hva
            self.close()

    # Henter resultatet av en lagret prosedyre
    def call_procedure(self, procedure, args=()):
        self.connect()                                                  # Kobler til databasen
        if not self.db:                                                 # Sjekker om tilkoblingen er vellykket
            return []                                                   # Returnerer tom liste hvis ikke

        try:                                                            # Prøver å kjøre lagret prosedyre
            with self.db.cursor(dictionary=True) as cursor:             # Bruker cursor() for å hente resultater som dictionary
                cursor.callproc(procedure, args)                        # Kaller den lagrede prosedyren med argumenter
                results = []                                            # Tom liste for å lagre resultatene
                for result in cursor.stored_results():                  # Går gjennom alle lagrede resultater
                    results.extend(result.fetchall())                   # Legger til resultatene i listen
                return results                                          # Returnerer resultatene
        except mysql.connector.Error as err:                            # Håndterer eventuelle feil

            return []                                                   # Returnerer tom liste ved feil
        finally:                                                        # Til slutt lukkes tilkoblingen uansett hva
            self.close()                                                # Tilkoblingen lukkes


# Kjør databaseoppsett hvis filen kjøres direkte
if __name__ == "__main__":
    db = Database()
