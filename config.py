# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Flask-konfigurasjon
FLASK_CONFIG = {
    "DEBUG": True,
    "HOST": os.getenv("FLASK_HOST", "127.0.0.1"),
    "PORT": int(os.getenv("FLASK_PORT", 5000)),
}

# Databasekonfigurasjon
DATABASE_CONFIG = {
    "NAME": os.getenv("DB_NAME"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "HOST": os.getenv("DB_HOST", "127.0.0.1"),
    "PORT": int(os.getenv("DB_PORT", 3306)),
}

# API-konfigurasjon
API_CONFIG = {
    "PREFIX": "/api",
    "VERSION": "v1",
    "SECRET_KEY": os.getenv("SECRET_KEY", "supersecretkey"),
}

# Logging-konfigurasjon
LOGGING_CONFIG = {
    "LOG_FILE": "app.log",
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
}

# Firma-informasjon for fakturaer
FIRMA_INFO = {
    "navn": "Gruppe 1",
    "adresse": "Gruppeveien 1",
    "postnummer": "1111",
    "sted": "Oslo",
    "orgnr": "111 111 111",
    "telefon": "22 22 22 22",
    "epost": "firma@epost.no"
}

# Kontrollflagg for database
DATABASE_FLAGS = {
    'is_active_added': True,
    'faktura_table_created': True,
}
