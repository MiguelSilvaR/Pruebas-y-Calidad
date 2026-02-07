# pylint: disable=invalid-name
#!/usr/bin/env python3
"""
Compute descriptive statistics from a file containing numbers.

Outputs to console and to StatisticsResults.txt:
- Mean
- Median
- Mode
- Variance (population)
- Standard deviation (population)
- Elapsed time
"""

from __future__ import annotations

import math
import sys
import time
from typing import List, Optional, Tuple


RESULTS_FILE = "StatisticsResults.txt"


def parse_numbers_from_file(file_path: str) -> Tuple[List[float], List[str]]:
    """Parse numbers from a text file. Collect errors but keep going."""
    numbers: List[float] = []
    errors: List[str] = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line_no, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            # Accept either "one per line" or "space-separated".
            parts = line.split()
            for part in parts:
                try:
                    numbers.append(float(part))
                except ValueError:
                    errors.append(f"Line {line_no}: invalid number '{part}'")

    return numbers, errors


def mean(values: List[float]) -> Optional[float]:
    """Compute arithmetic mean."""
    if not values:
        return None
    total = 0.0
    for val in values:
        total += val
    return total / len(values)


def median(values: List[float]) -> Optional[float]:
    """Compute median."""
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2

    if n % 2 == 1:
        return sorted_vals[mid]
    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def mode(values: List[float]) -> Optional[str]:
    """
    Compute mode(s).

    Returns:
      - None if no values
      - A string describing:
          - single mode
          - multiple modes
          - or "No mode" if all frequencies are 1
    """
    if not values:
        return None

    frequencies: dict[float, int] = {}
    for val in values:
        frequencies[val] = frequencies.get(val, 0) + 1

    max_freq = 0
    for freq in frequencies.values():
        max_freq = max(max_freq, freq)

    if max_freq == 1:
        return "No mode (all values appear once)."

    modes: List[float] = []
    for val, freq in frequencies.items():
        if freq == max_freq:
            modes.append(val)

    modes_sorted = sorted(modes)
    if len(modes_sorted) == 1:
        return f"{modes_sorted[0]} (frequency={max_freq})"
    return f"{modes_sorted} (frequency={max_freq})"


def variance_sample(values: List[float]) -> Optional[float]:
    """Compute sample variance."""
    n = len(values)
    if n < 2:
        return None

    mu = mean(values)
    acc = 0.0
    for val in values:
        diff = val - mu
        acc += diff ** 2

    return acc / (n - 1)


def variance_population(values: List[float]) -> Optional[float]:
    """Compute population variance."""
    if not values:
        return None
    mu = mean(values)
    if mu is None:
        return None

    acc = 0.0
    for val in values:
        diff = val - mu
        acc += diff * diff
    return acc / len(values)


def std_dev_population(values: List[float]) -> Optional[float]:
    """Compute population standard deviation."""
    var = variance_population(values)
    if var is None:
        return None
    return math.sqrt(var)


def build_report(
    file_path: str,
    values: List[float],
    errors: List[str],
    elapsed_seconds: float,
) -> str:
    """Build output report string."""
    lines: List[str] = []
    lines.append(f"Input file: {file_path}")
    lines.append(f"Valid numbers: {len(values)}")
    lines.append(f"Invalid items: {len(errors)}")
    lines.append("")

    if errors:
        lines.append("Invalid data (execution continued):")
        for err in errors:
            lines.append(f"  - {err}")
        lines.append("")

    if not values:
        lines.append("No valid numeric data found. Cannot compute statistics.")
        lines.append(f"Elapsed time (s): {elapsed_seconds:.6f}")
        return "\n".join(lines)

    lines.append(f"Count: {len(values) + len(errors)}")
    lines.append(f"Mean: {mean(values):.6f}")
    lines.append(f"Median: {median(values):.6f}")

    mode_text = mode(values)
    lines.append(f"Mode: {mode_text}")

    var = variance_sample(values)
    std = std_dev_population(values)
    lines.append(f"Standard deviation: {std:.6f}")
    lines.append(f"Variance: {var:.6f}")
    lines.append("")
    lines.append(f"Elapsed time (s): {elapsed_seconds:.6f}")

    return "\n".join(lines)


def main() -> int:
    """Entry point."""
    if len(sys.argv) != 2:
        print("Usage: python computeStatistics.py fileWithData.txt")
        return 1

    file_path = sys.argv[1]
    start = time.perf_counter()

    try:
        values, errors = parse_numbers_from_file(file_path)
    except OSError as exc:
        print(f"Error opening file: {exc}")
        return 1

    elapsed = time.perf_counter() - start
    report = build_report(file_path, values, errors, elapsed)

    print(report)
    with open(RESULTS_FILE, "w", encoding="utf-8") as out:
        out.write(report + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
