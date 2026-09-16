#!/usr/bin/env python3
"""Generate dash-separated IDs: `<prefix>{mmm-dddd-rrrrr}`.

Format: a `t` or `c` prefix, then the 7-digit zero-padded count of
minutes since the epoch split 3+4 (e.g. `005-4321`), a dash, then 5
random decimal digits — e.g. `t005-4321-48213`.
"""

import argparse
import datetime
import os
import random
import sys

MINUTE_CAP = 10_000_000  # 7-digit counter caps just under ~19 years


def die(message):
    print(f"generate-id: {message}", file=sys.stderr)
    sys.exit(1)


def parse_epoch(epoch_str):
    """Parse an epoch string into a timezone-aware UTC datetime.

    Accepts ISO 8601 with `Z` or an explicit offset, and bare
    `YYYY-MM-DD[ T]HH:MM:SS` date-times (assumed UTC), with the same
    tolerance as the previous tool.
    """
    try:
        dt = datetime.datetime.fromisoformat(epoch_str.strip().replace("Z", "+00:00"))
    except ValueError:
        die(
            f"cannot parse epoch: {epoch_str!r} — expected ISO 8601 with `Z` "
            "or an explicit offset, or a bare 'YYYY-MM-DD HH:MM:SS' (UTC)"
        )
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def read_epoch():
    """Read the default epoch from tools/.epoch next to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, ".epoch"), "r") as f:
        return f.read().strip()


def minutes_since(epoch_dt, now=None):
    """Floor the minute count between now (UTC) and the epoch."""
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    return (now - epoch_dt) // datetime.timedelta(minutes=1)


def used_in_dir(dir_path, candidate):
    """True if dir_path holds an entry whose name starts with `{candidate}-`."""
    return any(name.startswith(candidate + "-") for name in os.listdir(dir_path))


def mint_ids(prefix, minutes_part, count, dir_path=None):
    """Mint `count` unique ids sharing one minute part, sorted ascending."""
    prefix = prefix + minutes_part + "-"
    if dir_path is not None and not os.path.isdir(dir_path):
        die(f"--dir path does not exist: {dir_path}")
    batch = set()
    while len(batch) < count:
        candidate = prefix + f"{random.randint(0, 99999):05d}"
        if candidate in batch:
            continue
        if dir_path is not None and used_in_dir(dir_path, candidate):
            continue
        batch.add(candidate)
    return sorted(batch)


def main():
    parser = argparse.ArgumentParser(
        description="Generate dash-separated ids: <prefix>{mmm-dddd-rrrrr} "
        "(7-digit minutes since epoch, split 3+4, plus 5 random digits)."
    )
    parser.add_argument("--count", type=int, default=1, help="number of ids (default: 1)")
    parser.add_argument("--epoch", type=str, default=None, help="override the epoch (default: tools/.epoch next to the script)")
    parser.add_argument("--prefix", choices=("t", "c"), default="t", help="id prefix (default: t)")
    parser.add_argument("--dir", type=str, default=None, help="check minted ids against this existing directory of {id}-{name} files")
    args = parser.parse_args()

    if args.count < 1:
        die("--count must be >= 1")

    epoch_str = args.epoch if args.epoch is not None else read_epoch()
    epoch_dt = parse_epoch(epoch_str)

    minutes = minutes_since(epoch_dt)
    if minutes < 0:
        die(f"epoch is in the future ({epoch_str}); minutes-since-epoch is negative")
    if minutes >= MINUTE_CAP:
        die(
            f"minute counter overflow: {minutes} >= {MINUTE_CAP} — the 7-digit "
            "id space is exhausted; choose a later epoch"
        )

    minutes_part = f"{minutes:07d}"[:3] + "-" + f"{minutes:07d}"[3:]
    for id_str in mint_ids(args.prefix, minutes_part, args.count, args.dir):
        print(id_str)


if __name__ == "__main__":
    main()
