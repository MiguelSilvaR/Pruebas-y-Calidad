"""
CLI del sistema de reservaciones.

Permite crear/consultar/modificar/eliminar hoteles y clientes, y crear/cancelar
reservaciones. Los datos se almacenan en archivos JSON dentro del directorio
'data'.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from source.Customers import Customers
from source.Hotels import Hotels
from source.Reservation import Reservation


DATA_FILES = ("hotels.json", "customers.json", "reservations.json")


@dataclass
class AppContext:
    """Dependencias compartidas por los handlers del menú."""
    hotels: Hotels
    customers: Customers
    reservations: Reservation


def _ensure_data_dir() -> str:
    """Crea el directorio de datos y archivos JSON vacíos si no existen."""
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    for name in DATA_FILES:
        path = os.path.join(data_dir, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("[]")
    return data_dir


def _menu() -> None:
    """Imprime el menú principal."""
    print("\n--- Reservation System ---")
    print("1) Create Hotel")
    print("2) Display Hotel")
    print("3) Modify Hotel")
    print("4) Delete Hotel")
    print("5) Create Customer")
    print("6) Display Customer")
    print("7) Modify Customer")
    print("8) Delete Customer")
    print("9) Create Reservation")
    print("10) Cancel Reservation")
    print("0) Exit")


def _prompt_optional(prompt: str) -> Optional[str]:
    """Pide un string opcional; retorna None si el usuario deja vacío."""
    value = input(prompt).strip()
    return value or None


def _handle_create_hotel(ctx: AppContext) -> None:
    hid = input("hotel_id: ")
    name = input("name: ")
    loc = input("location: ")
    total = int(input("total_rooms: "))
    ctx.hotels.create_hotel(hid, name, loc, total)
    print("OK")


def _handle_display_hotel(ctx: AppContext) -> None:
    hid = input("hotel_id: ")
    hotel = ctx.hotels.display_hotel(hid)
    print(hotel if hotel else "Not found")


def _handle_modify_hotel(ctx: AppContext) -> None:
    hid = input("hotel_id: ")
    name = _prompt_optional("new name (blank to skip): ")
    loc = _prompt_optional("new location (blank to skip): ")
    total_txt = input("new total_rooms (blank to skip): ").strip()
    total = None if not total_txt else int(total_txt)
    ctx.hotels.modify_hotel(hid, name=name, location=loc, total_rooms=total)
    print("OK")


def _handle_delete_hotel(ctx: AppContext) -> None:
    hid = input("hotel_id: ")
    ctx.hotels.delete_hotel(hid)
    print("OK")


def _handle_create_customer(ctx: AppContext) -> None:
    cid = input("customer_id: ")
    full = input("full_name: ")
    email = input("email: ")
    ctx.customers.create_customer(cid, full, email)
    print("OK")


def _handle_display_customer(ctx: AppContext) -> None:
    cid = input("customer_id: ")
    cust = ctx.customers.display_customer(cid)
    print(cust if cust else "Not found")


def _handle_modify_customer(ctx: AppContext) -> None:
    cid = input("customer_id: ")
    full = _prompt_optional("new full_name (blank to skip): ")
    email = _prompt_optional("new email (blank to skip): ")
    ctx.customers.modify_customer(cid, full_name=full, email=email)
    print("OK")


def _handle_delete_customer(ctx: AppContext) -> None:
    cid = input("customer_id: ")
    ctx.customers.delete_customer(cid)
    print("OK")


def _handle_create_reservation(ctx: AppContext) -> None:
    rid = input("reservation_id: ")
    cid = input("customer_id: ")
    hid = input("hotel_id: ")
    ctx.reservations.create_reservation(rid, cid, hid)
    print("OK")


def _handle_cancel_reservation(ctx: AppContext) -> None:
    rid = input("reservation_id: ")
    ctx.reservations.cancel_reservation(rid)
    print("OK")


def _handle_exit(_: AppContext) -> None:
    print("Bye.")
    raise SystemExit


def _build_handlers() -> Dict[str, Callable[[AppContext], None]]:
    """Construye el mapa de opciones del menú a handlers."""
    return {
        "1": _handle_create_hotel,
        "2": _handle_display_hotel,
        "3": _handle_modify_hotel,
        "4": _handle_delete_hotel,
        "5": _handle_create_customer,
        "6": _handle_display_customer,
        "7": _handle_modify_customer,
        "8": _handle_delete_customer,
        "9": _handle_create_reservation,
        "10": _handle_cancel_reservation,
        "0": _handle_exit,
    }


def main() -> None:
    """Punto de entrada del CLI."""
    data_dir = _ensure_data_dir()

    hotels = Hotels(os.path.join(data_dir, "hotels.json"))
    customers = Customers(os.path.join(data_dir, "customers.json"))
    reservations = Reservation(
        os.path.join(data_dir, "reservations.json"),
        hotels,
        customers,
    )
    ctx = AppContext(
        hotels=hotels,
        customers=customers,
        reservations=reservations
        )

    handlers = _build_handlers()

    while True:
        _menu()
        choice = input("Select option: ").strip()
        handler = handlers.get(choice)

        try:
            if handler is None:
                print("Invalid option")
                continue
            handler(ctx)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
        except SystemExit:
            break


if __name__ == "__main__":
    main()
