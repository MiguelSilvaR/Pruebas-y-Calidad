from __future__ import annotations

import os

from source.Customers import Customers
from source.Hotels import Hotels
from source.Reservation import Reservation


def _ensure_data_dir() -> str:
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    # crea archivos vacíos si no existen
    for name in ("hotels.json", "customers.json", "reservations.json"):
        path = os.path.join(data_dir, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("[]")
    return data_dir


def _menu() -> None:
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


def main() -> None:
    data_dir = _ensure_data_dir()
    hotels = Hotels(os.path.join(data_dir, "hotels.json"))
    customers = Customers(os.path.join(data_dir, "customers.json"))
    reservations = Reservation(os.path.join(data_dir, "reservations.json"), hotels, customers)

    while True:
        _menu()
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                hid = input("hotel_id: ")
                name = input("name: ")
                loc = input("location: ")
                total = int(input("total_rooms: "))
                hotels.create_hotel(hid, name, loc, total)
                print("OK")

            elif choice == "2":
                hid = input("hotel_id: ")
                h = hotels.display_hotel(hid)
                print(h if h else "Not found")

            elif choice == "3":
                hid = input("hotel_id: ")
                name = input("new name (blank to skip): ").strip() or None
                loc = input("new location (blank to skip): ").strip() or None
                total_txt = input("new total_rooms (blank to skip): ").strip()
                total = None if not total_txt else int(total_txt)
                hotels.modify_hotel(hid, name=name, location=loc, total_rooms=total)
                print("OK")

            elif choice == "4":
                hid = input("hotel_id: ")
                hotels.delete_hotel(hid)
                print("OK")

            elif choice == "5":
                cid = input("customer_id: ")
                full = input("full_name: ")
                email = input("email: ")
                customers.create_customer(cid, full, email)
                print("OK")

            elif choice == "6":
                cid = input("customer_id: ")
                c = customers.display_customer(cid)
                print(c if c else "Not found")

            elif choice == "7":
                cid = input("customer_id: ")
                full = input("new full_name (blank to skip): ").strip() or None
                email = input("new email (blank to skip): ").strip() or None
                customers.modify_customer(cid, full_name=full, email=email)
                print("OK")

            elif choice == "8":
                cid = input("customer_id: ")
                customers.delete_customer(cid)
                print("OK")

            elif choice == "9":
                rid = input("reservation_id: ")
                cid = input("customer_id: ")
                hid = input("hotel_id: ")
                reservations.create_reservation(rid, cid, hid)
                print("OK")

            elif choice == "10":
                rid = input("reservation_id: ")
                reservations.cancel_reservation(rid)
                print("OK")

            elif choice == "0":
                print("Bye.")
                break
            else:
                print("Invalid option")

        except ValueError as exc:
            print(f"[ERROR] {exc}")


if __name__ == "__main__":
    main()