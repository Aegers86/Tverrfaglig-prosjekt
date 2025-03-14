# populate_database.py
# A script to populate the MySQL database with realistic dummy data.
import mysql.connector
from dotenv import load_dotenv
import os
import random
from faker import Faker

# Load environment variables
load_dotenv()

# Retrieve database credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Ensure the port is an integer

# Initialize Faker for generating realistic names and addresses
fake = Faker("no_NO")  # Use Norwegian locale

# List of Norwegian tech-related products
product_list = [
    "Bærbar PC", "Stasjonær PC", "Skjerm", "Tastatur", "Gaming mus",
    "SSD-disk", "Ekstern harddisk", "Høyttalere", "Webkamera", "Router",
    "Nettverkskabel", "Grafikkort", "Hovedkort", "Prosessor", "RAM-modul"
]

def purge_database(cursor):
    """Deletes existing data from tables and resets AUTO_INCREMENT."""
    print("🗑 Purging database...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # Temporarily disable foreign key checks
    tables = ["ordrelinje", "ordre", "kunde", "vare"]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")
        cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")  # Reset AUTO_INCREMENT
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Re-enable foreign key checks
    print("✅ Database purged successfully.")

def populate_database():
    """Purges database and inserts new, more realistic test data."""
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Purge existing data
        purge_database(cursor)

        ### ✅ Insert realistic products into `vare` ###
        print("📦 Inserting realistic Norwegian tech products...")
        for _ in range(20):  # Limit to 20 products
            product_name = random.choice(product_list)  # Select a Norwegian product
            price = round(random.uniform(500, 25000), 2)  # Price between 500 and 25000
            stock = random.randint(5, 50)  # Stock between 5 and 50 (realistic for stores)
            cursor.execute("INSERT INTO vare (betegnelse, pris, antall) VALUES (%s, %s, %s)", (product_name, price, stock))

        ### ✅ Insert 10 realistic customers into `kunde` ###
        print("👤 Inserting exactly 10 customers...")
        customer_ids = []
        for i in range(1, 11):  # Limit customer IDs from 1 to 10
            first_name = fake.first_name()
            last_name = fake.last_name()
            address = fake.street_address()
            postal_code = fake.postcode()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"  # Generate a fake email

            cursor.execute(
                "INSERT INTO kunde (knr, fornavn, etternavn, adresse, postnummer, epost) VALUES (%s, %s, %s, %s, %s, %s)",
                (i, first_name, last_name, address, postal_code, email)
            )  # Force customer IDs 1-10
            customer_ids.append(i)

        conn.commit()  # Ensure customers exist before inserting orders

        ### ✅ Insert realistic orders into `ordre` ###
        print("📑 Inserting realistic orders...")
        order_ids = []
        for _ in range(15):  # Limit to 15 orders
            order_date = fake.date_between(start_date="-6m", end_date="today")  # Orders from the past 6 months
            ship_date = fake.date_between(start_date=order_date, end_date="today")
            paid_date = fake.date_between(start_date=order_date, end_date=ship_date) if random.random() > 0.7 else None
            customer_id = random.choice(customer_ids)  # Only choose from the 10 valid customers
            cursor.execute("INSERT INTO ordre (ordre_dato, dato_sendt, betalt_dato, kundenummer) VALUES (%s, %s, %s, %s)",
                           (order_date, ship_date, paid_date, customer_id))
            order_ids.append(cursor.lastrowid)

        conn.commit()  # Ensure orders exist before inserting order lines

        ### ✅ Insert realistic order lines into `ordrelinje` ###
        print("🛒 Inserting realistic order lines...")
        cursor.execute("SELECT varenummer, pris, betegnelse FROM vare")  # Get all product IDs with prices
        products = cursor.fetchall()  # List of tuples (varenummer, pris, betegnelse)

        for order_id in order_ids:
            num_items = random.randint(1, 3)  # Each order has 1-3 products
            for _ in range(num_items):
                product = random.choice(products)
                product_id, price, name = product  # Extract ID, price, and name
                quantity = random.randint(1, 5)  # Quantity between 1 and 5 (realistic)
                cursor.execute("INSERT INTO ordrelinje (ordreNr, varenummer, pris_pr_enhet, antall) VALUES (%s, %s, %s, %s)",
                               (order_id, product_id, price, quantity))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Realistic Norwegian dummy data successfully inserted!")

    except mysql.connector.Error as err:
        print(f"⚠ Database Error: {err}")

# Run the function
if __name__ == "__main__":
    populate_database()
