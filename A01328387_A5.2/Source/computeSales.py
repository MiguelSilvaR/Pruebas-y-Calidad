#!/usr/bin/env python3
"""computeSales.py

Compute the total cost for all sales records, given:
1) A JSON catalogue of products and prices.
2) A JSON file with sales records (product + quantity).

Usage:
    python computeSales.py priceCatalogue.json salesRecord.json

The program prints a human-readable report to the console and writes the same
report to a file named 'SalesResults.txt'.

Requirements implemented:
- Command-line invocation with two file parameters.
- Computes total considering catalogue prices.
- Handles invalid data and keeps running, reporting errors to console.
- Includes elapsed execution time.
- PEP 8 compliant.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


RESULTS_FILENAME = "SalesResults.txt"


@dataclass
class Stats:
    """Execution statistics."""

    total_items: int = 0
    valid_items: int = 0
    errors: int = 0


def _safe_load_json(path: Path) -> Any:
    """Load JSON from *path*. On error, print and return None."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
    except PermissionError:
        print(f"ERROR: Permission denied: {path}", file=sys.stderr)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {path}: {exc}", file=sys.stderr)
    except OSError as exc:
        print(f"ERROR: Could not read {path}: {exc}", file=sys.stderr)
    return None


def _build_price_map(catalogue: Any) -> Dict[str, float]:
    """Convert catalogue JSON into a {title: price} dict.

    Expected catalogue format: list of dicts with keys 'title' and 'price'.
    Invalid entries are ignored with an error printed to stderr.
    """
    prices: Dict[str, float] = {}

    if not isinstance(catalogue, list):
        print(
            "ERROR: Price catalogue JSON must be a list of product objects.",
            file=sys.stderr,
        )
        return prices

    for idx, item in enumerate(catalogue, start=1):
        if not isinstance(item, dict):
            print(
                f"ERROR: Catalogue item #{idx} is not an object; skipping.",
                file=sys.stderr,
            )
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or not title.strip():
            print(
                f"ERROR: Catalogue item #{idx} has invalid 'title'; skipping.",
                file=sys.stderr,
            )
            continue

        try:
            price_f = float(price)
        except (TypeError, ValueError):
            print(
                f"ERROR: Catalogue item '{title}' has invalid 'price'; "
                "skipping.",
                file=sys.stderr,
            )
            continue

        prices[title] = price_f

    return prices


def _iter_sales_records(sales_data: Any) -> Iterable[Dict[str, Any]]:
    """Yield sales records as dicts from loaded JSON."""
    if not isinstance(sales_data, list):
        print(
            "ERROR: Sales record JSON must be a list of sale objects.",
            file=sys.stderr,
        )
        return []

    for idx, rec in enumerate(sales_data, start=1):
        if not isinstance(rec, dict):
            print(
                f"ERROR: Sales record #{idx} is not an object; skipping.",
                file=sys.stderr,
            )
            continue
        yield rec


def compute_total_cost(
    prices: Dict[str, float],
    sales_records: Iterable[Dict[str, Any]],
) -> Tuple[float, Stats]:
    """Compute the total cost across all sales records."""
    total = 0.0
    stats = Stats()

    for rec in sales_records:
        stats.total_items += 1

        product = rec.get("Product")
        quantity = rec.get("Quantity")

        if not isinstance(product, str) or not product.strip():
            stats.errors += 1
            print(
                f"ERROR: Sales record missing/invalid 'Product': {rec}",
                file=sys.stderr,
            )
            continue

        try:
            qty_i = int(quantity)
        except (TypeError, ValueError):
            stats.errors += 1
            print(
                f"ERROR: Invalid 'Quantity' for product '{product}': {rec}",
                file=sys.stderr,
            )
            continue

        price = prices.get(product)
        if price is None:
            stats.errors += 1
            print(
                f"ERROR: Product not found in catalogue: '{product}'",
                file=sys.stderr,
            )
            continue

        total += price * qty_i
        stats.valid_items += 1

    return total, stats


def _format_report(
    catalogue_path: Path,
    sales_path: Path,
    total: float,
    stats: Stats,
    elapsed_s: float,
) -> str:
    """Return a human-readable report string."""
    lines: List[str] = []
    lines.append("Compute Sales Results")
    lines.append("-" * 60)
    lines.append(f"Price catalogue: {catalogue_path}")
    lines.append(f"Sales record:    {sales_path}")
    lines.append("")
    lines.append(f"Records processed: {stats.total_items}")
    lines.append(f"Valid records:     {stats.valid_items}")
    lines.append(f"Errors:            {stats.errors}")
    lines.append("")
    lines.append(f"TOTAL: ${total:,.2f}")
    lines.append(f"Elapsed time: {elapsed_s:.6f} s")
    lines.append("-" * 60)
    return "\n".join(lines) + "\n"


def _write_results(report: str, out_path: Path) -> None:
    """Write report to output file, printing errors if writing fails."""
    try:
        out_path.write_text(report, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write results file: {exc}", file=sys.stderr)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compute total cost for all sales in a JSON file."
    )
    parser.add_argument(
        "price_catalogue",
        type=Path,
        help="JSON file with products and prices",
    )
    parser.add_argument(
        "sales_record",
        type=Path,
        help="JSON file with sales records (Product + Quantity)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Program entry point."""
    args = parse_args(argv)

    start = time.perf_counter()

    catalogue_json = _safe_load_json(args.price_catalogue)
    prices = _build_price_map(catalogue_json)

    sales_json = _safe_load_json(args.sales_record)
    sales_records = _iter_sales_records(sales_json)

    total, stats = compute_total_cost(prices, sales_records)

    elapsed_s = time.perf_counter() - start
    report = _format_report(
        args.price_catalogue, args.sales_record, total, stats, elapsed_s
    )

    print(report, end="")
    _write_results(report, Path(RESULTS_FILENAME))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
