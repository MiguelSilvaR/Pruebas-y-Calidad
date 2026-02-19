from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


def _print_data_error(message: str) -> None:
    # Req 5: show error y continue
    print(f"[DATA ERROR] {message}")


def _safe_load_list(path: str) -> List[dict]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            _print_data_error(f"Expected list in {path}")
            return []
        return [x for x in data if isinstance(x, dict)]
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError) as exc:
        _print_data_error(f"Cannot read {path}: {exc}")
        return []


def _safe_write_list(path: str, items: List[dict]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(items, handle, indent=2, ensure_ascii=False)
    except OSError as exc:
        _print_data_error(f"Cannot write {path}: {exc}")


@dataclass(frozen=True)
class HotelRecord:
    hotel_id: str
    name: str
    location: str
    total_rooms: int
    available_rooms: int


class Hotels:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def _load(self) -> Dict[str, HotelRecord]:
        records: Dict[str, HotelRecord] = {}
        for idx, row in enumerate(_safe_load_list(self.filepath)):
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
                _print_data_error(f"Invalid hotel at index {idx}: {exc}")
        return records

    def _save(self, records: Dict[str, HotelRecord]) -> None:
        _safe_write_list(self.filepath, [asdict(v) for v in records.values()])

    # Req 2.1 a-d
    def create_hotel(
        self, hotel_id: str, name: str, location: str, total_rooms: int
    ) -> None:
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
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")
        del hotels[hotel_id]
        self._save(hotels)

    def display_hotel(self, hotel_id: str) -> Optional[HotelRecord]:
        return self._load().get(hotel_id)

    def modify_hotel(
        self,
        hotel_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        total_rooms: Optional[int] = None,
    ) -> None:
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")

        old = hotels[hotel_id]
        new_total = old.total_rooms if total_rooms is None else int(total_rooms)
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
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")
        h = hotels[hotel_id]
        if h.available_rooms <= 0:
            raise ValueError("No rooms available")
        hotels[hotel_id] = HotelRecord(
            hotel_id=h.hotel_id,
            name=h.name,
            location=h.location,
            total_rooms=h.total_rooms,
            available_rooms=h.available_rooms - 1,
        )
        self._save(hotels)

    def release_room(self, hotel_id: str) -> None:
        hotels = self._load()
        if hotel_id not in hotels:
            raise ValueError("Hotel not found")
        h = hotels[hotel_id]
        if h.available_rooms >= h.total_rooms:
            raise ValueError("All rooms already available")
        hotels[hotel_id] = HotelRecord(
            hotel_id=h.hotel_id,
            name=h.name,
            location=h.location,
            total_rooms=h.total_rooms,
            available_rooms=h.available_rooms + 1,
        )
        self._save(hotels)
