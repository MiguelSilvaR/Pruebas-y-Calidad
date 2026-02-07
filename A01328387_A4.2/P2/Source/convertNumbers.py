# pylint: disable=invalid-name
#!/usr/bin/env python3
"""
convertNumbers.py

Convert integers from a file to binary and hexadecimal.

Rules:
- Negative numbers:
    * Represent using two's complement with a fixed 64-bit limit.
    * Output must be ONLY 10 characters:
        - BIN: last 10 bits (LSBs) of the 64-bit pattern.
        - HEX: last 10 hex characters of the 64-bit pattern.
- Positive numbers:
    * No bit-width restriction.
    * No padding added.
    * No trimming (print full minimal representation).
"""

from __future__ import annotations

import sys
import time
from typing import List, Tuple

RESULTS_FILE = "ConvertionResults.txt"
HEX_DIGITS = "0123456789ABCDEF"

NEG_BITS = 64
NEG_MASK = (1 << NEG_BITS) - 1

NEG_OUT_CHARS = 10  # Only negatives are trimmed to 10 chars (BIN and HEX)


def parse_integers_from_file(file_path: str) -> Tuple[List[int], List[str]]:
    """Parse integers from file. Keep errors and continue."""
    values: List[int] = []
    errors: List[str] = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line_no, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            for token in line.split():
                try:
                    values.append(int(token))
                except ValueError:
                    errors.append(f"Line {line_no}: invalid integer '{token}'")

    return values, errors


def to_base_unsigned(value: int, base: int) -> str:
    """Convert a NON-negative integer to a string in the given base (2..16)."""
    if base < 2 or base > 16:
        raise ValueError("Base must be between 2 and 16")

    if value == 0:
        return "0"

    digits: List[str] = []
    n = value
    while n > 0:
        remainder = n % base
        digits.append(HEX_DIGITS[remainder])
        n //= base

    digits.reverse()
    return "".join(digits)


def twos_complement_64bit(n: int) -> int:
    """Return the unsigned 64-bit two's complement representation of n."""
    return n & NEG_MASK


def rightmost(text: str, width: int) -> str:
    """Return the rightmost 'width' characters."""
    return text[-width:]


def format_negative(n: int) -> Tuple[str, str]:
    """
    Format negative number:
    - BIN: last 10 bits from 64-bit two's complement (10 chars)
    - HEX: last 10 hex chars from 64-bit two's complement (10 chars)
    """
    u64 = twos_complement_64bit(n)

    bin_full = to_base_unsigned(u64, 2).zfill(NEG_BITS)  # internal 64-bit view
    bin_out = rightmost(bin_full, NEG_OUT_CHARS)

    hex_full = to_base_unsigned(u64, 16).zfill(16).upper()  # 64-bit => 16 hex digits
    # If 64-bit hex is only 16 digits, rightmost(16,10) gives exactly 10 chars
    hex_out = rightmost(hex_full, NEG_OUT_CHARS)

    return bin_out, hex_out


def format_positive(n: int) -> Tuple[str, str]:
    """Format positive integer without padding and without trimming."""
    bin_str = to_base_unsigned(n, 2)
    hex_str = to_base_unsigned(n, 16).upper()
    return bin_str, hex_str


def build_report(values: List[int], errors: List[str], elapsed_seconds: float) -> str:
    """Build output report."""
    lines: List[str] = []
    lines.append("ID\tDEC\tBIN\tHEX")

    for idx, dec in enumerate(values, start=1):
        try:
            if dec < 0:
                bin_out, hex_out = format_negative(dec)
            else:
                bin_out, hex_out = format_positive(dec)

            lines.append(f"{idx}\t{dec}\t{bin_out}\t{hex_out}")
        except ValueError as exc:
            lines.append(f"{idx}\t{dec}\tERROR\t{exc}")

    if errors:
        lines.append("")
        lines.append("Invalid data (execution continued):")
        for err in errors:
            lines.append(f"\t- {err}")

    lines.append("")
    lines.append(f"Elapsed time (s):\t{elapsed_seconds:.6f}")
    lines.append("Rule:\tNegatives=2's complement 64-bit; output trimmed to 10 chars only")

    return "\n".join(lines)


def main() -> int:
    """Entry point."""
    if len(sys.argv) != 2:
        print("Usage: python convertNumbers.py fileWithData.txt")
        return 1

    file_path = sys.argv[1]
    start = time.perf_counter()

    try:
        values, errors = parse_integers_from_file(file_path)
    except OSError as exc:
        print(f"Error opening file: {exc}")
        return 1

    elapsed = time.perf_counter() - start
    report = build_report(values, errors, elapsed)

    print(report)
    with open(RESULTS_FILE, "w", encoding="utf-8") as out:
        out.write(report + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
