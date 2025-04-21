import mysql.connector
from dotenv import load_dotenv
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

    #Lukk tilkoblingen til databasen
    def close(self):
        if self.db:
            self.db.close()

    #Hent alle rader fra en spørring
    def fetch_all(self, query, params=None):
        self.connect()
        cursor = self.db.cursor()
        cursor.execute(query, params or ())
        data = cursor.fetchall()
        cursor.close()
        self.close()
        return data

    #Hent en enkelt rad fra en spørring
    def fetch_one(self, query, params=None):
        self.connect()
        cursor = self.db.cursor()
        cursor.execute(query, params or ())
        data = cursor.fetchone()
        cursor.close()
        self.close()
        return data
    
    #Hent resultatet av en lagret prosedyre
    def call_procedure(self, procedure, args=()):
        self.connect()
        cursor = self.db.cursor()
        cursor.callproc(procedure, args)
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        cursor.close()
        self.close()
        return results
    
    def insert_faktura(self, ordreNr, kNr):
        self.connect()
        cursor = self.db.cursor()
        insert_query = """
        INSERT INTO faktura (OrdreNr, KNr)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (ordreNr, kNr))
        self.db.commit()
        faktura_id = cursor.lastrowid
        cursor.close()
        self.close()
        return faktura_id
    
    def update_one(self, query, params):
        self.connect()
        cursor = self.db.cursor()
        cursor.execute(query, params)
        self.db.commit()
        cursor.close()
        self.close()

    def insert_kunde(self, Fornavn, Etternavn, Adresse, Postnr):
        self.connect()
        cursor = self.db.cursor()
        cursor.execute("SELECT MAX(KNr) FROM kunde")
        result = cursor.fetchone()
        max_kNr = result[0] if result[0] is not None else 0
        kNr = max_kNr + 1

        insert_query = """
        INSERT INTO kunde (KNr, Fornavn, Etternavn, Adresse, Postnr) VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (kNr, Fornavn, Etternavn, Adresse, Postnr))
        #print(f"Inserted Kunde with kNr: {kNr}")
        self.db.commit()
        cursor.close()
        self.close()