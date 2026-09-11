#!/usr/bin/env python3
"""Generate compact 8-char IDs per ADR05: 5-char base-36 timestamp + 3-char base-36 random suffix."""

import argparse
import datetime
import os
import random
import sys

BASE36_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
TIMESTAMP_CHARS = 5
RANDOM_CHARS = 3
TOTAL_CHARS = TIMESTAMP_CHARS + RANDOM_CHARS


def to_base36(value, width=TIMESTAMP_CHARS):
    """Convert a non-negative integer to a zero-padded base-36 string."""
    if value < 0:
        raise ValueError("Value must be non-negative")
    if value == 0:
        return BASE36_CHARS[0] * width
    digits = []
    while value > 0:
        digits.append(BASE36_CHARS[value % 36])
        value //= 36
    result = "".join(reversed(digits))
    return result.zfill(width)


def random_base36(n=RANDOM_CHARS):
    """Generate n random base-36 characters."""
    return "".join(random.choices(BASE36_CHARS, k=n))


def read_epoch():
    """Read the default epoch from LAAW/tools/.epoch."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    epoch_path = os.path.join(script_dir, ".epoch")
    with open(epoch_path, "r") as f:
        return f.read().strip()


def parse_epoch(epoch_str):
    """Parse an epoch string into a timezone-aware datetime."""
    # Handle format: "YYYY-MM-DD HH:MM:SS ±HHMM"
    try:
        dt = datetime.datetime.strptime(epoch_str, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        # Try without timezone, assume UTC if not specified
        try:
            dt = datetime.datetime.strptime(epoch_str, "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            raise ValueError(
                f"Cannot parse epoch string: {epoch_str}. "
                "Expected format: 'YYYY-MM-DD HH:MM:SS ±HHMM'"
            )
    return dt


def generate_id(epoch_dt, count=1):
    """Generate one or more 8-char IDs within the same minute bucket."""
    now = datetime.datetime.now(datetime.timezone.utc)
    # Calculate total minutes since epoch
    delta = now - epoch_dt
    total_minutes = int(delta.total_seconds() / 60)
    timestamp_part = to_base36(total_minutes)

    if count == 1:
        random_part = random_base36()
        return [timestamp_part + random_part]

    # For multiple IDs, generate all within the same minute bucket
    ids = []
    for _ in range(count):
        random_part = random_base36()
        ids.append(timestamp_part + random_part)

    # Sort numerically (by base-36 value, which is lexicographic for same-length strings)
    ids.sort(key=lambda x: int(x, 36))
    return ids


def main():
    parser = argparse.ArgumentParser(
        description="Generate compact 8-char IDs (5-char base-36 timestamp + 3-char base-36 random)."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of IDs to generate (default: 1)",
    )
    parser.add_argument(
        "--epoch",
        type=str,
        default=None,
        help='Override the default epoch (format: "YYYY-MM-DD HH:MM:SS ±HHMM")',
    )

    args = parser.parse_args()

    if args.epoch:
        epoch_dt = parse_epoch(args.epoch)
    else:
        epoch_str = read_epoch()
        epoch_dt = parse_epoch(epoch_str)

    ids = generate_id(epoch_dt, args.count)
    for id_str in ids:
        print(id_str)


if __name__ == "__main__":
    main()
