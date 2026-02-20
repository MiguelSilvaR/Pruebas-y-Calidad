import os
import tempfile
import unittest

from source.Hotels import Hotels


class HotelsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "hotels.json")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("[]")
        self.hotels = Hotels(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_and_display_hotel(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 2)
        rec = self.hotels.display_hotel("H1")
        self.assertEqual("H1", rec.hotel_id)
        self.assertEqual(2, rec.available_rooms)

    def test_reserve_room_decrements(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 1)
        self.hotels.reserve_room("H1")
        rec = self.hotels.display_hotel("H1")
        self.assertEqual(0, rec.available_rooms)

    def test_reserve_room_raises_when_full(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 0)
        with self.assertRaises(ValueError):
            self.hotels.reserve_room("H1")