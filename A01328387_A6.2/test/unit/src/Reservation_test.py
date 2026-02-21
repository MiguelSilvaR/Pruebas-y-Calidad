"""
Unit tests for the Reservation module.

Covers creation and cancellation flows, validates behavior when referenced
entities are missing, verifies idempotent cancellation, and checks robustness
against invalid JSON persistence data.
"""

import json
import os

from test.unit.src.base_test_case import TempDirTestCase
from source.customers import Customers
from source.hotels import Hotels
from source.reservation import Reservation


class ReservationTest(TempDirTestCase):
    """Unit tests for reservation creation, cancellation, and persistence."""

    def setUp(self):
        """
        Create temporary JSON files and
        initialize Hotels/Customers/Reservation.
        """
        super().setUp()

        self.hotels_path = os.path.join(self.tmp_dir, "hotels.json")
        self.customers_path = os.path.join(self.tmp_dir, "customers.json")
        self.res_path = os.path.join(self.tmp_dir, "reservations.json")

        for path in (self.hotels_path, self.customers_path, self.res_path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("[]")

        self.hotels = Hotels(self.hotels_path)
        self.customers = Customers(self.customers_path)
        self.res = Reservation(self.res_path, self.hotels, self.customers)

        self.hotels.create_hotel("H1", "Hotel One", "MTY", 1)
        self.customers.create_customer(
            "C1",
            "Miguel Silva",
            "miguel@example.com"
            )

    def test_create_reservation_decrements_room(self):
        """
        Creating a reservation should
        decrement available rooms for
        the hotel.
        """
        self.res.create_reservation("R1", "C1", "H1")
        hotel = self.hotels.display_hotel("H1")
        self.assertEqual(0, hotel.available_rooms)

    def test_cancel_reservation_releases_room(self):
        """Canceling a reservation should release a room back to the hotel."""
        self.res.create_reservation("R1", "C1", "H1")
        self.res.cancel_reservation("R1")
        hotel = self.hotels.display_hotel("H1")
        self.assertEqual(1, hotel.available_rooms)

    def test_load_corrupt_json_does_not_crash(self):
        """Corrupt JSON should not crash; display should return None."""
        with open(self.res_path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        self.assertIsNone(self.res.display_reservation("R1"))

    def test_cancel_reservation_raises_if_not_found(self):
        """Canceling a non-existent reservation should raise."""
        with self.assertRaises(ValueError):
            self.res.cancel_reservation("R404")

    def test_cancel_reservation_is_idempotent(self):
        """Canceling the same reservation twice should not raise."""
        self.res.create_reservation("R1", "C1", "H1")
        self.res.cancel_reservation("R1")
        self.res.cancel_reservation("R1")  # no exception expected

    def test_create_reservation_raises_when_hotel_full(self):
        """
        Creating a reservation should
        raise if the hotel has no availability.
        """
        self.res.create_reservation("R1", "C1", "H1")
        with self.assertRaises(ValueError):
            self.res.create_reservation("R2", "C1", "H1")

    def test_load_list_with_bad_items_is_ignored(self):
        """
        Invalid list items should be ignored;
        incomplete dict should not load.
        """
        with open(self.res_path, "w", encoding="utf-8") as f:
            json.dump(["bad", {"reservation_id": "R1"}], f)
        self.assertIsNone(self.res.display_reservation("R1"))

    def test_create_reservation_rejects_empty_reservation_id(self):
        """Empty reservation_id should raise."""
        with self.assertRaises(ValueError):
            self.res.create_reservation("", "C1", "H1")

    def test_create_reservation_rejects_duplicate_reservation_id(self):
        """Duplicate reservation_id should raise."""
        self.res.create_reservation("R1", "C1", "H1")
        with self.assertRaises(ValueError):
            self.res.create_reservation("R1", "C1", "H1")

    def test_create_reservation_raises_if_customer_missing(self):
        """Customer must exist to create a reservation."""
        with self.assertRaises(ValueError):
            self.res.create_reservation("R1", "C404", "H1")

    def test_create_reservation_raises_if_hotel_missing(self):
        """Hotel must exist to create a reservation."""
        with self.assertRaises(ValueError):
            self.res.create_reservation("R1", "C1", "H404")
