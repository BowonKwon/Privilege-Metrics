# -*- coding: utf-8 -*-
"""Re-OCR the Woodcroft scan pages where the Internet Archive OCR lost entry numbers.

  python src/reocr_pages.py [--tesseract PATH]   # pages = every page holding a numbering gap + the page after it

Run after a first build_woodcroft.py (it reads the numbering gaps from woodcroft_parse_log.json), then run
build_woodcroft.py again. tesseract is taken from --tesseract, else the TESSERACT environment variable, else
Library/bin/tesseract.exe next to the Python interpreter (a conda install on Windows), else tesseract on PATH.

Downloads the page image from Internet Archive (page/n{index-1}.jpg) and runs tesseract 5 (eng, psm 4)
to a TSV with word boxes in data/raw/woodcroft/reocr/p{part}_{index:04d}.tsv. build_woodcroft.py reads a
TSV in place of the djvu.xml page when one exists. Pages are listed in reocr/pages.json.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from paths import DER, RAW

OUT = RAW / "woodcroft" / "reocr"
IA = {1: "chronologicalin1617grea_0", 2: "chronologicalind1617grea"}
TESS = None


def tesseract(arg: str = "") -> Path:
    for c in (arg, os.environ.get("TESSERACT", ""), str(Path(sys.executable).parent / "Library" / "bin" / "tesseract.exe"), shutil.which("tesseract") or ""):
        if c and Path(c).exists():
            return Path(c)
    raise FileNotFoundError("tesseract not found: pass --tesseract PATH or set TESSERACT")


def one(pg):
    part, idx = pg
    jpg, tsv = OUT / f"p{part}_{idx:04d}.jpg", OUT / f"p{part}_{idx:04d}.tsv"
    if tsv.exists():
        return pg, "cached"
    if not jpg.exists():
        with urllib.request.urlopen(f"https://archive.org/download/{IA[part]}/page/n{idx - 1}.jpg", timeout=120) as r:
            jpg.write_bytes(r.read())
    subprocess.run([str(TESS), str(jpg), str(tsv.with_suffix("")), "-l", "eng", "--psm", "4", "-c", "tessedit_create_tsv=1", "-c", "tessedit_create_txt=0"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pg, "ok"


def main():
    global TESS
    ap = argparse.ArgumentParser()
    ap.add_argument("--tesseract", default="")
    TESS = tesseract(ap.parse_args().tesseract)
    log = json.loads((DER / "woodcroft_parse_log.json").read_text(encoding="utf-8"))
    pages = sorted({(g["page"][0], g["page"][1] + k) for g in log["gaps"] for k in (0, 1)})
    if (OUT / "pages.json").exists():
        pages = sorted(set(pages) | {tuple(p) for p in json.loads((OUT / "pages.json").read_text())})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pages.json").write_text(json.dumps(pages))
    with ThreadPoolExecutor(4) as ex:
        for pg, st in ex.map(one, pages):
            print(pg, st, flush=True)


if __name__ == "__main__":
    main()
