# database/database.py
# (Tidligere kjent som database_program.py)
# Fullstendig og korrekt!

import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import logging

# Last inn .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))

class Database:
    def __init__(self):
        self.connection = None
        self.last_cursor = None
        self._connect()

    def _connect(self):
        if self.connection and self.connection.is_connected():
            return
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT
            )
            self.connection.autocommit = False  # VIKTIG!
            logging.info("✅ Database connected (autocommit=False)")
        except mysql.connector.Error as err:
            logging.error(f"⚠ Database connection error: {err}")
            self.connection = None
            raise ConnectionError(f"Kunne ikke koble til databasen: {err}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("🔌 Database connection closed.")

    def _get_cursor(self, dictionary=False):
        if not self.connection or not self.connection.is_connected():
            self._connect()
        cursor = self.connection.cursor(dictionary=dictionary)
        self.last_cursor = cursor
        return cursor

    def fetch_all(self, query, params=()):
        try:
            cursor = self._get_cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()

    def fetch_one(self, query, params=()):
        try:
            cursor = self._get_cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()

    def execute(self, query, params=()):
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, query, params_list):
        try:
            cursor = self._get_cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
        finally:
            cursor.close()

    def call_procedure(self, procedure, args=()):
        try:
            cursor = self._get_cursor(dictionary=True)
            cursor.callproc(procedure, args)
            result = []
            for r in cursor.stored_results():
                result.extend(r.fetchall())
            self.connection.commit()
            return result
        finally:
            cursor.close()

    def start_transaction(self):
        if not self.connection or not self.connection.is_connected():
            self._connect()
        try:
            self.connection.start_transaction()
            logging.info("🚀 Startet ny database-transaksjon.")
        except mysql.connector.Error as err:
            logging.error(f"Feil ved start_transaction: {err}")
            raise RuntimeError("Kunne ikke starte databasetransaksjon.")

    def commit(self):
        if self.connection and self.connection.is_connected():
            self.connection.commit()
            logging.info("💾 Database-commit fullført.")

    def rollback(self):
        if self.connection and self.connection.is_connected():
            self.connection.rollback()
            logging.info("↩ Database rollback utført.")

    def get_last_row_id(self):
        if self.last_cursor:
            return self.last_cursor.lastrowid
        return None
