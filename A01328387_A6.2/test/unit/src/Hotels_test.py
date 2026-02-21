"""
Unit tests for the Hotels module.

These tests validate CRUD operations and room availability rules, and verify
that the JSON persistence layer is resilient to corrupt or invalid data.
"""

import json
import os
import tempfile
import unittest

from source.hotels import Hotels


class HotelsTest(unittest.TestCase):
    """Unit tests for Hotels persistence and business rules."""

    def setUp(self):
        """
        Create a temporary hotels.json and
        a Hotels instance for each test.
        """
        # pylint: disable=consider-using-with
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "hotels.json")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("[]")
        self.hotels = Hotels(self.path)

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tmp.cleanup()

    def test_create_and_display_hotel(self):
        """Creating a hotel should persist and be retrievable by id."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 2)
        rec = self.hotels.display_hotel("H1")
        self.assertEqual("H1", rec.hotel_id)
        self.assertEqual(2, rec.available_rooms)

    def test_reserve_room_decrements(self):
        """Reserving a room should decrement available_rooms by 1."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 1)
        self.hotels.reserve_room("H1")
        rec = self.hotels.display_hotel("H1")
        self.assertEqual(0, rec.available_rooms)

    def test_load_corrupt_json_does_not_crash(self):
        """Corrupt JSON should not crash; display should return None."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        res = self.hotels.display_hotel("H1")
        self.assertIsNone(res)

    def test_load_non_list_json_returns_empty(self):
        """
        If the JSON root is not a list,
        the loader should behave as empty.
        """
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"x": 1}, f)
        res = self.hotels.display_hotel("H1")
        self.assertIsNone(res)

    def test_load_invalid_hotel_records_are_ignored(self):
        """Invalid records should be ignored while valid ones remain usable."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "hotel_id": "BAD1",
                        "name": "X",
                        "location": "Y",
                        "total_rooms": 1,
                        "available_rooms": 2,  # invalid: available > total
                    },
                    {
                        "hotel_id": "BAD2",
                        "name": "X",
                        "location": "Y",
                        "total_rooms": -1,  # invalid: negative rooms
                        "available_rooms": 0,
                    },
                    "not-dict",  # invalid: not an object
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
        """Reserving a room for an unknown hotel should raise."""
        with self.assertRaises(ValueError):
            self.hotels.reserve_room("H404")

    def test_release_room_raises_if_hotel_not_found(self):
        """Releasing a room for an unknown hotel should raise."""
        with self.assertRaises(ValueError):
            self.hotels.release_room("H404")

    def test_release_room_raises_if_already_full(self):
        """Releasing when all rooms are already available should raise."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 1)
        with self.assertRaises(ValueError):
            self.hotels.release_room("H1")

    def test_modify_hotel_raises_if_not_found(self):
        """Modifying an unknown hotel should raise."""
        with self.assertRaises(ValueError):
            self.hotels.modify_hotel("H404", name="X")

    def test_modify_hotel_rejects_negative_total_rooms(self):
        """total_rooms cannot be negative."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 2)
        with self.assertRaises(ValueError):
            self.hotels.modify_hotel("H1", total_rooms=-1)

    def test_modify_hotel_rejects_total_less_than_reserved(self):
        """total_rooms cannot be reduced below the number of reserved rooms."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 2)
        self.hotels.reserve_room("H1")  # reserved = 1
        with self.assertRaises(ValueError):
            self.hotels.modify_hotel("H1", total_rooms=0)

    def test_reserve_room_raises_when_full(self):
        """Reserving a room when the hotel has no availability should raise."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 0)
        with self.assertRaises(ValueError):
            self.hotels.reserve_room("H1")

    def test_create_hotel_rejects_empty_id(self):
        """hotel_id must be non-empty."""
        with self.assertRaises(ValueError):
            self.hotels.create_hotel("", "Hotel One", "MTY", 10)

    def test_create_hotel_rejects_duplicate_id(self):
        """Creating a hotel with a duplicate id should raise."""
        self.hotels.create_hotel("H1", "Hotel One", "MTY", 10)
        with self.assertRaises(ValueError):
            self.hotels.create_hotel("H1", "Another", "CDMX", 5)

    def test_create_hotel_rejects_negative_total_rooms(self):
        """Creating a hotel with negative total_rooms should raise."""
        with self.assertRaises(ValueError):
            self.hotels.create_hotel("H2", "Hotel Two", "MTY", -1)

    def test_delete_hotel_raises_when_not_found(self):
        """Deleting an unknown hotel should raise."""
        with self.assertRaises(ValueError):
            self.hotels.delete_hotel("H404")
