# -*- coding: utf-8 -*-
"""Woodcroft, Titles of Patents of Invention, Chronologically Arranged (1854) -> one row per numbered entry.

  python src/build_woodcroft.py

Input  data/raw/woodcroft/p{1,2}.djvu.xml   Internet Archive OCR (ABBYY) with word coordinates
       p1 = chronologicalin1617grea_0 (Nos. 1-4,800), p2 = chronologicalind1617grea (Nos. 4,801-14,359)
Output data/derived/woodcroft_raw.csv        one row per entry: number, scan page, margin date, margin surnames, body text
       data/derived/woodcroft_parse_log.json gaps and repairs

Layout (checked on pages from both parts): the scan has a left margin column holding each patentee's
surname and, below the surnames, the date of the grant; the entry text is in a right column and every
entry starts with its number ("29." / "1536." / "10,737." which the OCR often reads "10.737.").
A margin line is assigned to the entry whose first line is the nearest one at or above it on the same page.

Number repair: entry numbers must run 1..14,359. A candidate start line is accepted when its number is the
next expected one (or within a short forward jump, which is logged as a gap); OCR variants of the
thousands separator ("," "." " ") are normalised.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd
from lxml import etree

from paths import DER, RAW as RAW_ROOT

RAW = RAW_ROOT / "woodcroft"

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
DATE_RE = re.compile(r"^\s*(\d{1,2})\s*(?:st|nd|rd|th|d|t)?\s*\.?\s*([A-Za-z]{3,9})\.?\s*,?\s*(1[5-8]\d\d)\b")
START_RE = re.compile(r"^\s*(\d{1,2}[,.\s]\d{3}|\d{1,4})\s*[.,]\s+\S")
NUM_TOKEN = re.compile(r"^\d{1,2}[,.]?\d{3}[.,]$|^\d{1,4}[.,]$")
MONTH_TOKEN = re.compile(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?$", re.I)
GRANT_RE = re.compile(r"\b(A|An)\s+(grant|graunt|spiall|speciall|special|lycence|licence|license|patent)\b|\bgrant\s+unt[o0]\b", re.I)
HEADER_Y = 0.085          # top band (running head, page number) as a share of page height


def lines_of(path: Path):
    """Yield (page_index, width, height, lines) per scanned page; a line is a list of words (x0, x1, ytop, text)."""
    for ev, obj in etree.iterparse(str(path), tag="OBJECT"):
        W, H = int(obj.get("width")), int(obj.get("height"))
        m = re.search(r"_(\d{4})\.djvu", obj.get("usemap", ""))
        idx = int(m.group(1)) if m else -1
        out = []
        tsv = RAW / "reocr" / f"{path.stem.split('.')[0]}_{idx:04d}.tsv"
        if tsv.exists():          # re-OCR (tesseract) replaces the Internet Archive OCR for this page
            yield idx, W, H, tsv_lines(tsv)
            obj.clear()
            continue
        for line in obj.iter("LINE"):
            ws = []
            for w in line.findall("WORD"):
                c = list(map(int, w.get("coords").split(",")))
                t = (w.text or "").strip()
                if t:
                    ws.append((c[0], c[2], c[3], t))
            if ws:
                out.append(sorted(ws))
        yield idx, W, H, sorted(out, key=lambda ws: (min(w[2] for w in ws), ws[0][0]))
        obj.clear()


def tsv_lines(path: Path):
    """tesseract TSV -> lines of words (x0, x1, ytop, text) in reading order."""
    import csv
    groups = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="	", quoting=csv.QUOTE_NONE):
            t = (r.get("text") or "").strip()
            if r["level"] != "5" or not t:
                continue
            k = (int(r["block_num"]), int(r["par_num"]), int(r["line_num"]))
            x0, y0, w = int(r["left"]), int(r["top"]), int(r["width"])
            groups.setdefault(k, []).append((x0, x0 + w, y0, t))
    lines = [sorted(ws) for ws in groups.values()]
    return sorted(lines, key=lambda ws: (min(w[2] for w in ws), ws[0][0]))


def split_columns(lines, W):
    """Word coordinates abut (each word's right edge reaches the next word), so the split is made on word
    starts. Body left edge L = 20th percentile of the first-word x of lines with >= 3 words that start
    right of 12% of the page width (continuation lines dominate this set); a word starting left of L - 15
    is a margin word. Returns (margin_lines, body_lines) as (x0, ytop, text)."""
    starts = sorted(ws[0][0] for ws in lines if len(ws) >= 3 and ws[0][0] > 0.12 * W)
    if starts:   # densest 40-px window of line starts = the continuation-line edge
        left = max(starts, key=lambda x: (sum(1 for y in starts if x <= y <= x + 40), -x))
    else:
        left = int(0.2 * W)
    mar, bod = [], []
    for ws in lines:
        mw = [w for w in ws if w[0] < left - 15]
        bw = [w for w in ws if w[0] >= left - 15]
        # an entry number set out into the margin ("Higgon. 4980. A grant ...") goes back to the body;
        # a year after a month name ("22nd June 1824.") stays in the margin
        for i, w in enumerate(mw):
            if NUM_TOKEN.match(w[3]) and not (i and MONTH_TOKEN.match(mw[i - 1][3])):
                bw, mw = mw[i:] + bw, mw[:i]
                break
        if mw:
            mar.append((mw[0][0], min(w[2] for w in mw), " ".join(w[3] for w in mw)))
        if bw:
            bod.append((bw[0][0], min(w[2] for w in bw), " ".join(w[3] for w in bw)))
    return mar, bod


MONTH_NAMES = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DATE_LOOSE = re.compile(r"^\s*([0-9IlSO]{1,2})\s*(?:st|nd|rd|th|d|t|h)?\s*\.?\s*([A-Za-z]{3,9})\.?\s*,?\s*([0-9IlO][0-9IlO\s]{2,5}[0-9IlO])?\s*\.?")


def _digits(t: str) -> str:
    return t.replace(" ", "").replace("I", "1").replace("l", "1").replace("O", "0").replace("S", "5")


def _month(tok: str):
    import difflib
    t = tok.lower()[:4]
    best = difflib.get_close_matches(t, [m[:len(t)] for m in MONTH_NAMES], n=1, cutoff=0.6)
    return [m[:len(t)] for m in MONTH_NAMES].index(best[0]) + 1 if best else None


def parse_date(s: str, need_year: bool = True):
    """Margin date ('4th March 1624.', OCR variants 'Ist Sept.', '2lst May', '6th Noy.') -> ISO string, or
    (day, month) when need_year is False and the year is missing."""
    s = s.replace("|", " ").replace("  ", " ").strip()
    m = DATE_LOOSE.match(s)
    if not m:
        return None
    try:
        d = int(_digits(m.group(1)))
    except ValueError:
        return None
    mon = _month(m.group(2))
    if not mon or not 1 <= d <= 31:
        return None
    if m.group(3):
        y = _digits(m.group(3))
        if y.isdigit() and len(y) == 4 and 1550 <= int(y) <= 1860:
            return f"{int(y):04d}-{mon:02d}-{d:02d}"
        return None
    return None if need_year else (d, mon)


def num_of(tok: str) -> int:
    return int(re.sub(r"[,.\s]", "", tok))


def main():
    pages = []
    for part in (1, 2):
        for idx, W, H, lines in lines_of(RAW / f"p{part}.djvu.xml"):
            pages.append((part, idx, W, H, lines))

    # pass 1: one global stream of body lines; margin lines kept per page
    stream, margins = [], {}
    for part, idx, W, H, lines in pages:
        key = (part, idx)
        margins[key] = []
        mar, bod = split_columns([ws for ws in lines if min(w[2] for w in ws) >= HEADER_Y * H], W)
        margins[key] = [(yt, txt) for x0, yt, txt in mar]
        for x0, yt, txt in sorted(bod, key=lambda r: (r[1], r[0])):
            m = START_RE.match(txt)
            stream.append({"key": key, "y": yt, "txt": txt, "n": num_of(m.group(1)) if m else None, "cut": m.end(1) if m else 0})
    cand = [i for i, r in enumerate(stream) if r["n"] is not None]

    # pass 2: longest chain of candidates whose numbers rise by 1..MAXSTEP (dynamic programming)
    MAXSTEP, LOOK = 30, 600
    best, prev = [0] * len(cand), [-1] * len(cand)
    for j, cj in enumerate(cand):
        nj = stream[cj]["n"]
        best[j] = 1 if nj <= MAXSTEP else -10**9
        for i in range(max(0, j - LOOK), j):
            d = nj - stream[cand[i]]["n"]
            if 1 <= d <= MAXSTEP and best[i] + 1 > best[j]:
                best[j], prev[j] = best[i] + 1, i
    j = max(range(len(cand)), key=lambda k: (best[k], -k))
    chain = []
    while j != -1:
        chain.append(cand[j]); j = prev[j]
    chain = chain[::-1]

    # pass 3: inside a gap, unaccepted candidates are renumbered in order when their count equals the gap
    log = {"gaps": [], "renumbered": 0, "candidates": len(cand), "chain": len(chain)}
    starts = {c: stream[c]["n"] for c in chain}
    flags = {}
    for a_, b_ in zip(chain, chain[1:]):
        na, nb = stream[a_]["n"], stream[b_]["n"]
        if nb - na > 1:
            inner = [c for c in cand if a_ < c < b_]
            soft = [i for i in range(a_ + 1, b_) if i not in inner and GRANT_RE.search(stream[i]["txt"][:60])]
            if len(inner) == nb - na - 1:
                for k, c in enumerate(inner, 1):
                    starts[c] = na + k; flags[c] = "renumbered"
                log["renumbered"] += len(inner)
            elif len(soft) + len(inner) == nb - na - 1:
                for k, c in enumerate(sorted(inner + soft), 1):
                    starts[c] = na + k; flags[c] = "renumbered" if c in inner else "start_by_wording"
                    if c not in inner:
                        stream[c]["cut"] = 0
                log["renumbered"] += len(inner); log["start_by_wording"] = log.get("start_by_wording", 0) + len(soft)
            else:
                log["gaps"].append({"after": na, "before": nb, "inner_candidates": len(inner), "page": list(stream[a_]["key"])})

    entries, cur = [], None
    by_page = {}
    for i, r in enumerate(stream):
        if i in starts:
            cur = {"number": starts[i], "part": r["key"][0], "page": r["key"][1], "y": r["y"], "flag": flags.get(i, ""),
                   "text": [r["txt"][r["cut"]:].lstrip(" .,")], "margin": []}
            entries.append(cur)
            by_page.setdefault(r["key"], []).append(cur)
        elif cur is not None:
            cur["text"].append(r["txt"])
    # margin lines: nearest entry start at or above on the same page, else the entry carried over from earlier pages
    last_before = {}
    cur = None
    order = sorted(margins)
    ent_iter = iter(entries)
    started = {}
    for e in entries:
        started.setdefault((e["part"], e["page"]), e)
    carried = None
    for key in order:
        here = by_page.get(key, [])
        joined, skip = [], False
        ms = margins[key]
        for k, (yt, txt) in enumerate(ms):
            if skip:
                skip = False
                continue
            if parse_date(txt) is None and parse_date(txt, need_year=False) and k + 1 < len(ms) and re.fullmatch(r"\s*[0-9IlO]{4}\s*\.?\s*\|?\s*", ms[k + 1][1]):
                joined.append((yt, txt.rstrip(" .|") + " " + ms[k + 1][1].strip(" .|") + "."))
                skip = True
            else:
                joined.append((yt, txt))
        for yt, txt in joined:
            owner = None
            for e in here:
                if e["y"] <= yt + 40:
                    owner = e
            if owner is None:
                owner = carried if carried is not None else (here[0] if here else None)
            if owner is not None:
                owner["margin"].append(txt)
        if here:
            carried = here[-1]

    rows = []
    for e in entries:
        dates = [parse_date(m) for m in e["margin"]]
        dates = [d for d in dates if d]
        names = [m for m in e["margin"] if not parse_date(m) and re.search(r"[A-Za-z]{2}", m) and not re.fullmatch(r"[\d\s.,]+", m)]
        text = " ".join(e["text"])
        text = re.sub(r"-\s+(?=[a-z])", "", text)          # rejoin hyphenated line breaks
        text = re.sub(r"\s+", " ", text).strip()
        rows.append({"number": e["number"], "part": e["part"], "scan_page": e["page"],
                     "date_margin": dates[0] if dates else "", "n_margin_dates": len(dates),
                     "margin_names": "; ".join(names), "n_margin_names": len(names), "flag": e["flag"], "text": text})
    df = pd.DataFrame(rows)
    df.to_csv(DER / "woodcroft_raw.csv", index=False, encoding="utf-8")
    log["entries"] = len(df)
    log["last_number"] = int(df["number"].max())
    log["missing_numbers"] = sorted(set(range(1, 14360)) - set(df["number"]))
    (DER / "woodcroft_parse_log.json").write_text(json.dumps(log, indent=1), encoding="utf-8")
    print("entries", len(df), "last", log["last_number"], "missing", len(log["missing_numbers"]), "gaps", len(log["gaps"]),
          "candidates", log["candidates"], "chain", log["chain"], "renumbered", log["renumbered"])
    print("no date:", int((df["date_margin"] == "").sum()), " >1 date:", int((df["n_margin_dates"] > 1).sum()))
    print("missing first 40:", log["missing_numbers"][:40])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
