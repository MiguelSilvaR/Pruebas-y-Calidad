"""
Reservation domain module.

Provides the Reservation service and ReservationRecord model to create and
cancel hotel reservations, persisting them to a JSON file.

Key behaviors:
- Validates reservation_id is non-empty and unique.
- Validates referenced customer and hotel exist.
- Reserves a room on creation and releases it on cancellation.
- Cancellation is idempotent (canceling twice does not raise).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Dict, Optional

from .storage import print_data_error, safe_load_list, safe_write_list
from .customers import Customers
from .hotels import Hotels


def _utc_iso() -> str:
    """Return current UTC time as an ISO-8601 string using 'Z' suffix."""
    return (
        datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True)
class ReservationRecord:
    """Immutable reservation record persisted to JSON."""
    reservation_id: str
    hotel_id: str
    customer_id: str
    created_at: str
    canceled_at: Optional[str] = None


class Reservation:
    """
    Reservation service handling
    create/cancel operations and persistence.
    """

    def __init__(
            self,
            filepath: str,
            hotels: Hotels,
            customers: Customers
            ) -> None:
        """
        Initialize the reservation service.

        Args:
            filepath: Path to the JSON file used for persistence.
            hotels: Hotels service used to validate hotels and
            reserve/release rooms.
            customers: Customers service used to validate customers.
        """
        self.filepath = filepath
        self.hotels = hotels
        self.customers = customers

    def _load(self) -> Dict[str, ReservationRecord]:
        """
        Load reservations from JSON storage.

        Returns:
            Dict mapping reservation_id to ReservationRecord.

        Notes:
            Invalid/corrupt items are ignored and
            reported via print_data_error,
            and the function continues best-effort.
        """
        records: Dict[str, ReservationRecord] = {}
        for idx, row in enumerate(safe_load_list(self.filepath)):
            try:
                rec = ReservationRecord(
                    reservation_id=str(row["reservation_id"]).strip(),
                    hotel_id=str(row["hotel_id"]).strip(),
                    customer_id=str(row["customer_id"]).strip(),
                    created_at=str(row["created_at"]).strip(),
                    canceled_at=row.get("canceled_at"),
                )
                if (not rec.reservation_id
                        or not rec.hotel_id
                        or not rec.customer_id):
                    raise ValueError("missing ids")
                records[rec.reservation_id] = rec
            except (KeyError, ValueError, TypeError) as exc:
                msg = f"Invalid reservation at index {idx}: {exc}"
                print_data_error(msg)
        return records

    def _save(self, records: Dict[str, ReservationRecord]) -> None:
        """
        Persist reservations to JSON storage.

        Args:
            records: Dict of ReservationRecord keyed by reservation_id.
        """
        safe_write_list(self.filepath, [asdict(v) for v in records.values()])

    def create_reservation(
        self,
        reservation_id: str,
        customer_id: str,
        hotel_id: str,
    ) -> None:
        """
        Create a reservation and reserve one room in the specified hotel.

        Args:
            reservation_id: Unique reservation identifier (non-empty).
            customer_id: Existing customer identifier.
            hotel_id: Existing hotel identifier.

        Raises:
            ValueError: If reservation_id is empty/duplicate,
                customer/hotel not
                found, or the hotel has no available rooms.
        """
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

    def cancel_reservation(self, reservation_id: str) -> None:
        """
        Cancel an existing reservation (idempotent) and release the hotel room.

        Args:
            reservation_id: Reservation identifier.

        Raises:
            ValueError: If the reservation does not exist.
        """
        reservations = self._load()
        if reservation_id not in reservations:
            raise ValueError("Reservation not found")

        rec = reservations[reservation_id]
        if rec.canceled_at is not None:
            return  # idempotent

        self.hotels.release_room(rec.hotel_id)
        reservations[reservation_id] = ReservationRecord(
            reservation_id=rec.reservation_id,
            hotel_id=rec.hotel_id,
            customer_id=rec.customer_id,
            created_at=rec.created_at,
            canceled_at=_utc_iso(),
        )
        self._save(reservations)

    def display_reservation(
            self,
            reservation_id: str
            ) -> Optional[ReservationRecord]:
        """
        Retrieve a reservation by id.

        Args:
            reservation_id: Reservation identifier.

        Returns:
            The ReservationRecord if found; otherwise None.
        """
        return self._load().get(reservation_id)
