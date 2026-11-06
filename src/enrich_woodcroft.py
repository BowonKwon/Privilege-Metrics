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
- term_years: the first term stated in the text ('for 14 yeares', 'xiiij yeares', 'xxjtie yeares', 'fourteene years',
  'for xiiij next ensuing'); term_other: further terms in the same entry (mines, Ireland, a later revenue) and 'residue'
  when the grant runs for the residue of an earlier term. 1.0.3 adds 'and 31 yeares wthin Ireland', OCR-damaged
  numbers ('80fy', '80^') and the residue re-grant; the first term is computed before these and never changes.
- a margin year that differs from both neighbours while they agree with each other is rejected as an OCR misreading.
- margin segments containing a digit are dates (whole or OCR-damaged), never grantees' names; a year read from a damaged
  date is kept when within 2 of the neighbours' median. data/coding/woodcroft_date_overrides.csv holds years read on the
  page image where the OCR lost the margin date (date_source = page_image).
- foreign_address ignores British street names built on foreign places ('Hanover Square') and society memberships.
- rent / proviso / void clauses: words in the text (17th–18th century grants carry them in the summary).
- title: quoted part of the entry if any; else, in the text from the first 'for/of his|their|her' on (the grantee's name,
  address and trade dropped, 1.0.3), the words after 'invented'/'invention (of)', else after 'sole use/making/…',
  else after 'for', each up to 'to hold' / 'for the term of' / 'within England' / 'By writ'.
- field: fields.classify(title).
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fields import classify  # noqa: E402
from paths import COD, DER  # noqa: E402

WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
           "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
           "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty-one": 21, "twentyone": 21, "twenty one": 21,
           "thirty": 30, "thirty-one": 31, "forty": 40, "fifty": 50, "sixty": 60}


def roman(s: str):
    # in a term of years 'l' is never fifty: it is OCR for 'i' ('xilij' = xiiij = 14)
    s = s.lower().replace("j", "i").replace("u", "v").replace("l", "i")
    vals = {"i": 1, "v": 5, "x": 10}
    if not s or any(c not in vals for c in s):
        return None
    tot = 0
    for i, c in enumerate(s):
        v = vals[c]
        tot += -v if i + 1 < len(s) and vals[s[i + 1]] > v else v
    return tot


OLD_SPELL = [("fower", "four"), ("foure", "four"), ("eleaven", "eleven"), ("seaven", "seven"), ("twelfe", "twelve"),
             ("tenne", "ten"), ("tenn", "ten"), ("sixe", "six"), ("fyve", "five"), ("twentie", "twenty"), ("thirtie", "thirty")]
UNITS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}


def word_number(tok: str):
    t = re.sub(r"\s+", " ", tok.lower().replace("-", " ")).strip()
    for a, b in OLD_SPELL:
        t = t.replace(a, b)
    t = re.sub(r"teene\b", "teen", t)
    if t in WORDNUM:
        return WORDNUM[t]
    m = re.fullmatch(r"(one|two|three|four|five|six|seven|eight|nine) and (twenty|thirty)", t)   # 'one and twenty'
    if m:
        return WORDNUM[m.group(2)] + UNITS[m.group(1)]
    m = re.fullmatch(r"(twenty|thirty) (one|two|three|four|five|six|seven|eight|nine)", t)
    if m:
        return WORDNUM[m.group(1)] + UNITS[m.group(2)]
    return None


NUM_TOK = (r"(\d(?:\s?\d)?(?:\s?(?:teene?|tie|ty))?"                                # 14, 1 4, 14teen
           r"|[xvilj]{1,7}(?:\s?(?:teene?|tie|ty|en|cn|e)\b|[0°o](?=\s))?"            # xiiij, xxjtie, xiiijteen, xiiij e, xiiij0, xilij
           r"|(?:one|two|three|four|five|six|seven|eight|nine)\s+and\s+(?:twent(?:y|ie)|thirt(?:y|ie))"
           r"|(?:twent(?:y|ie)|thirt(?:y|ie))[-\s]?(?:one|two|three|four|five|six|seven|eight|nine)"
           r"|[a-z]+)")
YEARS = r"(?:y[ec]a?r[ec]?[s3]?|yeeres?|yeers?)\b"                                         # years, yeares, yere, ycares (OCR)
TERM_RE = re.compile(r"(?:t[ec]rme?\s*of|for|space\s*of|residue\s*of|remainder\s*of)\s*(?:the\s*)?(?:t[ec]rme?\s*of\s*)?"
                     + NUM_TOK + r"\s*" + YEARS, re.I)
# 1.0.3: further terms the first-term rule cannot see. They are searched only after the first term is fixed, so they
# never change it: OCR-damaged numbers ('80fy', '80^'), 'and 31 yeares wthin Ireland', a re-grant for a residue.
NUM_TOK_OCR = NUM_TOK.replace(r"(?:\s?(?:teene?|tie|ty))?", r"(?:\s?(?:teene?|tie|ty)|fy\b|\^)?", 1)
TERM_OCR_RE = re.compile(r"(?:t[ec]rme?\s*of|for|space\s*of|residue\s*of|remainder\s*of)\s*(?:the\s*)?(?:t[ec]rme?\s*of\s*)?"
                         + NUM_TOK_OCR + r"\s*" + YEARS, re.I)
IRELAND_RE = re.compile(r"\band\s+" + NUM_TOK_OCR + r"\s*" + YEARS + r"\s*(?:w\S{0,4}in|in)\s+ireland", re.I)   # 'xiiij yeares wthin England and 31 yeares wthin Ireland'
RESIDUE_RE = re.compile(r"graunt\w*\s+(?:unto|to)\s+[^;—]{0,80}?\bdur\w*\s+the\s+(?:residue|remainder|remaynder)\s+of\s+the\s+said\s+t[ec]rme?\b", re.I)  # a re-grant for the rest of an earlier term
TERM_NEXT_RE = re.compile(r"\bfor\s+([xvilj]{2,7}|\d{1,2})\s+next\s+ensu", re.I)   # 'for xiiij next ensuing' (word 'years' left out)


def _term_value(tok: str):
    import difflib
    tok = tok.lower().strip()
    d = re.match(r"(\d)\s?(\d)?", tok)
    if d:
        return int(d.group(1) + (d.group(2) or ""))
    v = word_number(tok)
    if v is None:
        r = re.sub(r"\s?(?:teene?|tie|ty|en|cn|e)$|[0°o]$", "", tok)
        v = roman(r) if re.fullmatch(r"[xvilj]+", r) else None
    if v is None and len(tok) >= 6 and tok.isalpha():                      # OCR-damaged words: 'fcurteenc', 'nyneteene'
        t = tok.replace("nyne", "nine")
        t = re.sub(r"teene?$|teenc$", "teen", t)
        best = difflib.get_close_matches(t, list(WORDNUM), n=1, cutoff=0.8)
        v = WORDNUM[best[0]] if best else None
    return v


def terms_of(text: str):
    """All stated terms in order: the first (3–41 years) is the term of the grant; further distinct values (3–99) are other
    rights in the same entry (mines, Ireland, a later revenue) or a covenant."""
    out = []
    for m in TERM_RE.finditer(text):
        v = _term_value(m.group(1))
        if v and 3 <= v <= 99:
            out.append((m.start(), v))
    if not out:
        for m in TERM_NEXT_RE.finditer(text):
            v = _term_value(m.group(1))
            if v and 3 <= v <= 41:
                out.append((m.start(), v))
    vals = [v for _, v in sorted(out)]
    first = next((v for v in vals if v <= 41), None)
    if first is None:
        return []
    rest = []
    for v in vals:
        if v != first and v not in rest:
            rest.append(v)
    for rx in (TERM_OCR_RE, IRELAND_RE):             # 1.0.3
        for m in rx.finditer(text):
            v = _term_value(m.group(1))
            if v and 3 <= v <= 99 and v != first and v not in rest:
                rest.append(v)
    if RESIDUE_RE.search(text):                      # 1.0.3: the grant runs for the residue of an earlier term
        rest.append("residue")
    return [first] + rest


def term_of(text: str):
    t = terms_of(text)
    return t[0] if t else None


FOREIGN_PLACES = r"france|french|paris|lyons|rouen|bordeaux|marseilles|havre|calais|belgium|brussels|antwerp|ghent|liege|holland|netherlands|amsterdam|rotterdam|hague|dutch|flanders|germany|german|prussia|berlin|saxony|bavaria|hanover|hamburg|austria|vienna|bohemia|switzerland|swiss|geneva|italy|italian|venice|milan|genoa|naples|rome|sardinia|piedmont|turin|spain|madrid|portugal|lisbon|sweden|stockholm|denmark|copenhagen|norway|russia|petersburg|poland|united states|america|new york|boston|philadelphia|pennsylvania|massachusetts|baltimore|canada|east indies|west indies|jamaica|bengal|calcutta|madras|bombay|empire of|kingdom of (?!great britain|ireland|england|scotland)|republic of|state of"
FOREIGN_RE = re.compile(r"\b(?:" + FOREIGN_PLACES + r")\b|\balien\b|\bstranger\b|\bforeigner\b|\bborn (?:in|at)\b", re.I)
# London and other British street names built on foreign places ('Hanover Square', 'Holland Street', 'America Square'),
# and memberships of foreign societies, are not addresses abroad
NOT_ABROAD = re.compile(r"\b(?:" + FOREIGN_PLACES + r")\s+(?:square|street|st\.|row|place|terrace|road|lane|court|buildings|wharf|"
                        r"house|park|town|cottage|villa|works|crescent|gate|yard|grove|hill)\b"
                        r"|\b(?:member|fellow|associate)s?\s+of\s+[^,;]{0,80}", re.I)


def foreign_address_of(gp: str) -> bool:
    return bool(FOREIGN_RE.search(NOT_ABROAD.sub(" ", gp)))


# ---- margin segments: a segment with a digit is a date (whole or OCR-damaged), not a grantee's name
MARGIN_NOTE = re.compile(r"record\s+mutilat|illegible", re.I)
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]


def is_date_segment(seg: str) -> bool:
    return bool(re.search(r"\d", seg))


def is_name_segment(seg: str) -> bool:
    return bool(re.search(r"[A-Za-z]{2}", seg)) and not is_date_segment(seg) and not MARGIN_NOTE.search(seg)


def loose_margin_date(seg: str):
    """'loth Dec. 1744.' / 'Hth February 1661,' / '22nd April 18238. |' / 'November 1688.' -> (year, month, day);
    any part may be None. The year is the first four digits after OCR fixes (o/O->0, l/I->1, S->5)."""
    import difflib
    s = seg.replace("|", " ")
    month, mpos = None, None
    for m in re.finditer(r"[A-Za-z]{3,9}", s):
        w = m.group(0).lower()
        if re.fullmatch(r".{0,2}(?:st|nd|rd|th|d)", w):      # the day ('loth' = 10th, 'Hth', '22nd'), not a month
            continue
        best = difflib.get_close_matches(w[:3], [x[:3] for x in MONTHS], n=1, cutoff=0.66)
        if best and not re.fullmatch(r"(?:st|nd|rd|th)", w):
            month, mpos = [x[:3] for x in MONTHS].index(best[0]) + 1, m.end()
            break
    year = None
    tail = s[mpos:] if mpos else s
    digs = re.sub(r"[^0-9]", "", tail.replace("o", "0").replace("O", "0").replace("l", "1").replace("I", "1").replace("S", "5"))
    if len(digs) >= 4 and 1550 <= int(digs[:4]) <= 1860:
        year = int(digs[:4])
    day = None
    head = s[: (mpos or len(s))]
    # only a cleanly read day: digits at the start (after spaces or quote marks), with the ordinal that fits them.
    # 'loth' may be 10th or 15th; ']3th' and '£8th' have lost a digit
    dm = re.match(r"[\s'‘’\".:~(|-]*([0-9]{1,2})(st|nd|rd|th|d)\b", head)
    if dm:
        n, suf = int(dm.group(1)), dm.group(2)
        want = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        if 1 <= n <= 31 and (suf == want or (suf == "d" and want in ("nd", "rd"))):
            day = n
    return year, month, day


STOP = r"(?:;\s*to hold|to hold|for the terme? of|for (?:the )?(?:space|term) of|for \d+ yeares|within (?:England|the kingdom|our)|by writ|with a clause|w\. h\. m\.|$)"
TITLE_PATTERNS = [
    re.compile(r"\b(?:new\s+)?invent(?:ed|ion|ions)(?:\s+or\s+(?:found out|discovered|improved))?(?:\s+of)?\b(.*?)" + STOP, re.I),
    re.compile(r"\bsole\s+(?:use|making|exercise|benefit|benefitt|privilege|license|licence|power)\b(.*?)" + STOP, re.I),
    re.compile(r"\bfor\s+(?!the term|the terme|the space)(.*?)" + STOP, re.I),
]


OBJECT_START = re.compile(r"\b(?:for|of)\s+(?:his|their|her|its)\b(?!\s+(?:majest|maty|matie|royal))", re.I)


def object_text(text: str) -> str:
    """1.0.3 (dictionary r5): the text from the first 'for/of his|their|her' on, which drops the grantee's name, address
    and trade ('Seth Smith, ... builder', 'engraver', 'surgeon'). Quoted titles are taken before this is needed."""
    q = re.search(r"[\"“”]", text)
    m = OBJECT_START.search(text[: q.start() if q else len(text)])
    return text[m.start():] if m else text


def title_of(text: str) -> str:
    q = re.findall(r"[\"“”]\s*(.{6,}?)\s*[\"“”]", text)
    if q:
        return " ".join(q)
    obj = object_text(text)
    for rx in TITLE_PATTERNS:
        m = rx.search(obj)
        if m and len(m.group(1).strip()) >= 6:
            return m.group(1).strip()
    return obj[:300]


def grantee_part(text: str) -> str:
    """Text before the title: names, addresses and descriptions of the grantees."""
    q = re.search(r"[\"“”]", text)
    cut = q.start() if q else len(text)
    m = re.search(r"\b(?:for (?:his|their|her|an?|the|certain|a new)|of (?:his|their|her) (?:new|invention))\b", text[:cut], re.I)
    return text[: m.start() if m else min(cut, 220)]


def main():
    raw = pd.read_csv(DER / "woodcroft_raw.csv", dtype={"text": str, "margin_names": str}).fillna({"text": "", "margin_names": ""})
    full = pd.DataFrame({"number": range(1, 14360)}).merge(raw, on="number", how="left")
    full["parsed"] = full["text"].notna() & (full["text"] != "")
    full["text"] = full["text"].fillna("")
    full["margin_names"] = full["margin_names"].fillna("")
    segs = full["margin_names"].map(lambda s: [x for x in s.split("; ") if x])
    # margin segments the first pass could not read as dates (they were left among the names)
    loose = segs.map(lambda L: next((loose_margin_date(x) for x in L if is_date_segment(x)), (None, None, None)))
    d = pd.to_datetime(full["date_margin"], errors="coerce")
    ly = loose.map(lambda t: t[0])
    lfull = loose.map(lambda t: f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}" if all(t) else None)
    ld = pd.to_datetime(lfull, errors="coerce")
    # chronological sanity: a margin date whose year differs by more than 2 from the median year of the 20 nearest
    # dated entries (10 before, 10 after) is rejected as an OCR misreading
    y0 = d.dt.year
    med = y0.rolling(21, center=True, min_periods=5).median()
    bad = d.notna() & ((y0 - med).abs() > 2)
    # an isolated year between two entries that agree with each other ('1825' between 1823 and 1823) is an OCR misreading
    sy = y0.where(~bad).dropna()
    spike = (sy != sy.shift(1)) & (sy != sy.shift(-1)) & (sy.shift(1) == sy.shift(-1))
    bad = bad | pd.Series(full.index.isin(sy.index[spike]), index=full.index)
    full["date_source"] = "margin"
    full.loc[d.isna(), "date_source"] = "none"
    full.loc[bad, "date_source"] = "margin_rejected"
    d = d.where(~bad)
    full["date"] = d.dt.strftime("%Y-%m-%d").where(d.notna(), "")
    yr = d.dt.year
    # a year read from a damaged margin date (day or month unreadable) is used when it agrees with the neighbours' median
    # a date read from a damaged margin segment is used only when its year lies between the years of the nearest cleanly
    # dated entries before and after (the list is chronological)
    lo_s, hi_s = yr.ffill(), yr.bfill()
    inside = ly.notna() & (lo_s.isna() | (ly >= lo_s)) & (hi_s.isna() | (ly <= hi_s))
    use_full = yr.isna() & ld.notna() & inside
    yonly = yr.isna() & ~use_full & inside
    full.loc[use_full, "date"] = ld[use_full].dt.strftime("%Y-%m-%d")
    yr = yr.where(~(use_full | yonly), ly)
    full.loc[use_full, "date_source"] = "margin_ocr"
    full.loc[yonly, "date_source"] = "margin_year"
    lo, hi = yr.ffill(), yr.bfill()
    fill = yr.isna() & (lo == hi)
    full["year"] = yr.where(~fill, lo)
    full.loc[fill, "date_source"] = full.loc[fill, "date_source"].map(lambda s: "neighbours" if s == "none" else s + "+neighbours")
    # hand-checked years and dates for entries whose margin date the OCR lost (read on the page image)
    ov = pd.read_csv(COD / "woodcroft_date_overrides.csv", dtype={"date": str})
    for _, o in ov.iterrows():
        i = full.index[full["number"] == o["number"]]
        full.loc[i, "year"] = int(o["year"])
        full.loc[i, "date"] = o["date"] if isinstance(o["date"], str) else ""
        full.loc[i, "date_source"] = "page_image"
    t = full["text"]
    low = t.str.lower()
    full["kind"] = "grant"
    full.loc[low.str.contains(r"\bextension\b|\bprolong|\bconfirm(?:ing|ation)\b|\bfurther term\b", regex=True), "kind"] = "extension"
    full["communication"] = low.str.contains("communicat", regex=False)
    gp = t.map(grantee_part)
    full["foreign_address"] = gp.map(foreign_address_of)
    full["foreign_link"] = full["communication"] | full["foreign_address"]
    tl = t.map(terms_of)
    full["term_years"] = tl.map(lambda L: L[0] if L else None)
    full["term_other"] = tl.map(lambda L: "; ".join(str(v) for v in L[1:]) if len(L) > 1 else "")   # further terms stated in the same entry
    full["rent_clause"] = low.str.contains(r"\brent\b|\byearly\b.{0,40}\b(?:pay|rent)|\bpayinge?\b|reserv\w* to (?:the|his|our) (?:crown|matie|majesty)", regex=True)
    full["proviso_clause"] = low.str.contains(r"\bproviso\b|\bprovided\b|\bvoid\b|\bvoyd\b", regex=True)
    full["title"] = t.map(title_of).str.slice(0, 400)
    # before 1700 the title is not set off by quotation marks and addresses are rare: classify the whole text
    early = full["year"] < 1700
    basis = full["title"].where(~early, t)
    full["field"] = basis.map(classify)
    full.loc[~full["parsed"], ["kind", "field"]] = ["", ""]
    full.loc[~full["parsed"], ["communication", "foreign_address", "foreign_link", "rent_clause", "proviso_clause"]] = False
    names = segs.map(lambda L: [x for x in L if is_name_segment(x)])
    full["margin_dates_ocr"] = segs.map(lambda L: "; ".join(x for x in L if is_date_segment(x)))
    full["margin_names"] = names.map("; ".join)
    full["n_grantees"] = names.map(len)
    full["n_grantees"] = full["n_grantees"].where(full["n_grantees"] > 0)
    cols = ["number", "part", "scan_page", "parsed", "flag", "date", "year", "date_source", "kind", "n_grantees", "margin_names",
            "margin_dates_ocr", "communication", "foreign_address", "foreign_link", "term_years", "term_other", "rent_clause",
            "proviso_clause", "field", "title", "text"]
    full[cols].to_csv(DER / "woodcroft_entries.csv", index=False, encoding="utf-8")
    print("rows", len(full), "parsed", int(full.parsed.sum()), "year known", int(full.year.notna().sum()))
    print(full["date_source"].value_counts().to_string())
    print(full["kind"].value_counts().to_string())
    print("term stated:", int(full.term_years.notna().sum()), " comm:", int(full.communication.sum()), " foreign addr:", int(full.foreign_address.sum()))
    print(full["field"].value_counts().to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
