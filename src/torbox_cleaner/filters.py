"""Size parsing and item filtering."""

from __future__ import annotations

import re
from collections.abc import Iterable

from torbox_cleaner.api import Item

_UNITS = {
    "": 1,
    "B": 1,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
    "TB": 1000**4,
    "KIB": 1024,
    "MIB": 1024**2,
    "GIB": 1024**3,
    "TIB": 1024**4,
}
_SIZE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([A-Za-z]*)\s*$")


def parse_size(text: str) -> int:
    """Parse '50GB', '1.5 TiB', '500mb' or a raw byte count into bytes.

    KB/MB/GB/TB are decimal (powers of 1000, as the TorBox dashboard shows);
    KiB/MiB/GiB/TiB are binary (powers of 1024).
    """
    m = _SIZE_RE.match(text)
    if not m:
        raise ValueError(f"invalid size: {text!r}")
    number, unit = m.groups()
    unit = unit.upper()
    if unit not in _UNITS:
        raise ValueError(f"unknown size unit {unit!r} in {text!r}")
    return int(float(number) * _UNITS[unit])


def format_size(n: int) -> str:
    if n < 0:  # TorBox reports -1 while metadata is still being fetched
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1000 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1000
    raise AssertionError("unreachable")


def select(items: Iterable[Item], *, min_size: int | None = None, names: list[str] | None = None) -> list[Item]:
    """Keep items larger than ``min_size`` bytes AND whose name contains any of ``names``.

    Name matching is a case-insensitive substring match.
    """
    needles = [n.lower() for n in names or []]
    out = []
    for item in items:
        if min_size is not None and item.size <= min_size:
            continue
        if needles and not any(n in item.name.lower() for n in needles):
            continue
        out.append(item)
    return out
