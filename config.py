# config.py
# En fil som inneholder konfigurasjoner for GUI-applikasjonen
# Definer kolonnebredder for tabeller
COLUMN_WIDTHS = {
    "Ordrenummer": 100,
    "Ordre dato": 120,
    "Dato sendt": 120,
    "Betalt Dato": 120,
    "Kundenavn": 200,
    "Varenummer": 100,
    "Betegnelse": 200,
    "Pris": 100,
    "Antall": 100,
    "KundeNr": 80,
    "Fornavn": 120,
    "Etternavn": 120,
    "Adresse": 200,
    "PostNr": 80,
    "Epost": 200,
}

# Definer farger for Light Mode og Dark Mode
THEME_COLORS = {
    "light": {
        "bg": "#EAEAEA",
        "fg": "#000000",
        "sidebar": "#E0E0E0",
        "button_bg": "#E0E0E0",
        "button_fg": "#000000",
    },
    "dark": {
        "bg": "#333333",
        "fg": "#FFFFFF",
        "sidebar": "#444444",
        "button_bg": "#555555",
        "button_fg": "#FFFFFF",
    },
}

# SQL Queries for å hente nøkkeltall
QUERY_STATS = """
    SELECT 
        (SELECT COUNT(*) FROM kunde),
        (SELECT COUNT(*) FROM ordre),
        (SELECT COUNT(*) FROM vare),
        (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NOT NULL),
        (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NULL)
"""
