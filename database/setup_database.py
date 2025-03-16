# setup_database.py
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database credentials from .env file
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # Convert port to integer

# Connect to MySQL Server (without selecting a database)
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    passwd=DB_PASSWORD,
    port=DB_PORT
)
cursor = conn.cursor()

# Create database if it does not exist
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")

# ✅ Ensure 'kunde' table exists before altering it
cursor.execute("""
    CREATE TABLE IF NOT EXISTS kunde (
        knr INT AUTO_INCREMENT PRIMARY KEY,
        fornavn VARCHAR(255) NOT NULL,
        etternavn VARCHAR(255) NOT NULL,
        adresse VARCHAR(255) NOT NULL,
        postnummer INT NOT NULL,
        epost VARCHAR(255) UNIQUE NOT NULL
    )
""")

# ✅ Check if 'epost' column exists, if not, add it
cursor.execute("SHOW COLUMNS FROM kunde LIKE 'epost'")
if cursor.fetchone() is None:
    print("🔄 Adding missing 'epost' column to kunde table...")
    cursor.execute("ALTER TABLE kunde ADD COLUMN epost VARCHAR(255) UNIQUE NULL AFTER postnummer")
    conn.commit()
    print("✅ 'epost' column added (NULL allowed temporarily)")

# ✅ Ensure all existing customers have an email (avoid duplicates)
cursor.execute("SELECT knr, fornavn FROM kunde WHERE epost IS NULL OR epost = ''")
customers_without_email = cursor.fetchall()

if customers_without_email:
    print(f"🔄 Updating {len(customers_without_email)} customers with missing emails...")
    for knr, fornavn in customers_without_email:
        fake_email = f"{fornavn.lower()}_{knr}@example.com"
        cursor.execute("UPDATE kunde SET epost = %s WHERE knr = %s", (fake_email, knr))

    conn.commit()
    print("✅ All customers now have valid emails.")

# ✅ Enforce NOT NULL constraint only AFTER filling missing values
cursor.execute("ALTER TABLE kunde MODIFY COLUMN epost VARCHAR(255) UNIQUE NOT NULL")
conn.commit()

# ✅ Ensure `hent_alle_kunder()` stored procedure exists
cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s AND Name = 'hent_alle_kunder'", (DB_NAME,))
if not cursor.fetchone():
    print("🔄 Creating missing stored procedure 'hent_alle_kunder'...")
    cursor.execute("""
        DELIMITER //
        CREATE PROCEDURE hent_alle_kunder()
        BEGIN
            SELECT knr, fornavn, etternavn, adresse, postnummer, epost FROM kunde;
        END //
        DELIMITER ;
    """)
    conn.commit()
    print("✅ Stored procedure 'hent_alle_kunder' created!")

# Create 'vare' table (products table)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS vare (
        varenummer INT AUTO_INCREMENT PRIMARY KEY,
        betegnelse VARCHAR(255) NOT NULL,
        pris DECIMAL(10,2) NOT NULL,
        antall INT NOT NULL DEFAULT 0
    )
""")

# Create 'ordre' table (orders table)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ordre (
        ordrenummer INT AUTO_INCREMENT PRIMARY KEY,
        ordre_dato DATE NOT NULL,
        dato_sendt DATE NULL,
        betalt_dato DATE NULL,
        kundenummer INT NOT NULL,
        FOREIGN KEY (kundenummer) REFERENCES kunde(knr) ON DELETE CASCADE
    )
""")

# Create 'ordrelinje' table (order items table)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ordrelinje (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ordreNr INT NOT NULL,
        varenummer INT NOT NULL,
        pris_pr_enhet DECIMAL(10,2) NOT NULL,
        antall INT NOT NULL,
        FOREIGN KEY (ordreNr) REFERENCES ordre(ordrenummer) ON DELETE CASCADE,
        FOREIGN KEY (varenummer) REFERENCES vare(varenummer) ON DELETE CASCADE
    )
""")

# ✅ Insert sample data if the table is empty
cursor.execute("SELECT COUNT(*) FROM vare")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO vare (betegnelse, pris, antall) VALUES ('Laptop', 10000.00, 5)")
    cursor.execute("INSERT INTO vare (betegnelse, pris, antall) VALUES ('Mus', 299.00, 20)")

cursor.execute("SELECT COUNT(*) FROM kunde")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO kunde (fornavn, etternavn, adresse, postnummer, epost) VALUES ('Ola', 'Nordmann', 'Oslo Gate 1', 1234, 'ola@example.com')")
    cursor.execute("INSERT INTO kunde (fornavn, etternavn, adresse, postnummer, epost) VALUES ('Kari', 'Hansen', 'Bergen Vei 2', 4321, 'kari@example.com')")

conn.commit()
cursor.close()
conn.close()

print("✅ Database setup completed successfully!")
