# -*- coding: utf-8 -*-
"""woodcroft_raw.csv -> woodcroft_entries.csv: dates, kind, foreign links, stated term, conditions, title, field.

  python src/enrich_woodcroft.py

Rules (all published on the method page)
- date: the margin date. If missing or out of chronological order (year more than 2 away from the median year of the
  20 nearest dated entries), the year is taken from the neighbours when both neighbours agree; date_source records
  margin / neighbours / none. Missing entry numbers (parse gaps) get a row with text blank and year from neighbours.
- kind: extension when the text grants an 'extension'/'prolongation' of an earlier patent or 'confirmation' of one;
  otherwise grant.
- communication: the text contains 'communication' (invention communicated from abroad, Woodcroft's wording).
- foreign_address: the grantee's description (text before the title) names a place outside the British Isles.
- term_years: a term stated in the text ('for 14 yeares', 'xiiij yeares', 'term of fourteen years').
- rent / proviso / void clauses: words in the text (17th–18th century grants carry them in the summary).
- title: quoted part of the entry if any; else the words after 'invented'/'invention (of)', else after 'sole use/making/…',
  else after 'for', each up to 'to hold' / 'for the term of' / 'within England' / 'By writ'.
- field: fields.classify(title).
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fields import classify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
           "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
           "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty-one": 21, "twentyone": 21, "twenty one": 21,
           "thirty": 30, "thirty-one": 31, "forty": 40, "fifty": 50, "sixty": 60}


def roman(s: str):
    s = s.lower().replace("j", "i").replace("u", "v")
    vals = {"i": 1, "v": 5, "x": 10, "l": 50}
    if not s or any(c not in vals for c in s):
        return None
    tot = 0
    for i, c in enumerate(s):
        v = vals[c]
        tot += -v if i + 1 < len(s) and vals[s[i + 1]] > v else v
    return tot


TERM_RE = re.compile(r"(?:term\s+of|for|terme\s+of|space\s+of)\s+(?:the\s+)?(?:term\s+of\s+)?"
                     r"(\d{1,2}|[xvilj]{1,7}(?:en)?|twenty[-\s]?one|thirty[-\s]?one|[a-z]+)\s+(?:yeares?|years?|yeeres?|yeers?)", re.I)
FOREIGN_PLACES = r"france|french|paris|lyons|rouen|bordeaux|marseilles|havre|calais|belgium|brussels|antwerp|ghent|liege|holland|netherlands|amsterdam|rotterdam|hague|dutch|flanders|germany|german|prussia|berlin|saxony|bavaria|hanover|hamburg|austria|vienna|bohemia|switzerland|swiss|geneva|italy|italian|venice|milan|genoa|naples|rome|sardinia|piedmont|turin|spain|madrid|portugal|lisbon|sweden|stockholm|denmark|copenhagen|norway|russia|petersburg|poland|united states|america|new york|boston|philadelphia|pennsylvania|massachusetts|baltimore|canada|east indies|west indies|jamaica|bengal|calcutta|madras|bombay|empire of|kingdom of (?!great britain|ireland|england|scotland)|republic of|state of"
FOREIGN_RE = re.compile(r"\b(?:" + FOREIGN_PLACES + r")\b|\balien\b|\bstranger\b|\bforeigner\b|\bborn (?:in|at)\b", re.I)


def term_of(text: str):
    for m in TERM_RE.finditer(text):
        tok = m.group(1).lower().strip()
        if tok.isdigit():
            v = int(tok)
        elif tok.replace(" ", "-") in WORDNUM or tok in WORDNUM:
            v = WORDNUM.get(tok.replace(" ", "-"), WORDNUM.get(tok))
        else:
            v = roman(tok[:-2] if tok.endswith("en") else tok)   # 'xjen' = xj (11) with the old ending
        if v and 3 <= v <= 61:
            return v
    return None


STOP = r"(?:;\s*to hold|to hold|for the terme? of|for (?:the )?(?:space|term) of|for \d+ yeares|within (?:England|the kingdom|our)|by writ|with a clause|w\. h\. m\.|$)"
TITLE_PATTERNS = [
    re.compile(r"(?:new\s+)?invent(?:ed|ion|ions)(?:\s+or\s+(?:found out|discovered|improved))?(?:\s+of)?(.*?)" + STOP, re.I),
    re.compile(r"sole\s+(?:use|making|exercise|benefit|benefitt|privilege|license|licence|power)(.*?)" + STOP, re.I),
    re.compile(r"for\s+(?!the term|the terme|the space)(.*?)" + STOP, re.I),
]


def title_of(text: str) -> str:
    q = re.findall(r"[\"“”]\s*(.{6,}?)\s*[\"“”]", text)
    if q:
        return " ".join(q)
    for rx in TITLE_PATTERNS:
        m = rx.search(text)
        if m and len(m.group(1).strip()) >= 6:
            return m.group(1).strip()
    return text[:300]


def grantee_part(text: str) -> str:
    """Text before the title: names, addresses and descriptions of the grantees."""
    q = re.search(r"[\"“”]", text)
    cut = q.start() if q else len(text)
    m = re.search(r"\b(?:for (?:his|their|her|an?|the|certain|a new)|of (?:his|their|her) (?:new|invention))\b", text[:cut], re.I)
    return text[: m.start() if m else min(cut, 220)]


def main():
    raw = pd.read_csv(ROOT / "data" / "derived" / "woodcroft_raw.csv", dtype={"text": str, "margin_names": str}).fillna({"text": "", "margin_names": ""})
    full = pd.DataFrame({"number": range(1, 14360)}).merge(raw, on="number", how="left")
    full["parsed"] = full["text"].notna() & (full["text"] != "")
    full["text"] = full["text"].fillna("")
    d = pd.to_datetime(full["date_margin"], errors="coerce")
    # chronological sanity: a margin date whose year differs by more than 2 from the median year of the 20 nearest
    # dated entries (10 before, 10 after) is rejected as an OCR misreading
    y0 = d.dt.year
    med = y0.rolling(21, center=True, min_periods=5).median()
    bad = d.notna() & ((y0 - med).abs() > 2)
    full["date_source"] = "margin"
    full.loc[d.isna(), "date_source"] = "none"
    full.loc[bad, "date_source"] = "margin_rejected"
    d = d.where(~bad)
    full["date"] = d.dt.strftime("%Y-%m-%d").where(d.notna(), "")
    yr = d.dt.year
    lo, hi = yr.ffill(), yr.bfill()
    fill = yr.isna() & (lo == hi)
    full["year"] = yr.where(~fill, lo)
    full.loc[fill, "date_source"] = full.loc[fill, "date_source"].map(lambda s: "neighbours" if s == "none" else s + "+neighbours")
    t = full["text"]
    low = t.str.lower()
    full["kind"] = "grant"
    full.loc[low.str.contains(r"\bextension\b|\bprolong|\bconfirm(?:ing|ation)\b|\bfurther term\b", regex=True), "kind"] = "extension"
    full["communication"] = low.str.contains("communicat", regex=False)
    gp = t.map(grantee_part)
    full["foreign_address"] = gp.map(lambda s: bool(FOREIGN_RE.search(s)))
    full["foreign_link"] = full["communication"] | full["foreign_address"]
    full["term_years"] = t.map(term_of)
    full["rent_clause"] = low.str.contains(r"\brent\b|\byearly\b.{0,40}\b(?:pay|rent)|\bpayinge?\b|reserv\w* to (?:the|his|our) (?:crown|matie|majesty)", regex=True)
    full["proviso_clause"] = low.str.contains(r"\bproviso\b|\bprovided\b|\bvoid\b|\bvoyd\b", regex=True)
    full["title"] = t.map(title_of).str.slice(0, 400)
    # before 1700 the title is not set off by quotation marks and addresses are rare: classify the whole text
    early = full["year"] < 1700
    basis = full["title"].where(~early, t)
    full["field"] = basis.map(classify)
    full.loc[~full["parsed"], ["kind", "field"]] = ["", ""]
    full.loc[~full["parsed"], ["communication", "foreign_address", "foreign_link", "rent_clause", "proviso_clause"]] = False
    full["n_grantees"] = full["n_margin_names"].where(full["n_margin_names"] > 0)
    cols = ["number", "part", "scan_page", "parsed", "flag", "date", "year", "date_source", "kind", "n_grantees", "margin_names",
            "communication", "foreign_address", "foreign_link", "term_years", "rent_clause", "proviso_clause", "field", "title", "text"]
    full[cols].to_csv(ROOT / "data" / "derived" / "woodcroft_entries.csv", index=False, encoding="utf-8")
    print("rows", len(full), "parsed", int(full.parsed.sum()), "year known", int(full.year.notna().sum()))
    print(full["date_source"].value_counts().to_string())
    print(full["kind"].value_counts().to_string())
    print("term stated:", int(full.term_years.notna().sum()), " comm:", int(full.communication.sum()), " foreign addr:", int(full.foreign_address.sum()))
    print(full["field"].value_counts().to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
