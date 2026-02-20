import json
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

    def test_load_corrupt_json_does_not_crash(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        res = self.customers.display_customer("C1") 
        self.assertIsNone(res)

    def test_load_non_list_json_returns_empty(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"a": 1}, f)
        res = self.customers.display_customer("C1")
        self.assertIsNone(res)

    def test_load_list_with_non_object_items_is_ignored(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(["bad", 123, None, {"customer_id": "C1", "full_name": "Miguel", "email": "miguel@x.com"}], f)
        res = self.customers.display_customer("C1")
        self.assertIsNotNone(res)

    def test_load_object_missing_required_keys_is_ignored(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([{"customer_id": "C1"}], f)
        res = self.customers.display_customer("C1")
        self.assertIsNone(res)

    def test_modify_customer_raises_when_not_found(self):
        with self.assertRaises(ValueError):
            self.customers.modify_customer("C404", full_name="X")  # ajusta firma si cambia

    def test_modify_customer_rejects_invalid_email(self):
        self.customers.create_customer("C1", "Miguel Silva" , "miguel@example.com")
        with self.assertRaises (ValueError):
            self.customers.modify_customer ("C1", email="bad")
    
    def test_create_customer_rejects_empty_id(self):
        with self.assertRaises (ValueError):
            self. customers.create_customer("", "Miguel Silva", "miguel@example.com")

    def test_create_customer_rejects_duplicate_id(self):
        self.customers.create_customer("C1", "Miguel Silva", "miguel@example.com" ) 
        with self.assertRaises(ValueError):
            self.customers.create_customer ("C1", "Other Name", "other@example. com")

    def test_create_customer_rejects_invalid_email(self):
        with self.assertRaises(ValueError):
            self.customers.create_customer("C2", "Miguel", "invalid-email")
    
    def test_delete_customer_raises_when_not_found(self):
        with self.assertRaises (ValueError):
            self.customers.delete_customer ("С404")
