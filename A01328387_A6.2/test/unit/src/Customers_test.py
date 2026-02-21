"""
Unit tests for the Customers module.

Validates CRUD behavior and input validation, and ensures JSON persistence
loading is resilient to corrupt or malformed content.
"""

import json
import os

from test.unit.src.base_test_case import TempDirTestCase
from source.customers import Customers


class CustomersTest(TempDirTestCase):
    """Unit tests for Customers persistence and validation rules."""

    def setUp(self):
        """Create a temporary customers.json and a Customers instance."""
        super().setUp()

        self.path = os.path.join(self.tmp_dir, "customers.json")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("[]")

        self.customers = Customers(self.path)

    def test_create_and_display_customer(self):
        """Creating a customer should persist and be retrievable by id."""
        self.customers.create_customer(
            "C1",
            "Miguel Silva",
            "miguel@example.com"
            )
        rec = self.customers.display_customer("C1")
        self.assertEqual("C1", rec.customer_id)

    def test_load_corrupt_json_does_not_crash(self):
        """Corrupt JSON should not crash; display should return None."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        res = self.customers.display_customer("C1")
        self.assertIsNone(res)

    def test_load_non_list_json_returns_empty(self):
        """
        If the JSON root is not a list,
        the loader should behave as empty.
        """
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"a": 1}, f)
        res = self.customers.display_customer("C1")
        self.assertIsNone(res)

    def test_load_list_with_non_object_items_is_ignored(self):
        """Non-dict items in the JSON list should be ignored."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    "bad",
                    123,
                    None,
                    {
                        "customer_id": "C1",
                        "full_name": "Miguel",
                        "email": "miguel@x.com",
                    },
                ],
                f,
            )
        res = self.customers.display_customer("C1")
        self.assertIsNotNone(res)

    def test_load_object_missing_required_keys_is_ignored(self):
        """Objects missing required keys should be ignored."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([{"customer_id": "C1"}], f)
        res = self.customers.display_customer("C1")
        self.assertIsNone(res)

    def test_modify_customer_raises_when_not_found(self):
        """Modifying an unknown customer should raise."""
        with self.assertRaises(ValueError):
            self.customers.modify_customer("C404", full_name="X")

    def test_modify_customer_rejects_invalid_email(self):
        """Invalid email should be rejected when modifying."""
        self.customers.create_customer(
            "C1",
            "Miguel Silva",
            "miguel@example.com"
            )
        with self.assertRaises(ValueError):
            self.customers.modify_customer("C1", email="bad")

    def test_create_customer_rejects_empty_id(self):
        """customer_id must be non-empty."""
        with self.assertRaises(ValueError):
            self.customers.create_customer(
                "",
                "Miguel Silva",
                "miguel@example.com"
                )

    def test_create_customer_rejects_duplicate_id(self):
        """Duplicate customer_id should raise."""
        self.customers.create_customer(
            "C1",
            "Miguel Silva",
            "miguel@example.com"
            )
        with self.assertRaises(ValueError):
            self.customers.create_customer(
                "C1",
                "Other Name",
                "other@example.com"
                )

    def test_create_customer_rejects_invalid_email(self):
        """Invalid email should be rejected when creating."""
        with self.assertRaises(ValueError):
            self.customers.create_customer("C2", "Miguel", "invalid-email")

    def test_delete_customer_raises_when_not_found(self):
        """Deleting an unknown customer should raise."""
        with self.assertRaises(ValueError):
            self.customers.delete_customer("C404")
