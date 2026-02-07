# pylint: disable=invalid-name
#!/usr/bin/env python3
"""
wordCount.py

Count distinct words and their frequency from a file.

Outputs to console and to WordCountResults.txt using basic algorithms:
- Total distinct words
- Word frequencies sorted by:
    1) frequency (descending)
    2) word (ascending, alphabetical) as tie-breaker
- Elapsed time
"""

from __future__ import annotations

import sys
import time
from typing import Dict, List, Tuple

RESULTS_FILE = "WordCountResults.txt"


def normalize_word(token: str) -> str:
    """
    Normalize tokens to words:
    - Lowercase
    - Strip common punctuation from both ends
    """
    punctuation = ".,;:!?\"'()[]{}<>"
    return token.strip(punctuation).lower()


def parse_words_from_file(file_path: str) -> Tuple[List[str], List[str]]:
    """Parse words from file and return (words, errors)."""
    words: List[str] = []
    errors: List[str] = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line:
                    continue

                for token in line.split():
                    word = normalize_word(token)
                    if word:
                        words.append(word)
    except OSError as exc:
        errors.append(f"File error: {exc}")
    except UnicodeDecodeError:
        errors.append("File encoding error: could not decode as UTF-8.")

    return words, errors


def count_frequencies(words: List[str]) -> Dict[str, int]:
    """Count word frequencies using a basic dictionary algorithm."""
    freq: Dict[str, int] = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq


def sort_by_frequency(freq: Dict[str, int]) -> List[Tuple[str, int]]:
    """
    Sort by:
    1) frequency descending
    2) word ascending (alphabetical) as tie-breaker
    """
    items = list(freq.items())
    items.sort(key=lambda item: (-item[1], item[0]))
    return items


def build_report(
    file_path: str,
    freq: Dict[str, int],
    errors: List[str],
    elapsed_seconds: float,
    total_count: int,
) -> str:
    """Build output report string."""
    lines: List[str] = []
    lines.append(f"Input file: {file_path}")
    lines.append(f"Distinct words: {len(freq)}")
    lines.append(f"Errors: {len(errors)}")
    lines.append("")

    if errors:
        lines.append("Errors (execution continued when possible):")
        for err in errors:
            lines.append(f"  - {err}")
        lines.append("")

    lines.append("Word frequencies (sorted by frequency desc, then word asc):")
    for word, count in sort_by_frequency(freq):
        lines.append(f"{word}: {count}")

    lines.append("")
    lines.append(f"Count: {total_count}")
    lines.append("")
    lines.append(f"Elapsed time (s): {elapsed_seconds:.6f}")
    return "\n".join(lines)


def main() -> int:
    """Entry point."""
    if len(sys.argv) != 2:
        print("Usage: python wordCount.py fileWithData.txt")
        return 1

    file_path = sys.argv[1]
    start = time.perf_counter()

    words, errors = parse_words_from_file(file_path)
    freq = count_frequencies(words)

    elapsed = time.perf_counter() - start
    total_count = len(words)
    report = build_report(file_path, freq, errors, elapsed, total_count)

    print(report)
    with open(RESULTS_FILE, "w", encoding="utf-8") as out:
        out.write(report + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
