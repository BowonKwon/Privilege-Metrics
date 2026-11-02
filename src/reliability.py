# -*- coding: utf-8 -*-
"""Compare the blind coders' readings with the extracted values and write data/derived/reliability.json.

  python src/reliability.py

R1 image check  data/coding/reliability/r1_image_coder.csv  vs r1_key.csv
R2 text coding  data/coding/reliability/r2_text_coder.csv   vs r2_key.csv
R3 Fulin        data/coding/reliability/r3_fulin_second_coder.csv vs data/coding/fulin_coding.csv
H  Hulme        data/coding/reliability/hulme_image_coder.csv vs data/coding/hulme_1561_1603.csv
Agreement is reported as k/n (share, 95% Wilson interval); field agreement also as Cohen's kappa.
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REL = ROOT / "data" / "coding" / "reliability"
OUT = ROOT / "data" / "derived" / "reliability.json"


def wilson(k, n):
    if n == 0:
        return math.nan, math.nan
    z, p = 1.959964, k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def _blank(x):
    return x is None or (isinstance(x, float) and math.isnan(x)) or (isinstance(x, str) and x.strip() == "")


def same(x, y):
    """Equal values, or both blank (pandas turns None into NaN, and NaN != NaN)."""
    return (_blank(x) and _blank(y)) or x == y


def agree(a, b):
    a, b = list(a), list(b)
    k = sum(1 for x, y in zip(a, b) if same(x, y))
    n = len(a)
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "share": k / n if n else math.nan, "ci": [lo, hi]}


def fmt(r):
    return f"{r['k']}/{r['n']} ({r['share'] * 100:.0f}%, 95% CI {r['ci'][0] * 100:.0f}–{r['ci'][1] * 100:.0f}%)"


def kappa(a, b):
    a, b = list(a), list(b)
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else math.nan


def num(v):
    try:
        f = float(v)
        return None if math.isnan(f) else round(f, 1)
    except (TypeError, ValueError):
        return None


def tf(v):
    return str(v).strip().lower() in ("true", "yes", "1", "y")


def main():
    res, S = {}, {}
    # R3 Fulin
    p = REL / "r3_fulin_second_coder.csv"
    if p.exists():
        b = pd.read_csv(p, dtype=str)
        a = pd.read_csv(ROOT / "data" / "coding" / "fulin_coding.csv", dtype=str).set_index("number")
        b["number"] = b["number"].astype(str)
        a = a.loc[b["number"]]
        r_kind = agree((a["kind"] == "privilege").tolist(), (b["kind"] == "privilege").tolist())
        r_term = agree([num(x) for x in a["term_years"]], [num(x) for x in b["term_years"]])
        r_bt = agree(a["beneficiary_type"].fillna("").tolist(), b["beneficiary_type"].fillna("").tolist())
        r_year = agree(a["date"].str[:4].tolist(), b["date"].str[:4].tolist())
        res["r3"] = {"kind": r_kind, "term": r_term, "btype": r_bt, "year": r_year,
                     "disagree_term": [n for n, x, y in zip(b["number"], a["term_years"], b["term_years"]) if num(x) != num(y)],
                     "disagree_kind": [n for n, x, y in zip(b["number"], a["kind"], b["kind"]) if (x == "privilege") != (y == "privilege")]}
        S["r3_kind"], S["r3_term"], S["r3_btype"] = fmt(r_kind), fmt(r_term), fmt(r_bt)
    # R1 image check
    parts = [REL / "r1_image_coder_a.csv", REL / "r1_image_coder_b.csv"]
    if all(x.exists() for x in parts):
        c = pd.concat([pd.read_csv(x, dtype=str) for x in parts])
        c.to_csv(REL / "r1_image_coder.csv", index=False)
        k = pd.read_csv(REL / "r1_key.csv", dtype=str)
        m = k.merge(c, on="number", suffixes=("_ours", "_img"))
        r_year = agree(m["year"].map(num).tolist(), m["date_img"].str[:4].map(num).tolist())
        r_date = agree(m["date_ours"].fillna("").tolist(), m["date_img"].fillna("").tolist())
        r_term = agree(m["term_years_ours"].map(num).tolist(), m["term_years_img"].map(num).tolist())
        r_ng = agree(m["n_grantees_ours"].map(num).tolist(), m["n_grantees_img"].map(num).tolist())
        r_cm = agree(m["communication_ours"].map(tf).tolist(), m["communication_img"].map(tf).tolist())
        r_kind = agree(m["kind_ours"].fillna("").tolist(), m["kind_img"].fillna("").tolist())
        res["r1"] = {"kind": r_kind, "disagree_year": [n for n, a_, b_ in zip(m["number"], m["year"], m["date_img"]) if num(a_) != num(str(b_)[:4])],
                     "disagree_term": [n for n, a_, b_ in zip(m["number"], m["term_years_ours"], m["term_years_img"]) if not same(num(a_), num(b_))],
                     "disagree_n": [n for n, a_, b_ in zip(m["number"], m["n_grantees_ours"], m["n_grantees_img"]) if not same(num(a_), num(b_))],
                     "disagree_comm": [n for n, a_, b_ in zip(m["number"], m["communication_ours"], m["communication_img"]) if tf(a_) != tf(b_)],
                     "year": r_year, "date": r_date, "term": r_term, "n_grantees": r_ng, "communication": r_cm, "n": len(m)}
        S["r1_year"], S["r1_date"], S["r1_term"], S["r1_ngrantees"], S["r1_comm"] = fmt(r_year), fmt(r_date), fmt(r_term), fmt(r_ng), fmt(r_cm)
    # R2 text coding
    # R2 on the r3 dictionary (kept as the record that led to r4)
    p0 = REL / "r2_text_coder_dictr3.csv"
    if p0.exists():
        c0 = pd.read_csv(p0, dtype=str)
        k0 = pd.read_csv(REL / "r2_key_dictr3.csv", dtype=str)
        m0 = k0.merge(c0, on="number", suffixes=("_ours", "_text"))
        r0 = agree(m0["field_ours"].tolist(), m0["field_text"].tolist())
        res["r2_dictr3"] = {"field": r0, "kappa": kappa(m0["field_ours"].tolist(), m0["field_text"].tolist())}
        S["r2_dictr3_field"] = fmt(r0)
    p = REL / "r2b_text_coder.csv"
    if p.exists():
        c = pd.read_csv(p, dtype=str)
        k = pd.read_csv(REL / "r2b_key.csv", dtype=str)
        m = k.merge(c, on="number", suffixes=("_ours", "_text"))
        r_f = agree(m["field_ours"].tolist(), m["field_text"].tolist())
        kap = kappa(m["field_ours"].tolist(), m["field_text"].tolist())
        per_field = {}
        for f, g in m.groupby("field_ours"):
            per_field[f] = agree(g["field_ours"].tolist(), g["field_text"].tolist())
        r_fa = agree(m["foreign_address_ours"].map(tf).tolist(), m["foreign_address_text"].map(tf).tolist())
        r_cm = agree(m["communication_ours"].map(tf).tolist(), m["communication_text"].map(tf).tolist())
        r_t = agree(m["term_years_ours"].map(num).tolist(), m["term_years_text"].map(num).tolist())
        # population-weighted precision: per-field precision weighted by each field's share of all classified grants
        W = pd.read_csv(ROOT / "data" / "derived" / "woodcroft_entries.csv")
        pop = W[W["parsed"] & (W["kind"] == "grant")]["field"].value_counts(normalize=True)
        wprec = sum(pop.get(f, 0) * r["share"] for f, r in per_field.items())
        S["r2_weighted"] = f"{wprec * 100:.0f}%"
        S["r2_per_field"] = "; ".join(f"{f} {r['k']}/{r['n']}" for f, r in sorted(per_field.items()))
        res["r2"] = {"field": r_f, "kappa": kap, "weighted_precision": wprec, "per_field": per_field, "foreign_address": r_fa, "communication": r_cm, "term": r_t, "n": len(m)}
        S["r2_field"], S["r2_kappa"], S["r2_foreign"], S["r2_comm"], S["r2_term"] = fmt(r_f), f"{kap:.2f}", fmt(r_fa), fmt(r_cm), fmt(r_t)
    # Hulme transcription check
    p = REL / "hulme_image_coder.csv"
    if p.exists():
        c = pd.read_csv(p, dtype=str)
        h = pd.read_csv(ROOT / "data" / "coding" / "hulme_1561_1603.csv", dtype=str)
        m = h.merge(c, on="hulme_no", suffixes=("_ours", "_img"))
        def ymd(v):
            import re as _re
            t = str(v).replace(".", " ").replace(":", "1").split()
            mon = next((i for i, mn in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)
                        if len(t) > 1 and t[1].lower().startswith(mn)), None)
            return (t[0], mon, t[2] if len(t) > 2 else None)
        r_d = agree(m["date_given_ours"].map(ymd).tolist(), m["date_given_img"].map(ymd).tolist())
        r_t = agree(m["term_years_ours"].map(num).tolist(), m["term_years_img"].map(num).tolist())
        res["hulme"] = {"date": r_d, "term": r_t, "n": len(m),
                        "disagree_date": [n for n, a_, b_ in zip(m["hulme_no"], m["date_given_ours"], m["date_given_img"]) if ymd(a_) != ymd(b_)],
                        "disagree_term": [n for n, a_, b_ in zip(m["hulme_no"], m["term_years_ours"], m["term_years_img"]) if num(a_) != num(b_)]}
        S["hulme_date"], S["hulme_term"] = fmt(r_d), fmt(r_t)

    # cards per metric (ko/en lines)
    cards = {}
    def put(ids, ko, en):
        for i in ids:
            cards.setdefault(i, {"ko": {}, "en": {}})
            cards[i]["ko"].update(ko)
            cards[i]["en"].update(en)
    if "r1" in res:
        put(["a1_annual", "a3_1624", "a4_extensions", "c2_cogrant", "d2_term_shift", "d3_clauses", "d1_terms", "c1_foreign"],
            {"이미지 대조 연도 일치": S["r1_year"], "이미지 대조 기간 일치": S["r1_term"], "이미지 대조 수혜자 수 일치": S["r1_ngrantees"], "이미지 대조 communication 일치": S["r1_comm"]},
            {"Image check, year": S["r1_year"], "Image check, term": S["r1_term"], "Image check, number of grantees": S["r1_ngrantees"], "Image check, communication": S["r1_comm"]})
    if "r2" in res:
        put(["b1_fields", "b2_hhi"], {"본문 재코딩 분야 일치(층화 표본)": S["r2_field"], "Cohen κ": S["r2_kappa"], "분야 비중으로 가중한 정밀도": S["r2_weighted"], "분야별 일치": S["r2_per_field"]},
            {"Text recoding, field (stratified sample)": S["r2_field"], "Cohen's kappa": S["r2_kappa"], "Precision weighted by field shares": S["r2_weighted"], "Agreement by field": S["r2_per_field"]})
        put(["c1_foreign"], {"본문 재코딩 해외 주소 일치": S["r2_foreign"], "본문 재코딩 communication 일치": S["r2_comm"]},
            {"Text recoding, address abroad": S["r2_foreign"], "Text recoding, communication": S["r2_comm"]})
        put(["d1_terms", "d2_term_shift"], {"본문 재코딩 기간 일치": S["r2_term"]}, {"Text recoding, term": S["r2_term"]})
    if "r3" in res:
        put(["v1_venice_printing", "d1_terms", "a2_periods"], {"Fulin 재코딩 특권 여부 일치": S["r3_kind"], "Fulin 재코딩 기간 일치": S["r3_term"], "Fulin 재코딩 수혜자 유형 일치": S["r3_btype"]},
            {"Fulin recoding, privilege or not": S["r3_kind"], "Fulin recoding, term": S["r3_term"], "Fulin recoding, beneficiary type": S["r3_btype"]})
    if "hulme" in res:
        put(["a1_annual", "d1_terms", "c1_foreign"], {"Hulme 전사 날짜 일치": S["hulme_date"], "Hulme 전사 기간 일치": S["hulme_term"]},
            {"Hulme transcription, date": S["hulme_date"], "Hulme transcription, term": S["hulme_term"]})
    sro = {"ko": {"원자료": "SRO TEI 10,453항목. 10년 합이 SRO 사이트 검색값과 모든 10년에서 일치"}, "en": {"Source": "SRO TEI, 10,453 entries; decade totals equal the SRO website's search counts in every decade"}}
    for i in ("p1_sro_annual", "p2_sro_concentration", "p3_sro_status", "p4_sro_fees"):
        cards[i] = sro
    sec = {"ko": {"출처": "문헌 수치를 옮긴 값. 재계산하지 않음"}, "en": {"Source": "figures quoted from the literature; not recounted"}}
    cards.setdefault("b3_venice_sectors", sec)
    out = dict(cards)
    out["_summary"] = S
    out["_detail"] = res
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    print(json.dumps(S, indent=1, ensure_ascii=False))
    if "r3" in res:
        print("R3 term disagreements:", res["r3"]["disagree_term"], "kind:", res["r3"]["disagree_kind"])
    if "hulme" in res:
        print("Hulme disagreements:", res["hulme"]["disagree_date"], res["hulme"]["disagree_term"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
