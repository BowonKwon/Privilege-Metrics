# -*- coding: utf-8 -*-
"""Draw the reliability samples (fixed seed) and prepare blind coding inputs. Our extracted values are NOT written
into the coder inputs; they are kept in *_key.csv for the comparison in reliability.py.

  python src/reliability_samples.py

R1 image check   120 Woodcroft entries, 30 per period stratum, read from the page images (number, date, first surname,
                 number of grantees, 'communication', stated term)
R2 text coding   200 parsed Woodcroft grants, stratified by our field (11 per field, 'other' 25): field, foreign address,
                 communication, stated term, read from the OCR text
R3 Fulin recode  40 Fulin numbers drawn at random: recoded from the OCR text under the same codebook
R2c text coding  (1.0.3, field dictionary r5) 212 parsed Woodcroft grants, stratified by the r5 field (11 per field,
                 'other' 25), seed 20261107, entries already in R2 or R2b excluded: field only, read from the text.
                 Run with --r2c; the other samples are not redrawn.
"""
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from paths import COD, DER, REL, find  # noqa: F401
IA = {1: "chronologicalin1617grea_0", 2: "chronologicalind1617grea"}
rng = np.random.default_rng(20261103)


def r2c():
    """Fresh sample for the r5 dictionary: the sample that prompted r5 (R2b) is not reused."""
    import fields
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    used = set(pd.read_csv(REL / "r2_key_dictr3.csv")["number"]) | set(pd.read_csv(REL / "r2b_key.csv")["number"])
    G = W[W["parsed"] & (W["kind"] == "grant") & ~W["number"].isin(used)]
    g = np.random.default_rng(20261107)
    parts = [G[G["field"] == f].sample(min(25 if f == "other" else 11, int((G["field"] == f).sum())), random_state=int(g.integers(1e9)))
             for f in fields.FIELD_ORDER]
    r = pd.concat(parts).sample(frac=1, random_state=int(g.integers(1e9)))
    r[["number", "text"]].to_csv(REL / "r2c_text_input.csv", index=False)
    r[["number", "year", "field"]].to_csv(REL / "r2c_key.csv", index=False)
    (REL / "field_list_r5.txt").write_text("".join(f"{i}. {k} — {fields.LABEL[k]['en']}\n" for i, k in enumerate(fields.FIELD_ORDER[:-1], 1)), encoding="utf-8")
    print("R2c", len(r), "overlap with R2/R2b:", len(set(r["number"]) & used))


def main():
    REL.mkdir(parents=True, exist_ok=True)
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    P = W[W["parsed"]].copy()
    # R1
    strata = [(1617, 1699), (1700, 1799), (1800, 1829), (1830, 1853)]
    r1 = pd.concat([P[P["year"].between(a, b)].sample(30, random_state=int(rng.integers(1e9))) for a, b in strata]).sort_values("number")
    imgdir = REL / "pages"
    imgdir.mkdir(exist_ok=True)
    paths = []
    for _, r in r1.iterrows():
        f = imgdir / f"p{int(r.part)}_{int(r.scan_page):04d}.jpg"
        nxt = imgdir / f"p{int(r.part)}_{int(r.scan_page) + 1:04d}.jpg"
        last_on_page = W[(W["part"] == r.part) & (W["scan_page"] == r.scan_page)]["number"].max() == r.number
        need = [(int(r.scan_page), f)] + ([(int(r.scan_page) + 1, nxt)] if last_on_page else [])
        for pg, ff in need:
            for attempt in range(5):
                if ff.exists():
                    break
                try:
                    with urllib.request.urlopen(f"https://archive.org/download/{IA[int(r.part)]}/page/n{pg - 1}.jpg", timeout=120) as resp:
                        ff.write_bytes(resp.read())
                except Exception:
                    import time
                    time.sleep(10 * (attempt + 1))
        paths.append(f"{f.name}" + (f" (entry may continue on {nxt.name})" if last_on_page else ""))
    r1_in = pd.DataFrame({"number": r1["number"].values, "page_image": paths})
    r1_in.to_csv(REL / "r1_image_input.csv", index=False)
    r1[["number", "date", "year", "margin_names", "n_grantees", "communication", "term_years", "kind"]].to_csv(REL / "r1_key.csv", index=False)
    # R2
    G = P[P["kind"] == "grant"]
    parts = []
    for f, g in G.groupby("field"):
        k = 25 if f == "other" else 11
        parts.append(g.sample(min(k, len(g)), random_state=int(rng.integers(1e9))))
    r2 = pd.concat(parts).sample(frac=1, random_state=7)
    r2[["number", "text"]].to_csv(REL / "r2_text_input.csv", index=False)
    r2[["number", "year", "field", "foreign_address", "communication", "term_years"]].to_csv(REL / "r2_key.csv", index=False)
    # R3
    r3 = sorted(np.random.default_rng(3).choice(np.arange(1, 257), 40, replace=False).tolist())   # own seed: independent of R1/R2 draws
    (REL / "r3_fulin_numbers.json").write_text(json.dumps(r3))
    print("R1", len(r1), "images", len(list(imgdir.glob('*.jpg'))), "R2", len(r2), "R3", r3)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    r2c() if "--r2c" in sys.argv else main()
