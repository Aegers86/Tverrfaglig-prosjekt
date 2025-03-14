# tests.py
# Inneholder tester for API, database og GUI

import unittest
from database import Database
from api import app
from flask.testing import FlaskClient

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client: FlaskClient = app.test_client()

    def test_get_all_products(self):
        response = self.client.get("/api/varer")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()

    def test_fetch_all_customers(self):
        customers = self.db.fetch_all("CALL hent_alle_kunder()")
        self.assertIsInstance(customers, list)

if __name__ == "__main__":
    unittest.main()