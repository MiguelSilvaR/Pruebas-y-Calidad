from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional

from Customers import Customers
from Hotels import Hotels


def _print_data_error(message: str) -> None:
    print(f"[DATA ERROR] {message}")


def _utc_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


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
class ReservationRecord:
    reservation_id: str
    hotel_id: str
    customer_id: str
    created_at: str
    canceled_at: Optional[str] = None


class Reservation:
    def __init__(self, filepath: str, hotels: Hotels, customers: Customers) -> None:
        self.filepath = filepath
        self.hotels = hotels
        self.customers = customers

    def _load(self) -> Dict[str, ReservationRecord]:
        records: Dict[str, ReservationRecord] = {}
        for idx, row in enumerate(_safe_load_list(self.filepath)):
            try:
                rec = ReservationRecord(
                    reservation_id=str(row["reservation_id"]).strip(),
                    hotel_id=str(row["hotel_id"]).strip(),
                    customer_id=str(row["customer_id"]).strip(),
                    created_at=str(row["created_at"]).strip(),
                    canceled_at=row.get("canceled_at"),
                )
                if not rec.reservation_id or not rec.hotel_id or not rec.customer_id:
                    raise ValueError("missing ids")
                records[rec.reservation_id] = rec
            except (KeyError, ValueError, TypeError) as exc:
                _print_data_error(f"Invalid reservation at index {idx}: {exc}")
        return records

    def _save(self, records: Dict[str, ReservationRecord]) -> None:
        _safe_write_list(self.filepath, [asdict(v) for v in records.values()])

    # Req 2.3 a
    def create_reservation(self, reservation_id: str, customer_id: str, hotel_id: str) -> None:
        reservations = self._load()
        reservation_id = reservation_id.strip()
        if not reservation_id:
            raise ValueError("reservation_id must be non-empty")
        if reservation_id in reservations:
            raise ValueError("Reservation already exists")

        if self.customers.display_customer(customer_id) is None:
            raise ValueError("Customer not found")
        if self.hotels.display_hotel(hotel_id) is None:
            raise ValueError("Hotel not found")

        self.hotels.reserve_room(hotel_id)
        reservations[reservation_id] = ReservationRecord(
            reservation_id=reservation_id,
            hotel_id=hotel_id,
            customer_id=customer_id,
            created_at=_utc_iso(),
            canceled_at=None,
        )
        self._save(reservations)

    # Req 2.3 b
    def cancel_reservation(self, reservation_id: str) -> None:
        reservations = self._load()
        if reservation_id not in reservations:
            raise ValueError("Reservation not found")

        rec = reservations[reservation_id]
        if rec.canceled_at is not None:
            return  # idempotente

        self.hotels.release_room(rec.hotel_id)
        reservations[reservation_id] = ReservationRecord(
            reservation_id=rec.reservation_id,
            hotel_id=rec.hotel_id,
            customer_id=rec.customer_id,
            created_at=rec.created_at,
            canceled_at=_utc_iso(),
        )
        self._save(reservations)

    def display_reservation(self, reservation_id: str) -> Optional[ReservationRecord]:
        return self._load().get(reservation_id)
