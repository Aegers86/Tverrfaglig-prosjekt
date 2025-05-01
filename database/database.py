# database.py
# Databasehåndtering med MySQL
# ----------------------------------------------
# Denne klassen håndterer tilkobling til MySQL-databasen,
# utfører spørringer på en sikker måte og sikrer SQL-injection-beskyttelse.

import mysql.connector
from dotenv import load_dotenv
import os
from logs.logs import log_info, log_error
from .queries import TABLES

# Last inn miljøvariabler fra .env
load_dotenv()

# Databasekonfigurasjon
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Standard MySQL-port er 3306


class Database:
    """Håndterer tilkobling og spørringer mot MySQL-databasen."""

    def __init__(self):
        """Initialiserer databasen uten umiddelbar tilkobling."""
        self.db = None

    def connect(self):
        """Etablerer en tilkobling til databasen."""
        try:
            self.db = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT
            )
            log_info("Tilkobling til databasen vellykket.")
        except mysql.connector.Error as err:
            log_error(f"⚠ Database Connection Error: {err}")
            self.db = None

    def close(self):
        """Lukker databasen om den er åpen."""
        if self.db:
            self.db.close()
            log_info("🔌 Databaseforbindelse lukket.")

    def fetch_all(self, query, params=()):
        """Utfører en SELECT-spørring og returnerer alle rader som en liste av ordbøker."""
        self.connect()
        if not self.db:
            return []

        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results  # 🔹 Returnerer riktig struktur
        except mysql.connector.Error as err:
            log_error(f"⚠ Database Query Error (fetch_all): {err}")
            return []
        finally:
            self.close()

    def fetch_one(self, query, params=()):
        """Utfører en SELECT-spørring og returnerer én rad."""
        self.connect()
        if not self.db:
            return None

        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
        except mysql.connector.Error as err:
            log_error(f"⚠ Database Query Error (fetch_one): {err}")
            return None
        finally:
            self.close()

    def execute_query(self, query, params=()):
        """Utfører en INSERT, UPDATE eller DELETE-spørring."""
        self.connect()
        if not self.db:
            return False

        try:
            with self.db.cursor() as cursor:
                cursor.execute(query, params)
                self.db.commit()
                return True
        except mysql.connector.Error as err:
            log_error(f"⚠ Database Query Error (execute_query): {err}")
            self.db.rollback()  # Tilbakestill transaksjonen
            return False
        finally:
            self.close()

    def call_procedure(self, procedure, args=()):
        """Kaller en lagret prosedyre og returnerer resultater."""
        self.connect()
        if not self.db:
            return []

        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.callproc(procedure, args)
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
        except mysql.connector.Error as err:
            log_error(f"⚠ Stored Procedure Error: {err}")
            return []
        finally:
            self.close()

    def check_and_create_tables(self):
        """Sjekker om tabeller eksisterer og oppretter dem hvis de ikke finnes."""
        self.connect()
        if not self.db:
            log_error("⚠ Kunne ikke opprette databaseforbindelse.")
            return

        try:
            with self.db.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
                cursor.execute(f"USE {DB_NAME};")

                for table_name, table_sql in TABLES.items():
                    cursor.execute(table_sql)
                    log_info(f"Tabell sjekket/opprettet: {table_name}")

                self.db.commit()
                log_info("Alle nødvendige tabeller er sjekket og opprettet.")
        except mysql.connector.Error as err:
            log_error(f"⚠ Feil under oppretting av tabeller: {err}")
        finally:
            self.close()


# Kjør databaseoppsett hvis filen kjøres direkte
if __name__ == "__main__":
    db = Database()
    db.check_and_create_tables()
