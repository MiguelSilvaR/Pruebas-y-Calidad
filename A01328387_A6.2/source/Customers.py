from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


def _print_data_error(message: str) -> None:
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
class CustomerRecord:
    customer_id: str
    full_name: str
    email: str


class Customers:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def _load(self) -> Dict[str, CustomerRecord]:
        records: Dict[str, CustomerRecord] = {}
        for idx, row in enumerate(_safe_load_list(self.filepath)):
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
                _print_data_error(f"Invalid customer at index {idx}: {exc}")
        return records

    def _save(self, records: Dict[str, CustomerRecord]) -> None:
        _safe_write_list(self.filepath, [asdict(v) for v in records.values()])

    # Req 2.2 a-d
    def create_customer(self, customer_id: str, full_name: str, email: str) -> None:
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
        customers = self._load()
        if customer_id not in customers:
            raise ValueError("Customer not found")
        del customers[customer_id]
        self._save(customers)

    def display_customer(self, customer_id: str) -> Optional[CustomerRecord]:
        return self._load().get(customer_id)

    def modify_customer(
        self,
        customer_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        customers = self._load()
        if customer_id not in customers:
            raise ValueError("Customer not found")

        old = customers[customer_id]
        new_email = old.email if email is None else email.strip()
        if "@" not in new_email:
            raise ValueError("invalid email")

        customers[customer_id] = CustomerRecord(
            customer_id=old.customer_id,
            full_name=old.full_name if full_name is None else full_name.strip(),
            email=new_email,
        )
        self._save(customers)
