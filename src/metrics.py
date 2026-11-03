# -*- coding: utf-8 -*-
"""All metric tables. Reads data/derived/*.csv and data/coding/*.csv, writes data/derived/m_*.csv
(public repository: data/ and coding/, see paths.py). The Dutch tables need the Buning and Looijesteijn spreadsheet in
data/raw/buning/patents-dutch-republic-1581-1621.xlsx (figshare doi:10.6084/m9.figshare.16685788.v1, file 31787171).

  python src/metrics.py

Counting units are stated on every table:
  GB Hulme     one grant (reissues folded into the original, Hulme's rule)
  GB Woodcroft one numbered entry; 'grants' excludes entries whose text grants an extension/prolongation/confirmation;
               numbers lost by the OCR parse are counted (their year comes from the neighbours) but carry no text
  SRO          one register entry (a 'copy' entered; one entry may name several works)
  VE Fulin     one document coded 'privilege' (codebook data/coding/fulin_codebook.md)
  NL Buning    one document whose 'Nature of contact' is 3 (privilege issued)
  VE secondary period counts quoted from the literature, never mixed into our own counts
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fields import FIELD_ORDER, classify  # noqa: E402
from paths import BUNING_XLSX, COD, DER, find, need  # noqa: E402

RNG = np.random.default_rng(20261103)


def poisson_ci(k: int, years: int):
    """Exact (Garwood) 95% CI for a Poisson mean per year."""
    from scipy.stats import chi2
    lo = chi2.ppf(0.025, 2 * k) / 2 if k > 0 else 0.0
    hi = chi2.ppf(0.975, 2 * (k + 1)) / 2
    return lo / years, hi / years


def wilson(k: int, n: int):
    if n == 0:
        return (math.nan, math.nan)
    z, p = 1.959964, k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def hhi(shares) -> float:
    s = np.asarray(shares, dtype=float)
    s = s / s.sum() if s.sum() else s
    return float((s ** 2).sum())


def load():
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    W["grant"] = W["kind"].fillna("") != "extension"
    H = pd.read_csv(need(COD / "hulme_1561_1603.csv"))
    H["year"] = H["date_given"].str[:4].astype(int)
    S = pd.read_csv(find(DER, "sro_entries.csv"))
    F = pd.read_csv(need(COD / "fulin_coding.csv"))
    if True:
        F["year"] = pd.to_numeric(F["date"].astype(str).str[:4], errors="coerce")   # some dates are year-month only (e.g. 1508-10)
    if not BUNING_XLSX.exists():
        raise FileNotFoundError(f"{BUNING_XLSX} is missing: download file 31787171 of doi:10.6084/m9.figshare.16685788.v1 and save it under that name")
    B = pd.read_excel(BUNING_XLSX, sheet_name=None)
    return W, H, S, F, B


def buning_tables(B):
    P = B["Patents"].rename(columns=lambda c: c.strip())
    P = P[P["Unique number Document"].notna()].copy()
    P["doc"] = P["Unique number Document"].astype(int)
    P["year"] = pd.to_numeric(P["Year"], errors="coerce")
    P["privilege"] = P["Nature of contact"] == 3
    I = B["Inventors"].rename(columns=lambda c: c.strip())
    I["doc"] = pd.to_numeric(I["Unique number document"], errors="coerce")
    # Buning's 'Foreigner' codes: 1-6 a named foreign origin, 7 probably of foreign extraction, 8 certainly Dutch,
    # 9 probably Dutch, 0 not applicable (Codes sheet, row 33)
    fc = pd.to_numeric(I["Foreigner"], errors="coerce").fillna(0)
    I["foreign"] = fc.between(1, 6)
    I["foreign_probable"] = fc.between(1, 7)
    per_doc = I.groupby("doc").agg(n_patentees=("doc", "size"), any_foreign=("foreign", "max"), any_foreign_probable=("foreign_probable", "max"))
    V = B["Inventions"].rename(columns=lambda c: c.strip())
    V["doc"] = pd.to_numeric(V["Unique number document"], errors="coerce")
    V["gets"] = pd.to_numeric(V["Gets"], errors="coerce")
    gets = V.groupby("doc")["gets"].max()
    P = P.join(per_doc, on="doc").join(gets, on="doc")
    return P


def main():
    W, H, S, F, B = load()
    NL = buning_tables(B)
    out, rel = {}, {}

    # ---------------- A1 annual grants, England
    wy = W[W["year"].notna()].copy()
    wy["year"] = wy["year"].astype(int)
    a1 = pd.DataFrame({"year": range(1561, 1853)})
    a1["hulme"] = a1["year"].map(H.groupby("year").size()).fillna(0).astype(int)
    a1["woodcroft_grants"] = a1["year"].map(wy[wy["grant"]].groupby("year").size()).fillna(0).astype(int)
    a1["woodcroft_extensions"] = a1["year"].map(wy[~wy["grant"]].groupby("year").size()).fillna(0).astype(int)
    a1["woodcroft_no_text"] = a1["year"].map(wy[~wy["parsed"]].groupby("year").size()).fillna(0).astype(int)
    a1["grants"] = a1["hulme"] + a1["woodcroft_grants"]
    a1["list"] = np.where(a1["year"] <= 1603, "Hulme 1896/1900", np.where(a1["year"] >= 1617, "Woodcroft 1854", "no list (1604-1616)"))
    a1.loc[(a1["year"] > 1603) & (a1["year"] < 1617), "grants"] = np.nan
    out["m_a1_annual"] = a1

    # ---------------- A2 periods across jurisdictions
    rows = []
    periods = [(1469, 1500), (1501, 1550), (1551, 1600), (1601, 1650), (1651, 1700), (1701, 1750), (1751, 1800), (1801, 1852)]
    for lo, hi in periods:
        lab = f"{lo}-{hi}"
        g = int(a1[(a1.year >= lo) & (a1.year <= hi)]["grants"].sum(skipna=True)) if hi >= 1561 else None
        cover = "1561-1603, 1617-1852" if hi >= 1561 else ""
        if g is not None and hi >= 1561:
            rows.append({"period": lab, "jurisdiction": "GB", "kind": "invention", "count": g, "unit": "grant",
                         "basis": "own count", "source": "Hulme 1896/1900; Woodcroft 1854", "coverage": cover})
        if F is not None:
            k = int(((F["kind"] == "privilege") & F["year"].between(lo, hi)).sum())
            if lo <= 1526:
                rows.append({"period": lab, "jurisdiction": "VE", "kind": "printing", "count": k, "unit": "privilege document",
                             "basis": "own count", "source": "Fulin 1882 (docs 1-256, to Nov. 1526)", "coverage": "1469-1526"})
        k = int((NL["privilege"] & NL["year"].between(lo, hi)).sum())
        if lo <= 1621 and hi >= 1581:
            rows.append({"period": lab, "jurisdiction": "NL", "kind": "invention", "count": k, "unit": "privilege document",
                         "basis": "own count of Buning & Looijesteijn data", "source": "figshare 10.6084/m9.figshare.16685788", "coverage": "1581-1621"})
    for lab, c, c2 in [("1474-1500", 43, 33), ("1501-1550", 126, 116), ("1551-1600", 471, 461)]:
        rows.append({"period": lab.replace("1474", "1469") if False else lab, "jurisdiction": "VE", "kind": "invention", "count": c, "unit": "Senate grant",
                     "basis": "secondary", "source": "Comino, Galasso & Graziano 2017, p. 7 (from Berveglieri 1995/1999)", "coverage": lab, "alt_count": c2,
                     "alt_source": "Kostylo 2010, n. 5 (Berveglieri 1995, pp. 21-22)"})
    rows.append({"period": "before 1474", "jurisdiction": "VE", "kind": "invention", "count": 5, "unit": "ad hoc privilege", "basis": "secondary",
                 "source": "Comino, Galasso & Graziano 2017, p. 7 (Mandich 1936)", "coverage": "-1473"})
    out["m_a2_periods"] = pd.DataFrame(rows)

    # ---------------- A3 before / after the Statute of Monopolies (1624)
    a3 = []
    for lab, lo, hi in [("1617-1623", 1617, 1623), ("1625-1631", 1625, 1631), ("1632-1638", 1632, 1638)]:
        k = int(a1[(a1.year >= lo) & (a1.year <= hi)]["woodcroft_grants"].sum())
        n = hi - lo + 1
        cl, ch = poisson_ci(k, n)
        a3.append({"window": lab, "years": n, "grants": k, "per_year": k / n, "ci_low": cl, "ci_high": ch})
    t = wy[wy["year"].between(1617, 1640) & wy["term_years"].notna()]
    for lab, lo, hi in [("1617-1623", 1617, 1623), ("1624", 1624, 1624), ("1625-1640", 1625, 1640)]:
        s = t[t["year"].between(lo, hi)]["term_years"]
        a3.append({"window": lab, "years": hi - lo + 1, "term_stated": int(len(s)), "term_median": float(s.median()) if len(s) else math.nan,
                   "term_21": int((s == 21).sum()), "term_14_or_less": int((s <= 14).sum())})
    out["m_a3_1624"] = pd.DataFrame(a3)

    # ---------------- A4 extensions by decade
    dec = wy.assign(decade=wy["year"] // 10 * 10).groupby("decade").agg(entries=("number", "size"), extensions=("grant", lambda s: int((~s).sum())))
    dec["share"] = dec["extensions"] / dec["entries"]
    out["m_a4_extensions"] = dec.reset_index()

    # ---------------- B1/B2 field composition (Woodcroft, parsed grants) + Hulme
    wp = wy[wy["parsed"] & wy["grant"]].copy()
    wp["period"] = pd.cut(wp["year"], [1616, 1649, 1699, 1749, 1779, 1799, 1819, 1839, 1852],
                          labels=["1617-1649", "1650-1699", "1700-1749", "1750-1779", "1780-1799", "1800-1819", "1820-1839", "1840-1852"])
    b1 = wp.pivot_table(index="period", columns="field", values="number", aggfunc="size", fill_value=0, observed=False)
    b1 = b1.reindex(columns=[f for f in FIELD_ORDER if f in b1.columns], fill_value=0)
    H["field"] = H["subject"].map(classify)       # same dictionary as Woodcroft, applied to Hulme's subject line
    hf = H.pivot_table(index=lambda i: "1561-1603", columns="field", values="hulme_no", aggfunc="size", fill_value=0)
    b1_long = []
    for per, r in b1.iterrows():
        n = int(r.sum())
        for f, k in r.items():
            b1_long.append({"period": str(per), "source": "Woodcroft", "field": f, "count": int(k), "n": n, "share": k / n if n else math.nan})
    for f, k in hf.iloc[0].items():
        b1_long.append({"period": "1561-1603", "source": "Hulme (dictionary applied to subject)", "field": f, "count": int(k), "n": 55, "share": k / 55})
    out["m_b1_fields"] = pd.DataFrame(b1_long)
    wd = wp.assign(decade=wp["year"] // 10 * 10)
    b2 = []
    for d_, g in wd.groupby("decade"):
        vc = g[g["field"] != "other"]["field"].value_counts()
        b2.append({"decade": int(d_), "n": len(g), "classified": int(vc.sum()), "hhi": hhi(vc.values) if len(vc) else math.nan,
                   "top_field": vc.index[0] if len(vc) else "", "top_share": vc.iloc[0] / vc.sum() if len(vc) else math.nan,
                   "other_share": float((g["field"] == "other").mean())})
    out["m_b2_hhi"] = pd.DataFrame(b2)
    # Venetian sector table (secondary), mapped to our field keys for comparison
    ven = [("Mills — cereals", 42, "mills"), ("Mills — metals", 6, "mills"), ("Mills — textiles", 9, "mills"), ("Mills — wood saws", 6, "mills"),
           ("Mills — multiple usage", 22, "mills"), ("Fabrics", 8, "textiles"), ("Paint", 4, "chemicals"), ("Bread and food", 1, "food_drink"),
           ("Pottery and Porcelain Vases", 1, "glass_ceramics"), ("Agricultural machines", 4, "agriculture"), ("Drainage, mud removal", 20, "water"),
           ("Hydraulic pumps", 11, "water"), ("Armour and weapons", 7, "arms"), ("Arsenal", 3, "arms"), ("Mining", 3, "mining"),
           ("Perpetual Motion", 3, "steam_power"), ("Miscellaneous", 19, "other")]
    out["m_b3_venice_sectors"] = pd.DataFrame([{"sector_berveglieri": a, "count": b, "our_field": c} for a, b, c in ven])

    # ---------------- C1 foreign links
    c1 = wy[wy["parsed"] & wy["grant"]].assign(decade=lambda x: x["year"] // 10 * 10).groupby("decade").agg(
        n=("number", "size"), communication=("communication", "sum"), foreign_address=("foreign_address", "sum"), either=("foreign_link", "sum")).reset_index()
    for col in ("communication", "foreign_address", "either"):
        c1[col + "_share"] = c1[col] / c1["n"]
    ci = c1.apply(lambda r: wilson(int(r["either"]), int(r["n"])), axis=1)
    c1["either_ci_low"], c1["either_ci_high"] = [c[0] for c in ci], [c[1] for c in ci]
    out["m_c1_foreign_gb"] = c1
    hulme_tab = pd.DataFrame([("1561-1570", 15, 8, 0, 23), ("1571-1580", 4, 7, 1, 12), ("1581-1590", 2, 11, 1, 14), ("1591-1600", 0, 4, 2, 6), ("1601-1603", 0, 0, 0, 0)],
                             columns=["period", "hulme_alien", "hulme_native", "hulme_trade", "hulme_total"])
    H["period"] = pd.cut(H["year"], [1560, 1570, 1580, 1590, 1600, 1603], labels=hulme_tab["period"].tolist())
    ours = H.groupby("period", observed=False)["foreign_code"].agg(explicit=lambda s: int((s == "explicit").sum()), indirect=lambda s: int((s == "indirect").sum()))
    out["m_c1_hulme"] = hulme_tab.join(ours, on="period")
    nlp = NL[NL["privilege"]]
    c1nl = nlp.assign(period=pd.cut(nlp["year"], [1580, 1590, 1600, 1610, 1621], labels=["1581-1590", "1591-1600", "1601-1610", "1611-1621"])).groupby("period", observed=False).agg(
        n=("doc", "size"), foreign=("any_foreign", lambda s: int(s.fillna(False).astype(bool).sum())),
        foreign_incl_probable=("any_foreign_probable", lambda s: int(s.fillna(False).astype(bool).sum())),
        co=("n_patentees", lambda s: int((s >= 2).sum()))).reset_index()
    c1nl["foreign_share"] = c1nl["foreign"] / c1nl["n"]
    c1nl["foreign_incl_probable_share"] = c1nl["foreign_incl_probable"] / c1nl["n"]
    c1nl["co_share"] = c1nl["co"] / c1nl["n"]
    out["m_c1_foreign_nl"] = c1nl

    # ---------------- C2 co-grantees (England)
    c2 = wy[wy["parsed"] & wy["grant"] & wy["n_grantees"].notna()].assign(decade=lambda x: x["year"] // 10 * 10).groupby("decade").agg(
        n=("number", "size"), co=("n_grantees", lambda s: int((s >= 2).sum()))).reset_index()
    c2["co_share"] = c2["co"] / c2["n"]
    out["m_c2_cogrant"] = c2

    # ---------------- D1 stated terms
    d1 = []
    for src, s in [("GB Hulme 1561-1603", H["term_years"]),
                   ("GB Woodcroft 1617-1623", wy[wy["year"].between(1617, 1623)]["term_years"]),
                   ("GB Woodcroft 1625-1700", wy[wy["year"].between(1625, 1700)]["term_years"]),
                   ("GB Woodcroft 1701-1819", wy[wy["year"].between(1701, 1819)]["term_years"]),
                   ("NL Buning 1581-1621", NL[NL["privilege"]]["gets"].where(lambda v: (v > 0) & (v < 100)))]:
        s = pd.to_numeric(s, errors="coerce").dropna()
        d1.append({"source": src, "n_stated": int(len(s)), "median": float(s.median()) if len(s) else math.nan, "p25": float(s.quantile(.25)) if len(s) else math.nan,
                   "p75": float(s.quantile(.75)) if len(s) else math.nan, "min": float(s.min()) if len(s) else math.nan, "max": float(s.max()) if len(s) else math.nan,
                   "values": json.dumps({int(k): int(v) for k, v in s.value_counts().sort_index().items()})})
    if F is not None:
        s = pd.to_numeric(F.loc[F["kind"] == "privilege", "term_years"], errors="coerce").dropna()
        d1.append({"source": "VE Fulin 1469-1526 (printing)", "n_stated": int(len(s)), "median": float(s.median()), "p25": float(s.quantile(.25)), "p75": float(s.quantile(.75)),
                   "min": float(s.min()), "max": float(s.max()), "values": json.dumps({int(k): int(v) for k, v in s.value_counts().sort_index().items()})})
    out["m_d1_terms"] = pd.DataFrame(d1)
    d2 = wy[wy["year"].between(1617, 1700)].groupby("year").agg(n=("number", "size"), stated=("term_years", lambda s: int(s.notna().sum())),
                                                                 le14=("term_years", lambda s: int((s <= 14).sum())), eq21=("term_years", lambda s: int((s == 21).sum())),
                                                                 other_term=("term_other", lambda s: int(s.notna().sum()))).reset_index()
    out["m_d2_term_shift"] = d2
    d3 = wy[wy["parsed"] & wy["year"].between(1617, 1759)].assign(decade=lambda x: x["year"] // 10 * 10).groupby("decade").agg(
        n=("number", "size"), rent=("rent_clause", "sum"), proviso=("proviso_clause", "sum")).reset_index()
    d3["rent_share"], d3["proviso_share"] = d3["rent"] / d3["n"], d3["proviso"] / d3["n"]
    out["m_d3_clauses"] = d3

    # ---------------- P Stationers' Register
    S["enterer_list"] = S["enterers"].fillna("").map(lambda s: [x for x in s.split(";") if x])
    p1 = S.groupby("year").agg(entries=("sro_id", "size"), works=("works", "sum")).reindex(range(1557, 1641), fill_value=0).reset_index()
    p1["gap"] = p1["year"].between(1571, 1575)
    out["m_p1_sro_annual"] = p1
    p2 = []
    for y, g in S.groupby("year"):
        credit = {}
        for lst in g["enterer_list"]:
            for k in lst:
                credit[k] = credit.get(k, 0) + 1 / len(lst)
        v = sorted(credit.values(), reverse=True)
        tot = sum(v)
        p2.append({"year": y, "entries": len(g), "enterers": len(v), "hhi": hhi(v) if v else math.nan, "top5_share": sum(v[:5]) / tot if tot else math.nan,
                   "top1": max(credit, key=credit.get) if credit else ""})
    out["m_p2_sro_concentration"] = pd.DataFrame(p2)
    st = S["status"].fillna("")
    p3 = S.assign(shared=st.str.contains("shared"), reassigned=st.str.contains("reassigned"), cancelled=st.str.contains("cancelled"), stock=st.str.contains("stock"),
                  decade=S["year"] // 10 * 10).groupby("decade").agg(entries=("sro_id", "size"), shared=("shared", "sum"), reassigned=("reassigned", "sum"),
                                                                       cancelled=("cancelled", "sum"), stock=("stock", "sum")).reset_index()
    for c in ("shared", "reassigned", "cancelled"):
        p3[c + "_share"] = p3[c] / p3["entries"]
    out["m_p3_sro_status"] = p3
    fee = S[S["fee_pence"].notna() & (S["fee_pence"] > 0)]
    p4 = fee.groupby("year").agg(with_fee=("sro_id", "size"), fee6=("fee_pence", lambda s: int((s == 6).sum())), median_fee=("fee_pence", "median")).reset_index()
    p4["fee6_share"] = p4["fee6"] / p4["with_fee"]
    out["m_p4_sro_fees"] = p4
    zero = S.groupby("year")["fee_pence"].apply(lambda s: int((s.fillna(0) == 0).sum()))
    p4["no_fee_stated"] = p4["year"].map(zero).fillna(0).astype(int)

    # ---------------- Venice printing (Fulin)
    if F is not None:
        fp = F[F["kind"] == "privilege"]
        v1 = fp.groupby("year").agg(privileges=("number", "size"), author=("beneficiary_type", lambda s: int(s.isin(["author", "both"]).sum())),
                                    printer=("beneficiary_type", lambda s: int((s == "printer").sum())), term_stated=("term_years", lambda s: int(pd.to_numeric(s, errors="coerce").notna().sum()))).reindex(range(1469, 1527), fill_value=0).reset_index()
        out["m_v1_fulin_annual"] = v1
        out["m_v1_fulin_kinds"] = F["kind"].fillna("unknown").value_counts().rename_axis("kind").reset_index(name="documents")

    for k, df in out.items():
        df.to_csv(DER / f"{k}.csv", index=False, encoding="utf-8")
        print(k, df.shape)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
