"""
Hotels domain module.

Provides the Hotels service and HotelRecord model to manage hotel data and room
availability, persisting records in a JSON file.

Key behaviors:
- Validates hotel_id is non-empty and unique on creation.
- Enforces non-negative total/available rooms and available <= total.
- Supports modifying hotel metadata and resizing total_rooms without violating
  already-reserved rooms.
- Supports reserving/releasing a room with validation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional

from .storage import print_data_error, safe_load_list, safe_write_list


@dataclass(frozen=True)
class HotelRecord:
    """Immutable hotel record persisted to JSON."""
    hotel_id: str
    name: str
    location: str
    total_rooms: int
    available_rooms: int


class Hotels:
    """Service for hotel CRUD operations and room availability management."""

    def __init__(self, filepath: str) -> None:
        """
        Initialize the hotels service.

        Args:
            filepath: Path to the JSON file used for persistence.
        """
        self.filepath = filepath

    def _load(self) -> Dict[str, HotelRecord]:
        """
        Load hotels from JSON storage.

        Returns:
            Dict mapping hotel_id to HotelRecord.

        Notes:
            Invalid/corrupt items are ignored and
            reported via print_data_error,
            and the function continues best-effort.
        """
        records: Dict[str, HotelRecord] = {}
        for idx, row in enumerate(safe_load_list(self.filepath)):
            try:
                rec = HotelRecord(
                    hotel_id=str(row["hotel_id"]).strip(),
                    name=str(row["name"]).strip(),
                    location=str(row["location"]).strip(),
                    total_rooms=int(row["total_rooms"]),
                    available_rooms=int(row["available_rooms"]),
                )
                if not rec.hotel_id or not rec.name:
                    raise ValueError("hotel_id/name empty")
                if rec.total_rooms < 0 or rec.available_rooms < 0:
                    raise ValueError("negative rooms")
                if rec.available_rooms > rec.total_rooms:
                    raise ValueError("available > total")
                records[rec.hotel_id] = rec
            except (KeyError, ValueError, TypeError) as exc:
                msg = f"Invalid hotel at index {idx}: {exc}"
                print_data_error(msg)
        return records

    def _save(self, records: Dict[str, HotelRecord]) -> None:
        """
        Persist hotels to JSON storage.

        Args:
            records: Dict of HotelRecord keyed by hotel_id.
        """
        safe_write_list(self.filepath, [asdict(v) for v in records.values()])

    # Req 2.1 a-d
    def create_hotel(
        self,
        hotel_id: str,
        name: str,
        location: str,
        total_rooms: int,
    ) -> None:
        """
        Create a new hotel.

        Args:
            hotel_id: Unique hotel identifier (non-empty).
            name: Hotel name.
            location: Hotel location.
            total_rooms: Total number of rooms (must be >= 0).

        Raises:
            ValueError: If hotel_id is empty/duplicate
            or total_rooms is negative.
        """
        hotels = self._load()
        hotel_id = hotel_id.strip()
        if not hotel_id:
            raise ValueError("hotel_id must be non-empty")
        if hotel_id in hotels:
            raise ValueError("Hotel already exists")
        if total_rooms < 0:
            raise ValueError("total_rooms must be >= 0")

        hotels[hotel_id] = HotelRecord(
            hotel_id=hotel_id,
            name=name.strip(),
            location=location.strip(),
            total_rooms=int(total_rooms),
            available_rooms=int(total_rooms),
        )
        self._save(hotels)

    def delete_hotel(self, hotel_id: str) -> None:
        """
        Delete an existing hotel.

        Args:
            hotel_id: Hotel identifier.

        Raises:
            ValueError: If the hotel does not exist.
        """
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")
        del hotels[hotel_id]
        self._save(hotels)

    def display_hotel(self, hotel_id: str) -> Optional[HotelRecord]:
        """
        Retrieve a hotel by id.

        Args:
            hotel_id: Hotel identifier.

        Returns:
            HotelRecord if found; otherwise None.
        """
        return self._load().get(hotel_id)

    def modify_hotel(
        self,
        hotel_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        total_rooms: Optional[int] = None,
    ) -> None:
        """
        Modify hotel fields.

        Args:
            hotel_id: Hotel identifier.
            name: New name (optional).
            location: New location (optional).
            total_rooms: New total room count (optional).

        Raises:
            ValueError: If hotel not found, total_rooms is negative, or if
                total_rooms would be less than already-reserved rooms.
        """
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")

        old = hotels[hotel_id]
        new_total = (old.total_rooms
                     if total_rooms is None
                     else int(total_rooms))
        if new_total < 0:
            raise ValueError("total_rooms must be >= 0")

        reserved = old.total_rooms - old.available_rooms
        if new_total < reserved:
            raise ValueError("total_rooms less than reserved rooms")

        new_available = new_total - reserved
        hotels[hotel_id] = HotelRecord(
            hotel_id=old.hotel_id,
            name=old.name if name is None else name.strip(),
            location=old.location if location is None else location.strip(),
            total_rooms=new_total,
            available_rooms=new_available,
        )
        self._save(hotels)

    # Req 2.1 e-f (reservar / cancelar)
    def reserve_room(self, hotel_id: str) -> None:
        """
        Reserve one room in a hotel (decrement availability by 1).

        Args:
            hotel_id: Hotel identifier.

        Raises:
            ValueError: If hotel not found or no rooms are available.
        """
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")
        hotel = hotels[hotel_id]
        if hotel.available_rooms <= 0:
            raise ValueError("No rooms available")

        hotels[hotel_id] = HotelRecord(
            hotel_id=hotel.hotel_id,
            name=hotel.name,
            location=hotel.location,
            total_rooms=hotel.total_rooms,
            available_rooms=hotel.available_rooms - 1,
        )
        self._save(hotels)

    def release_room(self, hotel_id: str) -> None:
        """
        Release one room in a hotel (increment availability by 1).

        Args:
            hotel_id: Hotel identifier.

        Raises:
            ValueError: If hotel not found or all rooms are already available.
        """
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")
        hotel = hotels[hotel_id]
        if hotel.available_rooms >= hotel.total_rooms:
            raise ValueError("All rooms already available")

        hotels[hotel_id] = HotelRecord(
            hotel_id=hotel.hotel_id,
            name=hotel.name,
            location=hotel.location,
            total_rooms=hotel.total_rooms,
            available_rooms=hotel.available_rooms + 1,
        )
        self._save(hotels)
