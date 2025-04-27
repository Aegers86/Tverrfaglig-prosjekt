# database/database_checker.py
import mysql.connector
import os
from dotenv import load_dotenv
import logging
import config

# Laster miljøvariabler
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def _oppdater_config_flagg(flaggnavn, verdi):
    """Oppdaterer riktig flagg inne i DATABASE_FLAGS i config.py."""
    try:
        config_path = "config.py"

        with open(config_path, "r", encoding="utf-8") as fil:
            linjer = fil.readlines()

        ny_innhold = []
        inne_i_database_flags = False
        flagg_funnet = False

        for linje in linjer:
            if "DATABASE_FLAGS" in linje and "=" in linje:
                inne_i_database_flags = True
                ny_innhold.append(linje)
                continue

            if inne_i_database_flags:
                if "}" in linje:
                    inne_i_database_flags = False
                    ny_innhold.append(linje)
                    continue

                if f"'{flaggnavn}':" in linje or f'"{flaggnavn}":' in linje:
                    indent = " " * (len(linje) - len(linje.lstrip()))
                    ny_linje = f"{indent}'{flaggnavn}': {str(verdi)},\n"
                    ny_innhold.append(ny_linje)
                    flagg_funnet = True
                else:
                    ny_innhold.append(linje)
            else:
                ny_innhold.append(linje)

        if not flagg_funnet:
            print(f"⚠️ Fant ikke flagget '{flaggnavn}' i config.py. Ingen endring gjort.")
            return

        with open(config_path, "w", encoding="utf-8") as fil:
            fil.writelines(ny_innhold)

        print(f"✅ Oppdatert {flaggnavn} = {verdi} i config.py.")

    except Exception as e:
        logging.error(f"❌ Feil ved oppdatering av {flaggnavn} i config.py: {e}")
        print(f"⚠️ Feil under oppdatering av {flaggnavn} i config.py.")


def sjekk_og_opprett_is_active():
    if getattr(config, "DATABASE_FLAGS", {}).get("is_active_added", False):
        return

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM kunde LIKE 'is_active';")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE kunde ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
            conn.commit()
            print("✅ Kolonnen 'is_active' ble lagt til i kunde-tabellen.")
        else:
            print("ℹ️ Kolonnen 'is_active' finnes allerede.")

        # Oppdater config.py!
        _oppdater_config_flagg("is_active_added", True)

        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"❌ Feil ved sjekk/oppretting av is_active: {e}")
        raise

def sjekk_og_opprett_faktura_tabell():
    if getattr(config, "DATABASE_FLAGS", {}).get("faktura_table_created", False):
        return

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'faktura';")
        if cursor.fetchone() is None:
            cursor.execute("""
                CREATE TABLE faktura (
                    FakturaNr INT AUTO_INCREMENT PRIMARY KEY,
                    OrdreNr INT NOT NULL,
                    KNr INT NOT NULL,
                    FakturaDato TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (OrdreNr) REFERENCES ordre(OrdreNr),
                    FOREIGN KEY (KNr) REFERENCES kunde(KNr)
                );
            """)
            conn.commit()
            print("✅ Tabell 'faktura' ble opprettet.")
        else:
            print("ℹ️ Tabell 'faktura' finnes allerede.")

        # Oppdater config.py!
        _oppdater_config_flagg("faktura_table_created", True)

        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"❌ Feil ved sjekk/oppretting av faktura-tabell: {e}")
        raise
