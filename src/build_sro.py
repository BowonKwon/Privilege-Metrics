# -*- coding: utf-8 -*-
"""Stationers' Register Online (SRO) TEI -> one row per register entry.

  python src/build_sro.py

Input  data/raw/sro/current/reg_{A,B,C,D}.xml  (GitHub gbergel/SRO_data, 'Register /CURRENT Register/reg_X-updated.xml',
       commit in data/raw/sro/SRO_data.commit.txt)
Output data/derived/sro_entries.csv

Rules
- one row per <div type="entry"> (xml:id SROnnnn)
- date: SortDate/@when; date_exact = the Register date has @when (not a notBefore/notAfter range)
- status: every <note type="status"> subtype except "incomplete", which is carried by all 10,453 entries
  and reads as a workflow flag rather than a property of the entry
- enterers: persName whose @role contains "enterer" (stationer or non-stationer), keyed by the SRO name key @n
- fee: num[@type="totalEntryPence"]/@value (pence)
"""
import sys
from pathlib import Path

import pandas as pd
from lxml import etree

ROOT = Path(__file__).resolve().parent.parent
NS = {"t": "http://www.tei-c.org/ns/1.0"}


def text_of(el) -> str:
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def parse(path: Path):
    tree = etree.parse(str(path))
    for div in tree.iterfind(".//t:div[@type='entry']", NS):
        sid = div.get("{http://www.w3.org/XML/1998/namespace}id")
        md = div.find("t:ab[@type='metadata']", NS)
        g = lambda xp: md.find(xp, NS) if md is not None else None
        sort = g("t:date[@type='SortDate']")
        reg = g("t:date[@type='Register']")
        statuses = sorted({n.get("subtype") for n in md.iterfind("t:note[@type='status']", NS)} - {"incomplete"}) if md is not None else []
        enterers, roles = [], []
        for p in div.iterfind(".//t:persName", NS):
            role = (p.get("role") or "").strip()
            if "enterer" in role and p.getparent() is not md:
                key = (p.get("n") or "").strip()
                if key and key not in enterers:
                    enterers.append(key)
                    roles.append("non-stationer" if "non-stationer" in role else "stationer")
        body = [e for e in div if e.tag != "{%s}ab" % NS["t"]]
        titles = [text_of(t) for t in div.iterfind(".//t:title", NS)]
        fee = g("t:num[@type='totalEntryPence']")
        works = g("t:num[@type='works']")
        yield {
            "sro_id": sid,
            "sro_number": int(sid[3:]),
            "liber": text_of(g("t:idno[@type='Liber']")),
            "sort_date": sort.get("when") if sort is not None else "",
            "date_exact": bool(reg is not None and reg.get("when")),
            "date_not_before": reg.get("notBefore", "") if reg is not None else "",
            "date_not_after": reg.get("notAfter", "") if reg is not None else "",
            "fee_pence": int(fee.get("value")) if fee is not None and fee.get("value", "").lstrip("-").isdigit() else None,
            "works": int(works.get("value")) if works is not None and works.get("value", "").isdigit() else None,
            "status": ";".join(statuses),
            "enterers": ";".join(enterers),
            "enterer_roles": ";".join(roles),
            "n_enterers": len(enterers),
            "register_ref": text_of(g("t:idno[@type='RegisterRef']")),
            "arber_ref": text_of(g("t:idno[@type='ArberRef']")),
            "title": " | ".join(t for t in titles if t)[:300],
            "text_chars": sum(len(text_of(e)) for e in body),
        }


def main():
    rows = []
    for L in "ABCD":
        rows.extend(parse(ROOT / "data" / "raw" / "sro" / "current" / f"reg_{L}.xml"))
    df = pd.DataFrame(rows).sort_values("sro_number").reset_index(drop=True)
    df["year"] = df["sort_date"].str[:4].astype(int)
    out = ROOT / "data" / "derived" / "sro_entries.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print("entries:", len(df), "ids unique:", df["sro_id"].is_unique, "years:", df["year"].min(), df["year"].max())
    print("exact dates:", int(df["date_exact"].sum()))
    print(df["status"].value_counts().head(12).to_string())
    print("n_enterers:", df["n_enterers"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
