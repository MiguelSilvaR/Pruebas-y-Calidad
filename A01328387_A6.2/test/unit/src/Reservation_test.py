import json
import os
import tempfile
import unittest

from source.Customers import Customers
from source.Hotels import Hotels
from source.Reservation import Reservation


class ReservationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

        self.hotels_path = os.path.join(self.tmp.name, "hotels.json")
        self.customers_path = os.path.join(self.tmp.name, "customers.json")
        self.res_path = os.path.join(self.tmp.name, "reservations.json")

        for p in (self.hotels_path, self.customers_path, self.res_path):
            with open(p, "w", encoding="utf-8") as f:
                f.write("[]")

        self.hotels = Hotels(self.hotels_path)
        self.customers = Customers(self.customers_path)
        self.res = Reservation(self.res_path, self.hotels, self.customers)

        self.hotels.create_hotel("H1", "Hotel One", "MTY", 1)
        self.customers.create_customer("C1", "Miguel Silva", "miguel@example.com")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_reservation_decrements_room(self):
        self.res.create_reservation("R1", "C1", "H1")
        h = self.hotels.display_hotel("H1")
        self.assertEqual(0, h.available_rooms)

    def test_cancel_reservation_releases_room(self):
        self.res.create_reservation("R1", "C1", "H1")
        self.res.cancel_reservation("R1")
        h = self.hotels.display_hotel("H1")
        self.assertEqual(1, h.available_rooms)

    def test_load_corrupt_json_does_not_crash(self):
        with open(self.res_path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        self.assertIsNone(self.res.display_reservation("R1"))

    def test_cancel_reservation_raises_if_not_found(self):
        with self.assertRaises(ValueError):
            self.res.cancel_reservation("R404")

    def test_cancel_reservation_is_idempotent(self):
        self.res.create_reservation("R1", "C1", "H1")
        self.res.cancel_reservation("R1")
        self.res.cancel_reservation("R1") # No exception

    def test_create_reservation_raises_when_hotel_full(self):
        self.res.create_reservation("R1", "C1", "H1")
        with self.assertRaises(ValueError):
            self.res.create_reservation("R2", "C1", "H1")

    def test_load_list_with_bad_items_is_ignored(self):
        with open(self.res_path, "w", encoding="utf-8") as f:
            json.dump(["bad", {"reservation_id": "R1"}], f)
        self.assertIsNone(self.res.display_reservation("R1"))

    def test_create_reservation_raises_if_customer_missing(self):
        with self.assertRaises(ValueError):
            self.res.create_reservation("R1", "C404", "H1")

    def test_create_reservation_rejects_empty_reservation_id(self):
        with self.assertRaises (ValueError):
            self.res.create_reservation("", "C1", "H1")
    
    def test_create_reservation_rejects_duplicate_reservation_id(self):
        self. res. create_reservation("R1", "C1", "H1")
        with self.assertRaises (ValueError):
            self.res.create_reservation ("R1", "C1", "H1")

    def test_create_reservation_raises_if_hotel_missing(self):
        with self.assertRaises(ValueError):
            self. res.create_reservation ("R1", "C1", "H404")

    def test_create_reservation_raises_when_hotel_is_full(self):
        self. res. create_reservation("R1", "C1", "H1")
        with self.assertRaises (ValueError):
            self. res.create_reservation ("R2", "C1", "H1")