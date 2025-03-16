# populate_database.py
# Skript for å fylle MySQL-databasen med realistiske dummy-data
import mysql.connector
from dotenv import load_dotenv
import os
import random
import logging
from faker import Faker

# 🎯 Last inn miljøvariabler
load_dotenv()

# 🎯 Sett opp logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🎯 Databasekonfigurasjon
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# 🎯 Initialiser Faker for realistiske norske data
fake = Faker("no_NO")

# 🎯 Norske teknologiprodukter
product_list = [
    "Bærbar PC", "Stasjonær PC", "Skjerm", "Tastatur", "Gaming mus",
    "SSD-disk", "Ekstern harddisk", "Høyttalere", "Webkamera", "Router",
    "Nettverkskabel", "Grafikkort", "Hovedkort", "Prosessor", "RAM-modul"
]

def purge_database(cursor):
    """🗑 Sletter eksisterende data og nullstiller AUTO_INCREMENT."""
    logging.info("🗑 Rydder opp i databasen...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # Midlertidig slå av foreign key constraints
    tables = ["ordrelinje", "ordre", "kunde", "vare"]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")  # Slett alle rader i tabellen
        cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")  # Nullstill AUTO_INCREMENT
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Slå på foreign key constraints igjen
    logging.info("✅ Database tømt og nullstilt.")

def populate_database():
    """📌 Fyller databasen med realistiske testdata."""
    try:
        # 🎯 Koble til MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()
        logging.info("✅ Tilkoblet databasen.")

        # 🎯 Slett eksisterende data
        purge_database(cursor)

        ### ✅ Sett inn produkter i `vare` ###
        logging.info("📦 Setter inn 20 realistiske produkter...")
        for _ in range(20):
            product_name = random.choice(product_list)
            price = round(random.uniform(500, 25000), 2)  # Pris mellom 500 og 25 000
            stock = random.randint(5, 50)  # Antall mellom 5 og 50
            cursor.execute("INSERT INTO vare (betegnelse, pris, antall) VALUES (%s, %s, %s)", (product_name, price, stock))

        ### ✅ Sett inn kunder i `kunde` ###
        logging.info("👤 Setter inn 10 kunder...")
        customer_ids = []
        for i in range(1, 11):
            first_name = fake.first_name()
            last_name = fake.last_name()
            address = fake.street_address()
            postal_code = fake.postcode()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"

            cursor.execute(
                "INSERT INTO kunde (knr, fornavn, etternavn, adresse, postnummer, epost) VALUES (%s, %s, %s, %s, %s, %s)",
                (i, first_name, last_name, address, postal_code, email)
            )
            customer_ids.append(i)

        conn.commit()  # Lagre kunder før vi lager ordrer

        ### ✅ Sett inn ordrer i `ordre` ###
        logging.info("📑 Setter inn 15 ordrer...")
        order_ids = []
        for _ in range(15):
            order_date = fake.date_between(start_date="-6m", end_date="today")
            ship_date = fake.date_between(start_date=order_date, end_date="today")
            paid_date = fake.date_between(start_date=order_date, end_date=ship_date) if random.random() > 0.7 else None
            customer_id = random.choice(customer_ids)
            cursor.execute("INSERT INTO ordre (ordre_dato, dato_sendt, betalt_dato, kundenummer) VALUES (%s, %s, %s, %s)",
                           (order_date, ship_date, paid_date, customer_id))
            order_ids.append(cursor.lastrowid)

        conn.commit()  # Lagre ordrer før vi lager ordrelinjer

        ### ✅ Sett inn ordrelinjer i `ordrelinje` ###
        logging.info("🛒 Setter inn ordrelinjer...")
        cursor.execute("SELECT varenummer, pris FROM vare")  # Hent alle produkter
        products = cursor.fetchall()

        for order_id in order_ids:
            num_items = random.randint(1, 3)  # Hver ordre har 1-3 produkter
            for _ in range(num_items):
                product = random.choice(products)
                product_id, price = product
                quantity = random.randint(1, 5)  # Antall mellom 1 og 5
                cursor.execute("INSERT INTO ordrelinje (ordreNr, varenummer, pris_pr_enhet, antall) VALUES (%s, %s, %s, %s)",
                               (order_id, product_id, price, quantity))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("✅ Realistiske testdata satt inn!")

    except mysql.connector.Error as err:
        logging.error(f"⚠ Databasefeil: {err}")

# 🎯 Kjør funksjonen hvis scriptet kjøres direkte
if __name__ == "__main__":
    populate_database()
