# handlers/database_handler.py
# -*- coding: utf-8 -*-

# Sørg for korrekt import av din Database-klasse
try:
    from database.database import Database
except ImportError as e: raise ImportError(f"Kunne ikke importere Database-klassen. Sjekk filplassering. Feil: {e}")
import logging
from decimal import Decimal, InvalidOperation # Trengs for lagre_ny_ordre også

class DatabaseHandler:
    def __init__(self):
        """ Initialiserer DatabaseHandler og database-tilkoblingen. """
        try:
            self.db = Database() # Antar Database() håndterer tilkoblingsdetaljer
            logging.info("DatabaseHandler initialisert og tilkobling opprettet.")
            # Valgfri sjekk for nødvendige metoder i den underliggende DB-klassen
            required_db_methods = ['fetch_all', 'fetch_one', 'execute', 'call_procedure',
                                'start_transaction', 'commit', 'rollback', 'get_last_row_id']
            missing = [m for m in required_db_methods if not hasattr(self.db, m) or not callable(getattr(self.db, m))]
            if missing:
                logging.warning(f"Database-klassen ser ut til å mangle metoder: {', '.join(missing)}")
        except Exception as e:
            logging.critical(f"FEIL: Kunne ikke initialisere Database i DatabaseHandler: {e}", exc_info=True)
            raise ConnectionError(f"Database-init feilet: {e}") from e

    def kall_prosedyre(self, navn, parametre=()):
        """ Kaller en lagret prosedyre. """
        try:
            logging.debug(f"Kaller prosedyre: {navn} med params: {parametre}")
            result = self.db.call_procedure(navn, parametre)
            logging.debug(f"Resultat fra prosedyre {navn}: {len(result) if result else 0} rader")
            return result
        except Exception as e:
            logging.exception(f"Feil ved kall_prosedyre {navn}")
            raise RuntimeError(f"Databasefeil under kall til prosedyre '{navn}': {e}") from e

    def hent_alle(self, spørring, parametre=()):
        """ Henter alle rader som matcher spørringen. """
        try:
            logging.debug(f"Utfører hent_alle: {spørring} med params: {parametre}")
            result = self.db.fetch_all(spørring, parametre)
            logging.debug(f"Resultat fra hent_alle: {len(result) if result else 0} rader")
            return result
        except Exception as e:
            logging.exception(f"Feil ved hent_alle: {spørring}")
            raise RuntimeError(f"Databasefeil under hent_alle: {e}") from e

    def hent_en(self, spørring, parametre=()):
        """ Henter én rad som matcher spørringen. """
        try:
            logging.debug(f"Utfører hent_en: {spørring} med params: {parametre}")
            result = self.db.fetch_one(spørring, parametre)
            logging.debug(f"Resultat fra hent_en: {'Fant rad' if result else 'Ingen rad funnet'}")
            return result
        except Exception as e:
            logging.exception(f"Feil ved hent_en: {spørring}")
            raise RuntimeError(f"Databasefeil under hent_en: {e}") from e

    def execute_and_commit(self, spørring, parametre=()):
        """ Utfører en INSERT, UPDATE, DELETE og commiter.
            OBS: Bør kun brukes for enkle operasjoner som ikke krever transaksjon over flere steg.
        """
        logging.warning("execute_and_commit brukes. Vurder execute + commit/rollback separat.")
        try:
            logging.debug(f"Utfører execute_and_commit: {spørring} med params: {parametre}")
            rowcount = self.db.execute(spørring, parametre) # execute commiter ikke
            self.db.commit() # Manuell commit
            logging.info(f"execute_and_commit: {rowcount if rowcount is not None else 'ukjent'} rader påvirket for: {spørring[:50]}...")
            return rowcount
        except Exception as e:
            logging.exception(f"Feil under execute_and_commit for spørring: {spørring}")
            try: self.db.rollback() # Prøv rollback ved feil
            except Exception as rb_err: logging.error(f"Feil under rollback i execute_and_commit: {rb_err}")
            raise RuntimeError(f"Databasefeil under execute_and_commit: {e}") from e

    # --- Metoder for Kunde ---
    def sett_inn_kunde(self, fornavn, etternavn, adresse, postnr, telefon=None, epost=None, is_active=True):
        """ Setter inn en ny kunde, inkludert is_active-status. """
        try:
            spørring = """
                INSERT INTO kunde (Fornavn, Etternavn, Adresse, PostNr, is_active)
                VALUES (%s, %s, %s, %s, %s);
            """
            params = (fornavn, etternavn, adresse, postnr, int(is_active))
            logging.debug(f"Utfører sett_inn_kunde med params: {params}")
            rowcount = self.db.execute(spørring, params)
            self.db.commit()
            logging.info(f"Resultat fra sett_inn_kunde: {rowcount} rader påvirket.")
        except Exception as e:
            logging.exception("Feil ved sett_inn_kunde")
            try:
                self.db.rollback()
            except Exception as rb_err:
                logging.error(f"Feil under rollback i sett_inn_kunde: {rb_err}")
            raise RuntimeError(f"Databasefeil ved innsetting av kunde: {e}") from e

    def oppdater_kunde(self, knr, fornavn, etternavn, adresse, postnr, telefon=None, epost=None, is_active=True):
        """ Oppdaterer en eksisterende kunde inkludert is_active. """
        try:
            spørring = """
                UPDATE kunde
                SET Fornavn = %s, Etternavn = %s, Adresse = %s, PostNr = %s, is_active = %s
                WHERE KNr = %s;
            """
            params = (fornavn, etternavn, adresse, postnr, int(is_active), knr)
            logging.debug(f"Utfører oppdater_kunde for KNr {knr} med params: {params}")
            rowcount = self.db.execute(spørring, params)
            self.db.commit()
            logging.info(f"Resultat fra oppdater_kunde for KNr {knr}: {rowcount} rader påvirket.")
            return rowcount
        except Exception as e:
            logging.exception(f"Feil ved oppdater_kunde for KNr {knr}")
            try:
                self.db.rollback()
            except Exception as rb_err:
                logging.error(f"Feil under rollback i oppdater_kunde: {rb_err}")
            raise RuntimeError(f"Databasefeil ved oppdatering av kunde {knr}: {e}") from e

    def insert_faktura(self, ordre_nr, kunde_nr):
        """ Setter inn en faktura i databasen og returnerer faktura-ID. """
        try:
            spørring = """
                INSERT INTO faktura (OrdreNr, KNr)
                VALUES (%s, %s);
            """
            params = (ordre_nr, kunde_nr)
            logging.debug(f"Setter inn faktura for OrdreNr {ordre_nr}, KNr {kunde_nr}")

            rowcount = self.db.execute(spørring, params)
            if rowcount != 1:
                raise RuntimeError("Ingen faktura ble opprettet i databasen.")
            faktura_id = self.db.get_last_row_id()

            if not faktura_id:
                raise RuntimeError("Klarte ikke hente faktura ID etter insert.")

            self.db.commit()
            logging.info(f"Faktura satt inn med ID: {faktura_id}")
            return faktura_id

        except Exception as e:
            logging.error(f"Feil ved insert_faktura: {e}", exc_info=True)

            # --- FANG FEIL HVIS TABELL MANGLER ---
            if "Table 'varehusdb.faktura' doesn't exist" in str(e) or "1146" in str(e):
                logging.warning("Tabellen 'faktura' manglet. Oppretter tabellen...")
                self._opprett_faktura_tabell()

                # ➡ Prøv en gang til etter å ha laget tabellen:
                try:
                    rowcount = self.db.execute(spørring, params)
                    if rowcount != 1:
                        raise RuntimeError("Ingen faktura ble opprettet i databasen etter tabelloppretting.")
                    faktura_id = self.db.get_last_row_id()
                    if not faktura_id:
                        raise RuntimeError("Klarte ikke hente faktura ID etter insert etter tabelloppretting.")
                    self.db.commit()
                    logging.info(f"Faktura satt inn med ID: {faktura_id} etter automatisk tabelloppretting.")
                    return faktura_id
                except Exception as retry_error:
                    logging.error(f"Feil ved nytt forsøk på insert_faktura etter tabelloppretting: {retry_error}",
                                  exc_info=True)
                    raise RuntimeError(f"Feil etter automatisk oppretting av faktura-tabell: {retry_error}")

            try:
                self.db.rollback()
            except Exception as rb_err:
                logging.error(f"Feil under rollback i insert_faktura: {rb_err}")
            raise RuntimeError(f"Feil ved lagring av faktura: {e}")

    def _opprett_faktura_tabell(self):
        """ Oppretter faktura-tabellen hvis den ikke eksisterer. """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS faktura (
            FakturaNr INT AUTO_INCREMENT PRIMARY KEY,
            OrdreNr INT NOT NULL,
            KNr INT NOT NULL,
            FakturaDato TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (OrdreNr) REFERENCES ordre(OrdreNr),
            FOREIGN KEY (KNr) REFERENCES kunde(KNr)
        );
        """
        try:
            self.db.execute(create_table_sql)
            self.db.commit()
            logging.info("✅ Tabell 'faktura' opprettet automatisk.")
        except Exception as e:
            logging.error(f"Kunne ikke opprette tabellen 'faktura': {e}", exc_info=True)
            raise RuntimeError(f"Feil ved opprettelse av tabellen faktura: {e}")

    # --- Metoder for Startsiden (uendret fra sist) ---
    def hent_siste_ordrer(self, antall=5):
        try:
            spørring = """
                SELECT o.OrdreNr, o.OrdreDato, CONCAT(k.Fornavn, ' ', k.Etternavn) AS Kundenavn
                FROM ordre o LEFT JOIN kunde k ON o.KNr = k.KNr
                ORDER BY o.OrdreDato DESC, o.OrdreNr DESC LIMIT %s; """
            return self.hent_alle(spørring, (antall,))
        except Exception as e: logging.exception("Feil ved henting av siste ordrer"); return []

    def hent_verdi_ubetalte_ordrer(self):
        try:
            spørring = "SELECT SUM(PrisPrEnhet * Antall) FROM ordrelinje WHERE OrdreNr IN (SELECT OrdreNr FROM ordre WHERE BetaltDato IS NULL);"
            resultat = self.db.fetch_one(spørring)
            verdi = resultat.get("SUM(PrisPrEnhet * Antall)", 0) if resultat else 0
            return Decimal(verdi) if verdi is not None else Decimal('0.00')
        except Exception as e:
            logging.exception("Feil ved henting av verdi ubetalte ordrer")
            return Decimal('0.00')

    def hent_antall_ordrer_per_aar(self, årstall):
        try:
            spørring = "SELECT COUNT(*) FROM ordre WHERE YEAR(OrdreDato) = %s;"
            resultat = self.db.fetch_one(spørring, (årstall,))
            return resultat.get("COUNT(*)", 0) if resultat else 0
        except Exception as e:
            logging.exception(f"Feil ved henting av antall ordrer for år {årstall}")
            return 0

    def hent_varer_lav_beholdning(self, grense=10):
        try:
            spørring = "SELECT VNr, Betegnelse, Antall FROM vare WHERE Antall < %s ORDER BY Antall ASC;"
            return self.hent_alle(spørring, (grense,))
        except Exception as e: logging.exception(f"Feil ved henting av varer lav beholdning"); return []

    # --- Metoder for Ordrelegging (Inkludert nå) ---

    def hent_kunde_liste(self):
        """ Henter liste over kunder (KNr, Navn) via Stored Procedure. """
        try:
            kunder_raadata = self.kall_prosedyre("hent_alle_kunder")
            kunde_liste = []
            if kunder_raadata:
                for kunde in kunder_raadata: # Antar SP returnerer: KNr, Fornavn, Etternavn, ...
                    knr = kunde[0]; navn = f"{kunde[2]}, {kunde[1]}" # Etternavn, Fornavn
                    kunde_liste.append((knr, navn))
            logging.info(f"Hentet {len(kunde_liste)} kunder for liste via SP.")
            return kunde_liste
        except Exception as e:
            logging.error(f"Kunne ikke hente kundeliste via SP: {e}")
            raise RuntimeError(f"Databasefeil under henting av kundeliste: {e}") from e

    def hent_vare_liste(self):
        """ Henter liste over varer (VNr, Betegnelse, Pris). """
        try:
            spørring = "SELECT VNr, Betegnelse, Pris FROM vare ORDER BY Betegnelse ASC;"
            vareliste_raw = self.hent_alle(spørring)
            # Konverter pris til Decimal
            vareliste = [(v[0], v[1], Decimal(v[2]) if v[2] is not None else Decimal('0.00')) for v in vareliste_raw]
            logging.info(f"Hentet {len(vareliste)} varer for liste.")
            return vareliste
        except Exception as e:
            logging.exception("Feil ved henting av vareliste")
            raise RuntimeError(f"Databasefeil under henting av vareliste: {e}") from e

    def lagre_ny_ordre(self, kunde_nr, ordre_dato_str, ordrelinjer):
        """ Lagrer en ny ordre med linjer i en transaksjon. """
        if not kunde_nr or not ordrelinjer:
            raise ValueError("Mangler kunde eller ordrelinjer for å lagre ordren.")

        required_db_methods = ['start_transaction', 'commit', 'rollback', 'execute', 'get_last_row_id']
        if not all(hasattr(self.db, m) and callable(getattr(self.db, m)) for m in required_db_methods):
             missing = [m for m in required_db_methods if not hasattr(self.db, m) or not callable(getattr(self.db, m))]
             msg = f"Database-objektet mangler nødvendige metoder: {', '.join(missing)}"
             logging.error(msg)
             raise NotImplementedError(msg)

        nytt_ordre_nr = None
        try:
            self.db.start_transaction()
            logging.info(f"Startet transaksjon for ny ordre for kunde {kunde_nr}")

            sql_ordre = "INSERT INTO ordre (KNr, OrdreDato) VALUES (%s, %s);"
            self.db.execute(sql_ordre, (kunde_nr, ordre_dato_str))

            nytt_ordre_nr = self.db.get_last_row_id()
            if not nytt_ordre_nr:
                raise RuntimeError("Klarte ikke å hente nytt OrdreNr etter INSERT i ordre.")
            logging.info(f"Nytt ordrehode satt inn med OrdreNr: {nytt_ordre_nr}")

            sql_linje = "INSERT INTO ordrelinje (OrdreNr, VNr, PrisPrEnhet, Antall) VALUES (%s, %s, %s, %s);"
            linje_params_liste = []
            for linje in ordrelinjer:
                vnr, antall, pris_pr_enhet = linje
                try: # Valider/konverter inne i loopen
                    pris_decimal = Decimal(pris_pr_enhet) if not isinstance(pris_pr_enhet, Decimal) else pris_pr_enhet
                    antall_int = int(antall)
                    params_linje = (nytt_ordre_nr, vnr, pris_decimal, antall_int)
                    linje_params_liste.append(params_linje)
                except (InvalidOperation, TypeError, ValueError) as conv_err:
                    # Logger feil, men lar transaksjonen håndtere rollback i ytre try/except
                    logging.error(f"Ugyldig data i ordrelinje for VNr {vnr}: Antall='{antall}', Pris='{pris_pr_enhet}'. Feil: {conv_err}")
                    raise ValueError(f"Ugyldig data (antall/pris) for vare {vnr}.") from conv_err

            logging.debug(f"Forbereder {len(linje_params_liste)} ordrelinjer for ordre {nytt_ordre_nr}")

            # Bruk executemany hvis tilgjengelig
            if hasattr(self.db, 'executemany') and callable(getattr(self.db, 'executemany')):
                 rowcount_lines = self.db.executemany(sql_linje, linje_params_liste)
                 logging.info(f"Satte inn {rowcount_lines} ordrelinjer med executemany.")
            else:
                 logging.info("Bruker loop med execute for å sette inn ordrelinjer.")
                 for params_linje in linje_params_liste:
                      self.db.execute(sql_linje, params_linje)

            self.db.commit()
            logging.info(f"Transaksjon for ordre {nytt_ordre_nr} committet.")
            return nytt_ordre_nr

        except Exception as e:
            logging.exception(f"Feil under lagring av ny ordre for kunde {kunde_nr}. Ruller tilbake.")
            try: self.db.rollback(); logging.info("Transaksjon rullet tilbake.")
            except Exception as rb_err: logging.error(f"Feil under rollback: {rb_err}")
            raise RuntimeError(f"Databasefeil ved lagring av ordre: {e}") from e