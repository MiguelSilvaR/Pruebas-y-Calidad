"""
Customers domain module.

Provides the Customers service and CustomerRecord model to manage customer data
with JSON persistence.

Key behaviors:
- Validates customer_id is non-empty and unique on creation.
- Validates email contains '@' on create/modify and while
  loading persisted data.
- Loads data in a best-effort manner: invalid items are
  ignored and reported.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional

from .storage import print_data_error, safe_load_list, safe_write_list


@dataclass(frozen=True)
class CustomerRecord:
    """Immutable customer record persisted to JSON."""
    customer_id: str
    full_name: str
    email: str


class Customers:
    """Service for customer CRUD operations with JSON persistence."""

    def __init__(self, filepath: str) -> None:
        """
        Initialize the customers service.

        Args:
            filepath: Path to the JSON file used for persistence.
        """
        self.filepath = filepath

    def _load(self) -> Dict[str, CustomerRecord]:
        """
        Load customers from JSON storage.

        Returns:
            Dict mapping customer_id to CustomerRecord.

        Notes:
            Invalid/corrupt items are ignored and
            reported via print_data_error,
            and the function continues best-effort.
        """
        records: Dict[str, CustomerRecord] = {}
        for idx, row in enumerate(safe_load_list(self.filepath)):
            try:
                rec = CustomerRecord(
                    customer_id=str(row["customer_id"]).strip(),
                    full_name=str(row["full_name"]).strip(),
                    email=str(row["email"]).strip(),
                )
                if not rec.customer_id or not rec.full_name:
                    raise ValueError("customer_id/full_name empty")
                if "@" not in rec.email:
                    raise ValueError("invalid email")
                records[rec.customer_id] = rec
            except (KeyError, ValueError, TypeError) as exc:
                msg = f"Invalid customer at index {idx}: {exc}"
                print_data_error(msg)
        return records

    def _save(self, records: Dict[str, CustomerRecord]) -> None:
        """
        Persist customers to JSON storage.

        Args:
            records: Dict of CustomerRecord keyed by customer_id.
        """
        safe_write_list(self.filepath, [asdict(v) for v in records.values()])

    # Req 2.2 a-d
    def create_customer(
            self,
            customer_id: str,
            full_name: str,
            email: str) -> None:
        """
        Create a new customer.

        Args:
            customer_id: Unique customer identifier (non-empty).
            full_name: Customer full name (non-empty after strip).
            email: Customer email (must contain '@').

        Raises:
            ValueError: If customer_id is empty/duplicate or email is invalid.
        """
        customers = self._load()
        customer_id = customer_id.strip()
        if not customer_id:
            raise ValueError("customer_id must be non-empty")
        if customer_id in customers:
            raise ValueError("Customer already exists")
        if "@" not in email:
            raise ValueError("invalid email")

        customers[customer_id] = CustomerRecord(
            customer_id=customer_id,
            full_name=full_name.strip(),
            email=email.strip(),
        )
        self._save(customers)

    def delete_customer(self, customer_id: str) -> None:
        """
        Delete an existing customer.

        Args:
            customer_id: Customer identifier.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = self._load()
        if customer_id not in customers:
            raise ValueError("Customer not found")
        del customers[customer_id]
        self._save(customers)

    def display_customer(self, customer_id: str) -> Optional[CustomerRecord]:
        """
        Retrieve a customer by id.

        Args:
            customer_id: Customer identifier.

        Returns:
            CustomerRecord if found; otherwise None.
        """
        return self._load().get(customer_id)

    def modify_customer(
        self,
        customer_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        """
        Modify an existing customer's fields.

        Args:
            customer_id: Customer identifier.
            full_name: New full name (optional).
            email: New email (optional; must contain '@' if provided).

        Raises:
            ValueError: If customer not found or email is invalid.
        """
        customers = self._load()
        if customer_id not in customers:
            raise ValueError("Customer not found")

        old = customers[customer_id]
        new_email = old.email if email is None else email.strip()
        if "@" not in new_email:
            raise ValueError("invalid email")

        customers[customer_id] = CustomerRecord(
            customer_id=old.customer_id,
            full_name=(
                old.full_name
                if full_name is None
                else full_name.strip()
                ),
            email=new_email,
        )
        self._save(customers)
