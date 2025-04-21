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
        create_table_query = """
        CREATE TABLE IF NOT EXISTS faktura (
            id INT AUTO_INCREMENT PRIMARY KEY,
            OrdreNr INT NOT NULL,
            KNr INT NOT NULL,
            dato DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (KNr) REFERENCES kunde(KNr) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (OrdreNr) REFERENCES ordre(OrdreNr) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
        cursor.execute(create_table_query)
        self.db.commit()
        cursor.close()


if __name__ == "__main__":
    #Lager en instans av Database-klassen og oppretter faktura-tabellen
    db_instance = Database()
    db_instance.lag_faktura_databasen()


