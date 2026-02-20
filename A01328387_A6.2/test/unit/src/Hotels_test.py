import json
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

    def test_load_corrupt_json_does_not_crash(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        res = self.hotels.display_hotel("H1")
        self.assertIsNone(res)

    def test_load_non_list_json_returns_empty(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"x": 1}, f)
        res = self.hotels.display_hotel("H1")
        self.assertIsNone(res)

    def test_load_invalid_hotel_records_are_ignored(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "hotel_id": "BAD1",
                        "name": "X",
                        "location": "Y",
                        "total_rooms": 1,
                        "available_rooms": 2,
                    },
                    {
                        "hotel_id": "BAD2",
                        "name": "X",
                        "location": "Y",
                        "total_rooms": -1,
                        "available_rooms": 0,
                    },
                    "not-dict",
                    {
                        "hotel_id": "H1",
                        "name": "Ok",
                        "location": "MTY",
                        "total_rooms": 2,
                        "available_rooms": 2,
                    },
                ],
                f,
            )
        self.assertIsNotNone(self.hotels.display_hotel("H1"))
        self.assertIsNone(self.hotels.display_hotel("BAD1"))

    def test_reserve_room_raises_if_hotel_not_found(self):
        with self.assertRaises(ValueError):
            self.hotels.reserve_room("H404")

    def test_release_room_raises_if_hotel_not_found(self):
        with self.assertRaises(ValueError):
            self.hotels.release_room("H404")

    def test_release_room_raises_if_already_full(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 1)
        with self.assertRaises(ValueError):
            self.hotels.release_room("H1")

    def test_modify_hotel_raises_if_not_found(self):
        with self.assertRaises(ValueError):
            self.hotels.modify_hotel("H404", name="X")

    def test_modify_hotel_rejects_negative_total_rooms(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 2)
        with self.assertRaises(ValueError):
            self.hotels.modify_hotel("H1", total_rooms=-1)

    def test_modify_hotel_rejects_total_less_than_reserved(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 2)
        self.hotels.reserve_room("H1") 
        with self.assertRaises(ValueError):
            self.hotels.modify_hotel("H1", total_rooms=0)

    def test_reserve_room_raises_when_full(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 0)
        with self.assertRaises(ValueError):
            self.hotels.reserve_room("H1")

    def test_create_hotel_rejects_empty_id(self):
        with self.assertRaises(ValueError):
            self.hotels.create_hotel("", "Hotel One", "MTY", 10)

    def test_create_hotel_rejects_duplicate_id(self):
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 10) 
        with self.assertRaises(ValueError):
            self.hotels. create_hotel("H1", "Another", "CDMX", 5)

    def test_create_hotel_rejects_negative_total_rooms (self):
        with self.assertRaises(ValueError):
            self.hotels.create_hotel("H2", "Hotel Two", "MTY", -1)
    
    def test_delete_hotel_raises_when_not_found(self):
        with self.assertRaises(ValueError):
            self.hotels.delete_hotel ("H404")