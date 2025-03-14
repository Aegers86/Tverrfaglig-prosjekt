# queries.py
# Inneholder SQL-spørringer for prosjektet.

# Nøkkeltall-statistikk for hovedsiden
QUERY_STATS = """
    SELECT 
        (SELECT COUNT(*) FROM kunde),
        (SELECT COUNT(*) FROM ordre),
        (SELECT COUNT(*) FROM vare),
        (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NOT NULL),
        (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NULL)
"""

# Hent alle kunder (Bruker Stored Procedure)
QUERY_ALL_CUSTOMERS = "CALL hent_alle_kunder();"

# Hent alle varer
QUERY_ALL_PRODUCTS = """
    SELECT varenummer, betegnelse, pris, antall 
    FROM vare 
    ORDER BY betegnelse;
"""

# Hent alle ordrer
QUERY_ALL_ORDERS = """
    SELECT 
        o.ordrenummer, o.ordre_dato, o.dato_sendt, o.betalt_dato, 
        CONCAT(k.fornavn, ' ', k.etternavn) AS kundenavn
    FROM ordre o 
    JOIN kunde k ON o.kundenummer = k.knr
    ORDER BY o.ordre_dato DESC;
"""

# Hent en spesifikk ordre med varer
QUERY_ORDER_DETAILS = """
    SELECT 
        ol.ordreNr, ol.varenummer, v.betegnelse, ol.pris_pr_enhet, ol.antall
    FROM ordrelinje ol
    JOIN vare v ON ol.varenummer = v.varenummer
    WHERE ol.ordreNr = %s;
"""

# Hent en spesifikk kunde
QUERY_CUSTOMER_BY_ID = """
    SELECT knr, fornavn, etternavn, adresse, postnummer, epost 
    FROM kunde 
    WHERE knr = %s;
"""

# Legg til en ny kunde
QUERY_INSERT_CUSTOMER = """
    INSERT INTO kunde (fornavn, etternavn, adresse, postnummer, epost) 
    VALUES (%s, %s, %s, %s, %s);
"""

# Slett en kunde
QUERY_DELETE_CUSTOMER = "DELETE FROM kunde WHERE knr = %s;"

# Legg til en ny vare
QUERY_INSERT_PRODUCT = """
    INSERT INTO vare (betegnelse, pris, antall) 
    VALUES (%s, %s, %s);
"""

# Oppdater en vare
QUERY_UPDATE_PRODUCT = """
    UPDATE vare SET betegnelse = %s, pris = %s, antall = %s WHERE varenummer = %s;
"""

# Slett en vare
QUERY_DELETE_PRODUCT = "DELETE FROM vare WHERE varenummer = %s;"

# Hent varer med lav beholdning (f.eks. under 5)
QUERY_LOW_STOCK = """
    SELECT varenummer, betegnelse, pris, antall 
    FROM vare 
    WHERE antall < 5;
"""

# Hent varer som er utsolgt
QUERY_OUT_OF_STOCK = """
    SELECT varenummer, betegnelse, pris, antall 
    FROM vare 
    WHERE antall = 0;
"""

# Hent varer i en gitt prisklasse
QUERY_PRODUCTS_BY_PRICE_RANGE = """
    SELECT varenummer, betegnelse, pris, antall 
    FROM vare 
    WHERE pris BETWEEN %s AND %s;
"""

# Opprett fakturanummer og lagre i databasen
QUERY_CREATE_INVOICE = """
    INSERT INTO faktura (ordreNr, faktura_dato, totalbeløp) 
    VALUES (%s, NOW(), %s);
"""

# Hent faktura for en spesifikk ordre
QUERY_INVOICE_DETAILS = """
    SELECT f.fakturaNr, f.faktura_dato, f.totalbeløp, o.ordrenummer
    FROM faktura f
    JOIN ordre o ON f.ordreNr = o.ordrenummer
    WHERE o.ordrenummer = %s;
"""

# Hent alle fakturaer for en spesifikk kunde
TABLES = {
    "vare": """
        CREATE TABLE IF NOT EXISTS vare (
            varenummer INT AUTO_INCREMENT PRIMARY KEY,
            betegnelse VARCHAR(255) NOT NULL,
            pris DECIMAL(10,2) NOT NULL,
            antall INT NOT NULL DEFAULT 0
        )
    """,

    "kunde": """
        CREATE TABLE IF NOT EXISTS kunde (
            knr INT AUTO_INCREMENT PRIMARY KEY,
            fornavn VARCHAR(255) NOT NULL,
            etternavn VARCHAR(255) NOT NULL,
            adresse VARCHAR(255) NOT NULL,
            postnummer INT NOT NULL
        )
    """,

    "ordre": """
        CREATE TABLE IF NOT EXISTS ordre (
            ordrenummer INT AUTO_INCREMENT PRIMARY KEY,
            ordre_dato DATE NOT NULL,
            dato_sendt DATE NULL,
            betalt_dato DATE NULL,
            kundenummer INT NOT NULL,
            FOREIGN KEY (kundenummer) REFERENCES kunde(knr) ON DELETE CASCADE
        )
    """,

    "ordrelinje": """
        CREATE TABLE IF NOT EXISTS ordrelinje (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ordreNr INT NOT NULL,
            varenummer INT NOT NULL,
            pris_pr_enhet DECIMAL(10,2) NOT NULL,
            antall INT NOT NULL,
            FOREIGN KEY (ordreNr) REFERENCES ordre(ordrenummer) ON DELETE CASCADE,
            FOREIGN KEY (varenummer) REFERENCES vare(varenummer) ON DELETE CASCADE
        )
    """
}