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

    def test_create_reservation_raises_if_customer_missing(self):
        with self.assertRaises(ValueError):
            self.res.create_reservation("R1", "C404", "H1")