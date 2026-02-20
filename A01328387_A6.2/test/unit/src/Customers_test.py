import os
import tempfile
import unittest

from source.Customers import Customers


class CustomersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "customers.json")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("[]")
        self.customers = Customers(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_and_display_customer(self):
        self.customers.create_customer("C1", "Miguel Silva", "miguel@example.com")
        rec = self.customers.display_customer("C1")
        self.assertEqual("C1", rec.customer_id)

    def test_create_customer_rejects_invalid_email(self):
        with self.assertRaises(ValueError):
            self.customers.create_customer("C1", "Miguel", "invalid-email")