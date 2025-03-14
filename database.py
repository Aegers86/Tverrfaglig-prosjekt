# database.py
# En klasse som håndterer tilkobling til databasen og utføring av spørringer og lagrede prosedyrer
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve database credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Ensure the port is an integer

class Database:
    def __init__(self):
        self.db = None

    def connect(self):
        """Connects to MySQL and ensures the correct database is selected."""
        try:
            self.db = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                port=DB_PORT
            )
            cursor = self.db.cursor()
            # Ensure the database exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
            cursor.execute(f"USE {DB_NAME};")  # Select the correct database
            cursor.close()
        except mysql.connector.Error as err:
            print(f"⚠ Database Connection Error: {err}")
            self.db = None

    def close(self):
        """Closes the database connection."""
        if self.db:
            self.db.close()

    def fetch_all(self, query, params=()):
        """Executes a query and fetches all results."""
        self.connect()
        if self.db is None:
            return []
        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall()
            cursor.close()
            return data
        except mysql.connector.Error as err:
            print(f"⚠ Database Query Error: {err}")
            return []

    def fetch_one(self, query, params=()):
        """Executes a query and fetches a single row."""
        self.connect()
        if self.db is None:
            return None
        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            data = cursor.fetchone()
            cursor.close()
            if data is None:
                print(f"⚠ No results found for query: {query}")
            return data
        except mysql.connector.Error as err:
            print(f"⚠ Database Query Error: {err}")
            return None

    def execute_query(self, query, params=()):
        """Executes a query without returning data (for INSERT, UPDATE, DELETE)."""
        self.connect()
        if self.db is None:
            return False
        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            self.db.commit()
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"⚠ Database Query Error: {err}")
            return False

    def call_procedure(self, procedure, args=()):
        """Calls a stored procedure and fetches results."""
        self.connect()
        if self.db is None:
            return []
        try:
            cursor = self.db.cursor()
            cursor.callproc(procedure, args)
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            cursor.close()
            return results
        except mysql.connector.Error as err:
            print(f"⚠ Stored Procedure Error: {err}")
            return []

    def check_and_create_tables(self):
        """Ensures required tables exist and creates them if they don't."""
        self.connect()
        if self.db is None:
            print("⚠ Could not establish a database connection.")
            return

        cursor = self.db.cursor()

        # Create 'vare' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vare (
                varenummer INT AUTO_INCREMENT PRIMARY KEY,
                betegnelse VARCHAR(255) NOT NULL,
                pris DECIMAL(10,2) NOT NULL,
                antall INT NOT NULL DEFAULT 0
            )
        """)

        # Create 'kunde' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kunde (
                knr INT AUTO_INCREMENT PRIMARY KEY,
                fornavn VARCHAR(255) NOT NULL,
                etternavn VARCHAR(255) NOT NULL,
                adresse VARCHAR(255) NOT NULL,
                postnummer INT NOT NULL
            )
        """)

        # Create 'ordre' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordre (
                ordrenummer INT AUTO_INCREMENT PRIMARY KEY,
                ordre_dato DATE NOT NULL,
                dato_sendt DATE NULL,
                betalt_dato DATE NULL,
                kundenummer INT NOT NULL,
                FOREIGN KEY (kundenummer) REFERENCES kunde(knr)
            )
        """)

        # Create 'ordrelinje' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordrelinje (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ordreNr INT,
                varenummer INT,
                pris_pr_enhet DECIMAL(10,2),
                antall INT,
                FOREIGN KEY (ordreNr) REFERENCES ordre(ordrenummer),
                FOREIGN KEY (varenummer) REFERENCES vare(varenummer)
            )
        """)

        self.db.commit()
        cursor.close()
        self.close()
        print("✅ Database tables checked/created successfully.")

# Run this when the script is executed directly to ensure tables exist
if __name__ == "__main__":
    db = Database()
    db.check_and_create_tables()
