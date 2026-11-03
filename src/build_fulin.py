# -*- coding: utf-8 -*-
"""Fulin, 'Documenti per servire alla storia della tipografia veneziana', Archivio Veneto 23 (1882) -> one row per document.

  python src/build_fulin.py

Input  data/raw/fulin/av23.djvu.txt  (Internet Archive ArchivioVeneto23, OCR, Public Domain Mark)
Output data/derived/fulin_docs.csv   number, date (modern year: Fulin gives the modern year first and the Venetian
                                     style year 'm. v.' in brackets), series (N. C. = Collegio Notatorio, S. T. = Senato Terra,
                                     N. C. X. = Capi del Consiglio dei Dieci), raw text of the document
Documents are numbered 1..256 (1469-1526). A start line is '<n>. <year>, <day> <month>' with n the next expected number
(short forward jumps logged). Whether a document is a privilege, its term and beneficiary are coded by hand
(data/coding/fulin_coding.csv), not here.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

from paths import DER, RAW
MONTHS = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
          "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
START = re.compile(r"^\s*(\d(?:\s?\d){0,2})\s*[.,]\s*([0-9OIlG()\s]{3,7}?)\s*[,.]\s*[0-9ÌI]{1,2}\s*[A-Z]")


def year_of(tok: str):
    t = tok.replace(" ", "").replace("O", "0").replace("G", "6").replace("l", "1").replace("I", "1")
    return int(t) if re.fullmatch(r"1[45]\d\d", t) else None


def month_of(s: str):
    s = s.lower()
    for k, v in MONTHS.items():
        if k[:4] in s or k[1:5] in s:
            return v
    return None


def main():
    text = (RAW / "fulin" / "av23.djvu.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    # the document series begins at no. 1 (1469, 18 Settembre); stop at the first heading after the last document of
    # the first article (pp. 84-212). 'Nuovi documenti' (pp. 390-405) continue the numbering and are included.
    cand = []
    for i, ln in enumerate(lines):
        m = START.match(ln)
        if m:
            y = year_of(m.group(2))
            cand.append((i, int(m.group(1).replace(" ", "")), y if y and 1460 <= y <= 1530 else None))
    # longest chain of candidates whose numbers rise by 1..12 (OCR misreads drop or garble some numbers)
    best, prev = [0] * len(cand), [-1] * len(cand)
    for j, (_, nj, _) in enumerate(cand):
        best[j] = 1 if nj <= 5 else -10**9
        for k in range(max(0, j - 120), j):
            d = nj - cand[k][1]
            if 1 <= d <= 12 and best[k] + 1 > best[j]:
                best[j], prev[j] = best[k] + 1, k
    j = max(range(len(cand)), key=lambda k: (best[k], -k))
    chain = []
    while j != -1:
        chain.append(j); j = prev[j]
    chain = chain[::-1]
    log = []
    docs = []
    for a_, b_ in zip(chain, chain[1:] + [None]):
        i, n, y = cand[a_]
        end = cand[b_][0] if b_ is not None else min(len(lines), i + 400)
        if b_ is not None and cand[b_][1] - n > 1:
            log.append({"after": n, "before": cand[b_][1], "line": i})
        docs.append({"number": n, "year": y, "head": lines[i].strip(), "text": [l.strip() for l in lines[i + 1:end]], "line": i})
    rows = []
    for d in docs:
        head = d["head"]
        dm = re.search(r"(\d{1,2})\s+([A-Za-zÌì]+)", head[head.find(",") + 1:] if "," in head else head)
        mon = month_of(dm.group(2)) if dm else None
        day = int(dm.group(1)) if dm and dm.group(1).isdigit() else None
        ser = re.search(r"\(\s*([NS$][\s.]*[CT£][\s.]*(?:X\.?)?)\s*\)", head + " " + " ".join(d["text"][:2]))
        series = ""
        if ser:
            s = re.sub(r"[\s.]", "", ser.group(1)).replace("$", "S").replace("£", "C")
            series = {"NC": "N. C.", "ST": "S. T.", "NCX": "N. C. X."}.get(s, s)
        body = re.sub(r"-\s+(?=[a-zà-ù])", "", " ".join(t for t in d["text"] if t))
        rows.append({"number": d["number"], "year": d["year"], "month": mon, "day": day, "series": series,
                     "head": head, "text": re.sub(r"\s+", " ", body)[:6000], "src_line": d["line"]})
    df = pd.DataFrame(rows)
    # an unreadable or implausible year (OCR '1197', '1402') is taken from the neighbours when they agree
    yrs = [None if pd.isna(v) else int(v) for v in df["year"]]
    for k, y in enumerate(yrs):
        lo = next((yrs[j] for j in range(k - 1, -1, -1) if yrs[j]), None)
        hi = next((yrs[j] for j in range(k + 1, len(yrs)) if yrs[j]), None)
        if y is None or (lo and hi and not lo <= y <= hi):
            df.loc[k, "year_flag"] = "from_neighbours" if lo == hi else "uncertain"
            df.loc[k, "year"] = lo if lo == hi else (lo or hi)
    df["year"] = df["year"].astype(int)
    df.to_csv(DER / "fulin_docs.csv", index=False, encoding="utf-8")
    missing = sorted(set(range(1, df["number"].max() + 1)) - set(df["number"]))
    (DER / "fulin_parse_log.json").write_text(json.dumps({"jumps": log, "missing": missing}, indent=1), encoding="utf-8")
    print("docs", len(df), "last", df["number"].max(), "missing", missing, "years", df.year.min(), df.year.max())
    print(df["series"].value_counts().to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
