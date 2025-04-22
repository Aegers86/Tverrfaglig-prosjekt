from database_program import Database
from dotenv import load_dotenv
import mysql.connector
import os

#Laster miljøvariabler fra .env-filen
load_dotenv()

#Henter databasekonfigurasjon fra miljøvariabler
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

class Database:
    def __init__(self):
        self.db = None

    #Koble til databasen
    def connect(self):
        self.db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME
        )

    def lag_faktura_databasen(self):
        #Oppretter faktura-tabellen i databasen.
        self.connect()
        cursor = self.db.cursor()

        #SQL-spørring for å opprette faktura-tabellen
        #Tabellen har kolonnene id, OrdreNr, KNr og dato.
        #id er en auto-increment primærnøkkel, OrdreNr og KNr er utenlandsk nøkkel som refererer til ordre og kunde-tabellene.
        #dato er en datetime-kolonne som får standardverdien til å være nåværende tidspunkt.
        #Tabellen opprettes kun hvis den ikke allerede eksisterer.

        create_table_query = """
        CREATE TABLE IF NOT EXISTS faktura (
            id INT AUTO_INCREMENT PRIMARY KEY,
            OrdreNr INT NOT NULL,
            KNr INT NOT NULL,
            dato DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (KNr) REFERENCES kunde(KNr),
            FOREIGN KEY (OrdreNr) REFERENCES ordre(OrdreNr)
        )
        """
        cursor.execute(create_table_query)
        self.db.commit()
        cursor.close()

    def oppdater_kunde(self):
        self.connect()
        cursor = self.db.cursor()
        #SQL-spørring for å oppdatere kunde-tabellen for å legge til en ny kolonne is_active.
        #Kolonnen is_active er av typen BOOLEAN og har standardverdien TRUE.
        create_table_query = """
        ALTER TABLE kunde
        ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE
        """
        cursor.execute(create_table_query)
        self.db.commit()
        cursor.close()

#oppdater stored procedure for å oppdatere kunde-tabellen
#SELECT * FROM varehusdb.kunde WHERE is_active = 1;

if __name__ == "__main__":
    #Lager en instans av Database-klassen og oppretter faktura-tabellen
    db_instance = Database()
    db_instance.lag_faktura_databasen()
    db_instance.oppdater_kunde()


