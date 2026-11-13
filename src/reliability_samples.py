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
R2d text coding  (1.0.6, field dictionary r6) same design as R2c: 212 parsed Woodcroft grants, stratified by the r6 field
                 (11 per field, 'other' 25), seed 20261113 (fixed and committed before the draw), entries already in R2,
                 R2b or R2c excluded. The key keeps the r6 and the r5 field of every item (r5 frozen in
                 coding/reliability/field_r5.csv) so that both dictionaries are measured on the same items. The shuffled sample
                 is split in two halves of 106 (coder 1: rows 1-106, coder 2: rows 107-212), as in R2c.
                 Run with --r2d; then --r2d-packets OUTDIR writes the two blind packets (text and field list only).
R2d-chg          (1.0.6) 60 entries drawn from the grants whose field changed from r5 to r6 (595 rows), entries in R2, R2b,
                 R2c or R2d excluded, seed 20261113 (fixed and committed before the draw). Simple random sampling, not
                 stratified: the question is what share of the changes are improvements over the whole change set, and a
                 simple random sample estimates that share without weights; proportional stratification by the r6 field
                 would give nearly the same allocation (60/595 of each field) while forcing rounding choices for the many
                 small cells. BOTH coders code ALL 60 items, each in a different random order, so inter-coder agreement
                 can be computed and r5 and r6 can be scored on every item. Run with --r2d-chg; then --r2d-chg-packets OUTDIR.
R2f, R2f-chg     (1.0.7, field dictionary r7) same two designs as R2d and R2d-chg, seed 20261114 (R2f) and 20261115 (R2f-chg),
                 fixed and committed before the draw; every earlier sample (R2, R2b, R2c, R2d, R2d-chg, R2e) is excluded. The
                 coders get new instructions (CODER_RULES_R7: object first, with boundary examples), so R2f agreement is not
                 comparable item by item with the earlier samples coded under the old instructions. Run --r2f, --r2f-chg,
                 then --r2f-packets OUTDIR.
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


R2D_SEED = 20261113
CODER_RULES = """# Coding instructions (field of the invention)

You will read short abstracts of English patent grants, 1617-1852 (Bennet Woodcroft's chronological index, OCR text).
For each entry, choose ONE field from field_list.txt and write its code (the word before the dash, e.g. `textiles`)
in the `field` column of answers.csv. Write `other` when no field fits.

Rules
1. Code the object of the invention: what is made or done by the invention. Do not code the grantee's trade, name or
   address ('iron founder', 'Smith', 'of Bath'), and do not code the place or purpose where the invention is used
   ('for mines', 'for ships') unless that is what the invention itself is.
2. If the entry covers several fields, take the one that comes first in field_list.txt.
3. If no field fits, write `other`.
4. The text is OCR of a printed index and has misreadings and old spellings; read through them.
5. Use the `note` column only when you are unsure or applied rule 2 (a few words). Leave it empty otherwise.

Work only from items.csv and field_list.txt. Do not look up the entries elsewhere and do not open any other file.
Fill every row; do not add, remove or reorder rows.
"""


def r2d():
    """Fresh sample for the r6 dictionary: R2c (which prompted r6) and the earlier samples are not reused."""
    import fields
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    r5 = pd.read_csv(REL / "field_r5.csv").set_index("number")["field"]
    used = (set(pd.read_csv(REL / "r2_key_dictr3.csv")["number"]) | set(pd.read_csv(REL / "r2b_key.csv")["number"])
            | set(pd.read_csv(REL / "r2c_key.csv")["number"]))
    G = W[W["parsed"] & (W["kind"] == "grant") & ~W["number"].isin(used)]
    g = np.random.default_rng(R2D_SEED)
    parts = [G[G["field"] == f].sample(min(25 if f == "other" else 11, int((G["field"] == f).sum())), random_state=int(g.integers(1e9)))
             for f in fields.FIELD_ORDER]
    r = pd.concat(parts).sample(frac=1, random_state=int(g.integers(1e9))).reset_index(drop=True)
    r["coder"] = [1 if i < len(r) // 2 else 2 for i in range(len(r))]
    r["field_r5"] = r["number"].map(r5)
    r[["number", "text"]].to_csv(REL / "r2d_text_input.csv", index=False)
    r[["number", "year", "field", "field_r5", "coder"]].rename(columns={"field": "field_r6"}).to_csv(REL / "r2d_key.csv", index=False)
    (REL / "field_list_r6.txt").write_text("".join(f"{i}. {k} — {fields.LABEL[k]['en']}\n" for i, k in enumerate(fields.FIELD_ORDER[:-1], 1)), encoding="utf-8")
    print("R2d", len(r), "overlap with R2/R2b/R2c:", len(set(r["number"]) & used), "r6 != r5:", int((r["field"] != r["field_r5"]).sum()))


def r2d_packets(outdir: Path):
    """Blind packets: field list, item text and an empty answer sheet. No machine label, no other coder's file."""
    inp = pd.read_csv(REL / "r2d_text_input.csv")
    key = pd.read_csv(REL / "r2d_key.csv")[["number", "coder"]]
    inp = inp.merge(key, on="number", how="left", validate="1:1")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "instructions.md").write_text(CODER_RULES, encoding="utf-8")
    for c in (1, 2):
        d = outdir / f"coder{c}"
        d.mkdir(parents=True, exist_ok=True)
        part = inp[inp["coder"] == c]
        part[["number", "text"]].to_csv(d / "items.csv", index=False)
        pd.DataFrame({"number": part["number"], "field": "", "note": ""}).to_csv(d / "answers.csv", index=False)
        (d / "field_list.txt").write_bytes((REL / "field_list_r6.txt").read_bytes())
        (d / "instructions.md").write_text(CODER_RULES, encoding="utf-8")
        print(d, len(part))


def r2d_chg():
    """Change-set sample: does r6 improve on r5 where they differ? Simple random, 60 items, both coders code all."""
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    r5 = pd.read_csv(REL / "field_r5.csv").set_index("number")["field"]
    used = set()
    for f in ("r2_key_dictr3.csv", "r2b_key.csv", "r2c_key.csv", "r2d_key.csv"):
        used |= set(pd.read_csv(REL / f)["number"])
    W["field_r5"] = W["number"].map(r5)
    C = W[W["parsed"] & (W["kind"] == "grant") & (W["field"] != W["field_r5"]) & ~W["number"].isin(used)]
    g = np.random.default_rng(R2D_SEED)
    r = C.sample(60, random_state=int(g.integers(1e9))).sort_values("number")
    o1 = int(g.integers(1e9)); o2 = int(g.integers(1e9))
    r[["number", "text"]].to_csv(REL / "r2d_chg_text_input.csv", index=False)
    key = r[["number", "year", "field", "field_r5"]].rename(columns={"field": "field_r6"})
    key["order_coder1"] = key["number"].map({n: i for i, n in enumerate(r["number"].sample(frac=1, random_state=o1), 1)})
    key["order_coder2"] = key["number"].map({n: i for i, n in enumerate(r["number"].sample(frac=1, random_state=o2), 1)})
    key.to_csv(REL / "r2d_chg_key.csv", index=False)
    print("R2d-chg", len(r), "of change set", len(C), "overlap with R2/R2b/R2c/R2d:", len(set(r["number"]) & used))


def r2d_chg_packets(outdir: Path):
    """Both coders get all 60 items, each in the order fixed in the key. Same file set and instructions as R2d."""
    inp = pd.read_csv(REL / "r2d_chg_text_input.csv").merge(pd.read_csv(REL / "r2d_chg_key.csv")[["number", "order_coder1", "order_coder2"]],
                                                             on="number", how="left", validate="1:1")
    for c in (1, 2):
        d = outdir / f"chg-coder{c}"
        d.mkdir(parents=True, exist_ok=True)
        part = inp.sort_values(f"order_coder{c}")
        part[["number", "text"]].to_csv(d / "items.csv", index=False)
        pd.DataFrame({"number": part["number"], "field": "", "note": ""}).to_csv(d / "answers.csv", index=False)
        (d / "field_list.txt").write_bytes((REL / "field_list_r6.txt").read_bytes())
        (d / "instructions.md").write_text(CODER_RULES, encoding="utf-8")
        print(d, len(part))


R2F_SEED = 20261114
PRIOR_KEYS = ("r2_key_dictr3.csv", "r2b_key.csv", "r2c_key.csv", "r2d_key.csv", "r2d_chg_key.csv", "r2e_key.csv")
CODER_RULES_R7 = """# Coding instructions (field of the invention) - codebook of 2026-11-14

You will read short abstracts of English patent grants, 1617-1852 (Bennet Woodcroft's chronological index, OCR text).
For each entry, choose ONE field from field_list.txt and write its code (the word before the dash, e.g. `textiles`)
in the `field` column of answers.csv. Write `other` when no field fits.

Principle: the object comes first. The field is the thing that is made or improved by the invention. The rule 'first
field in the list' is used only when the object itself belongs to two fields. If what is improved is the engine, the
field is steam_power; if it is the ship, the carriage or the way of propelling it, the field is transport.

Rules
1. Code the object of the invention: what is made or done by the invention. Do not code
   - the grantee's trade, name or address ('iron founder', 'Smith', 'of Bath');
   - the driving power ('worked by steam', 'by hand, water or wind'): ask what is being driven;
   - the material it is made of or from ('wire strings of a harpsichord' is a musical instrument);
   - the place or purpose where it is used or to which it is 'also applicable' ('for mines', 'for ships',
     'applicable to printing and other purposes'), unless that is what the invention itself is.
2. Only if the object itself covers several fields ('improvements in looms and in lamps'), take the one that comes
   first in field_list.txt. Do not use this rule to choose between an object and its power, material or use.
3. If no field fits, write `other`.
4. The text is OCR of a printed index and has misreadings and old spellings; read through them.
5. Use the `note` column only when you are unsure or applied rule 2 (a few words). Leave it empty otherwise.

Examples of the boundary
- 'propelling vessels by steam', 'paddle wheels for steam boats' -> transport (the vessel and its propulsion).
- 'improvements in steam engines for vessels', 'boilers for marine engines', 'locomotive engines' -> steam_power
  (the engine is what is improved). 'locomotive carriages', 'railway wheels' -> transport.
- 'machinery for figuring fabrics, parts of which are applicable to musical instruments' -> textiles.
- 'dials for clocks', 'a pendulum spring for time keepers' -> instruments (a part of the object is the object).
- 'a nautical instrument for measuring the way of a ship' -> instruments (the instrument, not navigation).
- 'hinges for doors' -> metals (the hinge, not the building).
- 'making iron from iron stone or iron ore with pit coal' -> metals (the ore and the coal are materials).
- 'an engine for raising water out of mines' -> water (what the engine does, not where).

Work only from items.csv and field_list.txt. Do not look up the entries elsewhere and do not open any other file.
Fill every row; do not add, remove or reorder rows.
"""


def _used():
    used = set()
    for f in PRIOR_KEYS:
        used |= set(pd.read_csv(REL / f)["number"])
    return used


def _at_draw(W):
    """The r7 field as it stood when R2f and R2f-chg were drawn (1.0.7 build). 1.0.8 changed one grant (no. 1287), which
    would shift the strata; the samples are kept as drawn, and this file lets the draw be repeated exactly."""
    f = pd.read_csv(REL / "field_r7_at_draw.csv").set_index("number")["field"]
    W = W.copy()
    W["field"] = W["number"].map(f)
    return W


def _r6():
    return pd.read_csv(REL / "field_r6_reparsed.csv").set_index("number")["field"]      # 1.0.8: shipped with the samples


def r2f():
    """Fresh sample for the r7 dictionary (1.0.7): same design as R2c/R2d, every earlier sample excluded (R2e included).
    r6 here is the r6 dictionary applied to the re-parsed text (coding/reliability/field_r6_reparsed.csv), so r6 vs r7 isolates the dictionary."""
    import fields
    W = _at_draw(pd.read_csv(find(DER, "woodcroft_entries.csv")))
    used = _used()
    G = W[W["parsed"] & (W["kind"] == "grant") & ~W["number"].isin(used)]
    g = np.random.default_rng(R2F_SEED)
    parts = [G[G["field"] == f].sample(min(25 if f == "other" else 11, int((G["field"] == f).sum())), random_state=int(g.integers(1e9)))
             for f in fields.FIELD_ORDER]
    r = pd.concat(parts).sample(frac=1, random_state=int(g.integers(1e9))).reset_index(drop=True)
    r["coder"] = [1 if i < len(r) // 2 else 2 for i in range(len(r))]
    r["field_r6"] = r["number"].map(_r6())
    r[["number", "text"]].to_csv(REL / "r2f_text_input.csv", index=False)
    r[["number", "year", "field", "field_r6", "coder"]].rename(columns={"field": "field_r7"}).to_csv(REL / "r2f_key.csv", index=False)
    print("R2f", len(r), "overlap with earlier samples:", len(set(r["number"]) & used), "r7 != r6:", int((r["field"] != r["field_r6"]).sum()))


def r2f_chg():
    """Change-set sample for r6 -> r7: simple random, 60 items (or all, if fewer are left), both coders code all."""
    W = _at_draw(pd.read_csv(find(DER, "woodcroft_entries.csv")))
    used = _used() | set(pd.read_csv(REL / "r2f_key.csv")["number"])
    W["field_r6"] = W["number"].map(_r6())
    C = W[W["parsed"] & (W["kind"] == "grant") & (W["field"] != W["field_r6"]) & ~W["number"].isin(used)]
    g = np.random.default_rng(R2F_SEED + 1)
    r = C.sample(min(60, len(C)), random_state=int(g.integers(1e9))).sort_values("number")
    o1 = int(g.integers(1e9)); o2 = int(g.integers(1e9))
    r[["number", "text"]].to_csv(REL / "r2f_chg_text_input.csv", index=False)
    key = r[["number", "year", "field", "field_r6"]].rename(columns={"field": "field_r7"})
    key["order_coder1"] = key["number"].map({n: i for i, n in enumerate(r["number"].sample(frac=1, random_state=o1), 1)})
    key["order_coder2"] = key["number"].map({n: i for i, n in enumerate(r["number"].sample(frac=1, random_state=o2), 1)})
    key.to_csv(REL / "r2f_chg_key.csv", index=False)
    print("R2f-chg", len(r), "of change set", len(C), "overlap:", len(set(r["number"]) & used))


def r2f_packets(outdir: Path):
    """Blind packets for R2f (two halves) and R2f-chg (both coders, all items): text, field list, new instructions only."""
    inp = pd.read_csv(REL / "r2f_text_input.csv").merge(pd.read_csv(REL / "r2f_key.csv")[["number", "coder"]], on="number", validate="1:1")
    chg = pd.read_csv(REL / "r2f_chg_text_input.csv").merge(pd.read_csv(REL / "r2f_chg_key.csv")[["number", "order_coder1", "order_coder2"]],
                                                             on="number", validate="1:1")
    for c in (1, 2):
        for name, part in ((f"coder{c}", inp[inp["coder"] == c]), (f"chg-coder{c}", chg.sort_values(f"order_coder{c}"))):
            d = outdir / name
            d.mkdir(parents=True, exist_ok=True)
            part[["number", "text"]].to_csv(d / "items.csv", index=False)
            pd.DataFrame({"number": part["number"], "field": "", "note": ""}).to_csv(d / "answers.csv", index=False)
            (d / "field_list.txt").write_bytes((REL / "field_list_r6.txt").read_bytes())
            (d / "instructions.md").write_text(CODER_RULES_R7, encoding="utf-8")
            print(d, len(part))


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
    if "--r2f" in sys.argv:
        r2f()
    elif "--r2f-chg" in sys.argv:
        r2f_chg()
    elif "--r2f-packets" in sys.argv:
        r2f_packets(Path(sys.argv[sys.argv.index("--r2f-packets") + 1]))
    elif "--r2c" in sys.argv:
        r2c()
    elif "--r2d" in sys.argv:
        r2d()
    elif "--r2d-chg" in sys.argv:
        r2d_chg()
    elif "--r2d-chg-packets" in sys.argv:
        r2d_chg_packets(Path(sys.argv[sys.argv.index("--r2d-chg-packets") + 1]))
    elif "--r2d-packets" in sys.argv:
        r2d_packets(Path(sys.argv[sys.argv.index("--r2d-packets") + 1]))
    else:
        main()
