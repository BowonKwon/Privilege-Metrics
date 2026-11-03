# -*- coding: utf-8 -*-
"""Folder layout shared by every script.

Two layouts hold the same files:
  build layout   data/derived/  data/coding/  data/raw/  site/
  public layout  data/          coding/       data/raw/  docs/    (the published repository)
The layout is detected from the folders present (data/derived/ means the build layout) and can be forced with the
environment variable PRIVILEGE_METRICS_LAYOUT=build|public. In the public layout the record tables are gzipped
(data/woodcroft_entries.csv.gz) and the Stationers' Register tables sit in data/sro/; find() looks in both places.
A required file that is missing is an error, never a silent skip.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYOUT = os.environ.get("PRIVILEGE_METRICS_LAYOUT") or ("build" if (ROOT / "data" / "derived").is_dir() else "public")
if LAYOUT == "build":
    DER, COD, OUT = ROOT / "data" / "derived", ROOT / "data" / "coding", ROOT / "site"
elif LAYOUT == "public":
    DER, COD, OUT = ROOT / "data", ROOT / "coding", ROOT / "docs"
else:
    raise SystemExit(f"PRIVILEGE_METRICS_LAYOUT must be 'build' or 'public', not {LAYOUT!r}")
RAW = ROOT / "data" / "raw"
REL = COD / "reliability"
BUNING_XLSX = RAW / "buning" / "patents-dutch-republic-1581-1621.xlsx"


def find(base: Path, name: str) -> Path:
    """base/name, its .gz copy, or the same under base/sro/. Raises FileNotFoundError when none exists."""
    for c in (base / name, base / (name + ".gz"), base / "sro" / name, base / "sro" / (name + ".gz")):
        if c.exists():
            return c
    raise FileNotFoundError(f"required input {name} not found under {base} ({LAYOUT} layout)")


def need(p: Path) -> Path:
    """Return p, or stop with a clear message when a required input is missing."""
    if not p.exists():
        raise FileNotFoundError(f"required input missing: {p} ({LAYOUT} layout)")
    return p
