# -*- coding: utf-8 -*-
"""Compare the blind coders' readings with the extracted values and write data/derived/reliability.json.

  python src/reliability.py

R1 image check  data/coding/reliability/r1_image_coder.csv  vs r1_key.csv  (merged from the two coders' _a/_b files when they exist)
R2 text coding  data/coding/reliability/r2b_text_coder.csv  vs r2b_key.csv (and the r3-dictionary round r2_*_dictr3.csv):
                address abroad, communication, term; field as recorded for dictionary r4 (the key's sampling-time field)
R2c (1.0.3)     data/coding/reliability/r2c_text_coder.csv  vs r2c_key.csv: field under dictionary r5, on a fresh sample
                (pinned to r5 in 1.0.6: R2c was used to write r6)
R2d (1.0.6)     r2d_coder1.csv + r2d_coder2.csv (106 items each) vs r2d_key.csv: field under dictionary r6 on a fresh sample,
                and r5 on the same items (field_r5 in the key)
R2d-chg (1.0.6) r2d_chg_coder1.csv and r2d_chg_coder2.csv (both coders, all 60 items) vs r2d_chg_key.csv: entries whose
                field changed from r5 to r6. Inter-coder agreement; per item, improvement (r6 matches the coders, r5 does
                not), regression (the reverse) or neither, counted where the two coders agree
R3 Fulin        data/coding/reliability/r3_fulin_second_coder.csv vs data/coding/fulin_coding.csv
H  Hulme        data/coding/reliability/hulme_image_coder.csv vs data/coding/hulme_1561_1603.csv
Agreement is reported as k/n (share, 95% Wilson interval); field agreement also as Cohen's kappa.
In the public repository the same files are in coding/reliability/ and the output goes to data/reliability.json (paths.py).
Every input is required: a missing file stops the run instead of dropping cards.
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

from paths import COD, DER, REL, find, need

OUT = DER / "reliability.json"



def refresh(key: pd.DataFrame, cols: list) -> pd.DataFrame:
    """The sampled entry numbers stay fixed; the values compared are the current extraction (the key files keep the values
    at sampling time, and re-measuring after a correction must compare the corrected values)."""
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"), dtype=str).set_index("number")
    key = key.copy()
    for c in cols:
        if c in key.columns:
            key[c] = key["number"].map(W[c])
    return key

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
    p = need(REL / "r3_fulin_second_coder.csv")
    if True:
        b = pd.read_csv(p, dtype=str)
        a = pd.read_csv(need(COD / "fulin_coding.csv"), dtype=str).set_index("number")
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
    if all(x.exists() for x in parts):        # build layout: the two coders' files, merged here
        c = pd.concat([pd.read_csv(x, dtype=str) for x in parts])
        c.to_csv(REL / "r1_image_coder.csv", index=False)
    else:                                     # public layout: the merged file only
        c = pd.read_csv(need(REL / "r1_image_coder.csv"), dtype=str)
    if True:
        k = refresh(pd.read_csv(need(REL / "r1_key.csv"), dtype=str), ["date", "year", "margin_names", "n_grantees", "communication", "term_years", "kind"])
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
    p0 = need(REL / "r2_text_coder_dictr3.csv")
    if True:
        c0 = pd.read_csv(p0, dtype=str)
        k0 = pd.read_csv(need(REL / "r2_key_dictr3.csv"), dtype=str)
        m0 = k0.merge(c0, on="number", suffixes=("_ours", "_text"))
        r0 = agree(m0["field_ours"].tolist(), m0["field_text"].tolist())
        res["r2_dictr3"] = {"field": r0, "kappa": kappa(m0["field_ours"].tolist(), m0["field_text"].tolist())}
        S["r2_dictr3_field"] = fmt(r0)
    p = need(REL / "r2b_text_coder.csv")
    if True:
        c = pd.read_csv(p, dtype=str)
        k = refresh(pd.read_csv(need(REL / "r2b_key.csv"), dtype=str), ["field", "foreign_address", "communication", "term_years"])
        m = k.merge(c, on="number", suffixes=("_ours", "_text"))
        # field: the r4 record, compared with the field stored in the key at sampling time (r5 was revised on this sample,
        # so R2b is not used to measure r5)
        k4 = pd.read_csv(need(REL / "r2b_key.csv"), dtype=str)[["number", "field"]].rename(columns={"field": "field_r4"})
        m = m.merge(k4, on="number")
        r_f = agree(m["field_r4"].tolist(), m["field_text"].tolist())
        kap = kappa(m["field_r4"].tolist(), m["field_text"].tolist())
        per_field = {}
        for f, g in m.groupby("field_r4"):
            per_field[f] = agree(g["field_r4"].tolist(), g["field_text"].tolist())
        r_fa = agree(m["foreign_address_ours"].map(tf).tolist(), m["foreign_address_text"].map(tf).tolist())
        r_cm = agree(m["communication_ours"].map(tf).tolist(), m["communication_text"].map(tf).tolist())
        r_t = agree(m["term_years_ours"].map(num).tolist(), m["term_years_text"].map(num).tolist())
        # population-weighted precision: per-field precision weighted by each field's share of all classified grants
        W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
        pop = W[W["parsed"] & (W["kind"] == "grant")]["field"].value_counts(normalize=True)
        # the r4 weighted precision (67%, published in 1.0-1.0.2) used r4 field shares, which are not rebuilt here
        res["r2"] = {"field_r4": r_f, "kappa_r4": kap, "per_field_r4": per_field, "foreign_address": r_fa, "communication": r_cm, "term": r_t, "n": len(m)}
        S["r2b_field_r4"], S["r2b_kappa_r4"] = fmt(r_f), f"{kap:.2f}"
        S["r2_foreign"], S["r2_comm"], S["r2_term"] = fmt(r_fa), fmt(r_cm), fmt(r_t)
    # R2c: field under dictionary r5 on a fresh sample (1.0.3). Pinned to r5 (1.0.6): R2c was used to write r6, so it
    # keeps the r5 labels stored in its key (the sampling-time field, equal to r5 for all 212 items) and the r5 field
    # shares of the 14,287 grants (field_shares_r5.csv) instead of the current field column.
    pop = pd.read_csv(need(REL / "field_shares_r5.csv")).set_index("field")["share"]
    c = pd.read_csv(need(REL / "r2c_text_coder.csv"), dtype=str)
    k = pd.read_csv(need(REL / "r2c_key.csv"), dtype=str)
    m = k.merge(c, on="number", suffixes=("_ours", "_text"))
    r_f = agree(m["field_ours"].tolist(), m["field_text"].tolist())
    kap = kappa(m["field_ours"].tolist(), m["field_text"].tolist())
    per_field = {f: agree(g["field_ours"].tolist(), g["field_text"].tolist()) for f, g in m.groupby("field_ours")}
    wprec = sum(pop.get(f, 0) * r["share"] for f, r in per_field.items())
    res["r2c"] = {"field": r_f, "kappa": kap, "weighted_precision": wprec, "per_field": per_field, "n": len(m),
                  "disagree": [n for n, a_, b_ in zip(m["number"], m["field_ours"], m["field_text"]) if a_ != b_]}
    S["r2_field"], S["r2_kappa"], S["r2_weighted"] = fmt(r_f), f"{kap:.2f}", f"{wprec * 100:.0f}%"
    S["r2_per_field"] = "; ".join(f"{f} {r['k']}/{r['n']}" for f, r in sorted(per_field.items()))
    # R2d: dictionary r6 on a fresh sample (1.0.6), and r5 on the same items
    # Pinned to r6 (1.0.7): the key keeps the r6 labels of 1.0.6 and field_shares_r6.csv the r6 shares of the 14,287
    # grants of 1.0.6, so the card does not move when the dictionary or the parse changes.
    pop6 = pd.read_csv(need(REL / "field_shares_r6.csv")).set_index("field")["share"]
    c = pd.concat([pd.read_csv(need(REL / f"r2d_coder{i}.csv"), dtype=str) for i in (1, 2)])
    k = pd.read_csv(need(REL / "r2d_key.csv"), dtype=str)
    m = k.merge(c, on="number", validate="1:1")
    for lab, col, pp in (("r6", "field_r6", pop6), ("r5", "field_r5", pop)):
        r_f = agree(m[col].tolist(), m["field"].tolist())
        kap = kappa(m[col].tolist(), m["field"].tolist())
        pf = {f: agree(g[col].tolist(), g["field"].tolist()) for f, g in m.groupby(col)}
        wp = sum(pp.get(f, 0) * r["share"] for f, r in pf.items())
        res[f"r2d_{lab}"] = {"field": r_f, "kappa": kap, "weighted_precision": wp, "per_field": pf, "n": len(m),
                             "disagree": [n for n, a_, b_ in zip(m["number"], m[col], m["field"]) if a_ != b_]}
        pre = "r2d" if lab == "r6" else "r2d_r5"
        S[f"{pre}_field"], S[f"{pre}_kappa"], S[f"{pre}_weighted"] = fmt(r_f), f"{kap:.2f}", f"{wp * 100:.0f}%"
        S[f"{pre}_per_field"] = "; ".join(f"{f} {r['k']}/{r['n']}" for f, r in sorted(pf.items()))
    pf6 = res["r2d_r6"]["per_field"]
    named = [r["share"] for f, r in pf6.items() if f != "other"]
    S["r2d_named_range"] = f"{min(named) * 100:.0f}%–{max(named) * 100:.0f}%"
    S["r2d_other"] = f"{pf6['other']['k']}/{pf6['other']['n']}"
    S["r2d_n_differ"] = str(int((m["field_r6"] != m["field_r5"]).sum()))
    # R2d-chg: entries whose field changed r5 -> r6, both coders on all items
    kc = pd.read_csv(need(REL / "r2d_chg_key.csv"), dtype=str)
    a1 = pd.read_csv(need(REL / "r2d_chg_coder1.csv"), dtype=str)[["number", "field"]].rename(columns={"field": "c1"})
    a2 = pd.read_csv(need(REL / "r2d_chg_coder2.csv"), dtype=str)[["number", "field"]].rename(columns={"field": "c2"})
    x = kc.merge(a1, on="number", validate="1:1").merge(a2, on="number", validate="1:1")
    ic = agree(x["c1"].tolist(), x["c2"].tolist())
    ick = kappa(x["c1"].tolist(), x["c2"].tolist())
    ag = x[x["c1"] == x["c2"]]
    out_ = ["improvement" if (a_ == c_ and b_ != c_) else "regression" if (b_ == c_ and a_ != c_) else "neither"
            for a_, b_, c_ in zip(ag["field_r6"], ag["field_r5"], ag["c1"])]
    na = len(ag)
    cnt = {o: agree([1] * out_.count(o) + [0] * (na - out_.count(o)), [1] * na) for o in ("improvement", "regression", "neither")}
    per_coder = {cc: {"r6": int((x["field_r6"] == x[cc]).sum()), "r5": int((x["field_r5"] == x[cc]).sum())} for cc in ("c1", "c2")}
    res["r2d_chg"] = {"n": len(x), "intercoder": ic, "kappa": ick, "n_agree": na, "outcome_where_agree": cnt, "per_coder": per_coder,
                      "regressions": [n for n, o in zip(ag["number"], out_) if o == "regression"],
                      "neither": [n for n, o in zip(ag["number"], out_) if o == "neither"],
                      "coders_disagree": list(x.loc[x["c1"] != x["c2"], "number"])}
    S["chg_n"], S["chg_intercoder"], S["chg_kappa"], S["chg_n_agree"] = str(len(x)), fmt(ic), f"{ick:.2f}", str(na)
    S["chg_improve"], S["chg_regress"], S["chg_neither"] = fmt(cnt["improvement"]), fmt(cnt["regression"]), fmt(cnt["neither"])
    S["chg_improve_k"], S["chg_regress_k"], S["chg_neither_k"] = (str(cnt[o]["k"]) for o in ("improvement", "regression", "neither"))
    # R2f: dictionary r7 on a fresh sample (1.0.7), and r6 (on the re-parsed text) on the same items
    W7 = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    pop7 = W7[W7["parsed"] & (W7["kind"] == "grant")]["field"].value_counts(normalize=True)
    pop6r = pd.read_csv(need(REL / "field_shares_r6_reparsed.csv")).set_index("field")["share"]
    c = pd.concat([pd.read_csv(need(REL / f"r2f_coder{i}.csv"), dtype=str) for i in (1, 2)])
    k = pd.read_csv(need(REL / "r2f_key.csv"), dtype=str)
    m = k.merge(c, on="number", validate="1:1")
    for lab, col, pp in (("r7", "field_r7", pop7), ("r6", "field_r6", pop6r)):
        r_f = agree(m[col].tolist(), m["field"].tolist())
        kap = kappa(m[col].tolist(), m["field"].tolist())
        pf = {f: agree(g[col].tolist(), g["field"].tolist()) for f, g in m.groupby(col)}
        wp = sum(pp.get(f, 0) * r["share"] for f, r in pf.items())
        res[f"r2f_{lab}"] = {"field": r_f, "kappa": kap, "weighted_precision": wp, "per_field": pf, "n": len(m),
                             "disagree": [n for n, a_, b_ in zip(m["number"], m[col], m["field"]) if a_ != b_]}
        pre = "r2f" if lab == "r7" else "r2f_r6"
        S[f"{pre}_field"], S[f"{pre}_kappa"], S[f"{pre}_weighted"] = fmt(r_f), f"{kap:.2f}", f"{wp * 100:.0f}%"
        S[f"{pre}_per_field"] = "; ".join(f"{f} {r['k']}/{r['n']}" for f, r in sorted(pf.items()))
    pf7 = res["r2f_r7"]["per_field"]
    named = [r["share"] for f, r in pf7.items() if f != "other"]
    S["r2f_named_range"] = f"{min(named) * 100:.0f}%–{max(named) * 100:.0f}%"
    S["r2f_other"] = f"{pf7['other']['k']}/{pf7['other']['n']}"
    S["r2f_n_differ"] = str(int((m["field_r7"] != m["field_r6"]).sum()))
    S["r2f_low_fields"] = "; ".join(f"{f} {r['k']}/{r['n']}" for f, r in sorted(pf7.items()) if f != "other" and r["share"] < 0.6)
    # R2f-chg: entries whose field changed r6 -> r7, both coders on all items
    kc = pd.read_csv(need(REL / "r2f_chg_key.csv"), dtype=str)
    a1 = pd.read_csv(need(REL / "r2f_chg_coder1.csv"), dtype=str)[["number", "field"]].rename(columns={"field": "c1"})
    a2 = pd.read_csv(need(REL / "r2f_chg_coder2.csv"), dtype=str)[["number", "field"]].rename(columns={"field": "c2"})
    x = kc.merge(a1, on="number", validate="1:1").merge(a2, on="number", validate="1:1")
    ic = agree(x["c1"].tolist(), x["c2"].tolist())
    ick = kappa(x["c1"].tolist(), x["c2"].tolist())
    ag = x[x["c1"] == x["c2"]]
    out_ = ["improvement" if (a_ == c_ and b_ != c_) else "regression" if (b_ == c_ and a_ != c_) else "neither"
            for a_, b_, c_ in zip(ag["field_r7"], ag["field_r6"], ag["c1"])]
    na = len(ag)
    cnt = {o: agree([1] * out_.count(o) + [0] * (na - out_.count(o)), [1] * na) for o in ("improvement", "regression", "neither")}
    per_coder = {cc: {"r7": int((x["field_r7"] == x[cc]).sum()), "r6": int((x["field_r6"] == x[cc]).sum())} for cc in ("c1", "c2")}
    res["r2f_chg"] = {"n": len(x), "intercoder": ic, "kappa": ick, "n_agree": na, "outcome_where_agree": cnt, "per_coder": per_coder,
                      "regressions": [n for n, o in zip(ag["number"], out_) if o == "regression"],
                      "neither": [n for n, o in zip(ag["number"], out_) if o == "neither"],
                      "coders_disagree": list(x.loc[x["c1"] != x["c2"], "number"])}
    S["fchg_n"], S["fchg_intercoder"], S["fchg_kappa"], S["fchg_n_agree"] = str(len(x)), fmt(ic), f"{ick:.2f}", str(na)
    S["fchg_improve"], S["fchg_regress"], S["fchg_neither"] = fmt(cnt["improvement"]), fmt(cnt["regression"]), fmt(cnt["neither"])
    S["fchg_improve_k"], S["fchg_regress_k"], S["fchg_neither_k"] = (str(cnt[o]["k"]) for o in ("improvement", "regression", "neither"))
    # R2e: all grants the title-fallback rule of r6 moved out of 'other' in 1.0.6 (141), coded blind by an outside verifier
    e = pd.read_csv(need(REL / "r2e_scored.csv"), dtype=str)
    S["r2e_n"] = str(len(e))
    # Hulme transcription check
    p = need(REL / "hulme_image_coder.csv")
    if True:
        c = pd.read_csv(p, dtype=str)
        h = pd.read_csv(need(COD / "hulme_1561_1603.csv"), dtype=str)
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
        put(["b1_fields", "b2_hhi"], {"본문 재코딩 분야 일치(층화 표본 R2f, 사전 r7)": S["r2f_field"], "Cohen κ": S["r2f_kappa"], "분야 비중으로 가중한 정밀도": S["r2f_weighted"], "분야별 일치": S["r2f_per_field"],
                                      "같은 항목의 사전 r6": f"{S['r2f_r6_field']}(κ {S['r2f_r6_kappa']}, 가중 {S['r2f_r6_weighted']})",
                                      "r6→r7로 바뀐 항목 표본(R2f-chg, 두 코더가 같은 답 " + S["fchg_n_agree"] + "건)": f"r7만 맞음 {S['fchg_improve']}; r6만 맞음 {S['fchg_regress']}; 둘 다 틀림 {S['fchg_neither_k']}건",
                                      "R2f-chg 코더 간 일치": f"{S['fchg_intercoder']}(κ {S['fchg_kappa']})",
                                      "앞 판의 측정(사전 r6, 표본 R2d, 옛 코더 지시)": f"{S['r2d_field']}(κ {S['r2d_kappa']}, 가중 {S['r2d_weighted']})"},
            {"Text recoding, field (stratified sample R2f, dictionary r7)": S["r2f_field"], "Cohen's kappa": S["r2f_kappa"], "Precision weighted by field shares": S["r2f_weighted"], "Agreement by field": S["r2f_per_field"],
             "Dictionary r6 on the same entries": f"{S['r2f_r6_field']} (κ {S['r2f_r6_kappa']}, {S['r2f_r6_weighted']} weighted)",
             "Entries changed r6→r7 (R2f-chg, " + S["fchg_n_agree"] + " where both coders agree)": f"only r7 right {S['fchg_improve']}; only r6 right {S['fchg_regress']}; both wrong {S['fchg_neither_k']}",
             "R2f-chg agreement between coders": f"{S['fchg_intercoder']} (κ {S['fchg_kappa']})",
             "Previous measurement (dictionary r6, sample R2d, earlier coder instructions)": f"{S['r2d_field']} (κ {S['r2d_kappa']}, {S['r2d_weighted']} weighted)"})
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
