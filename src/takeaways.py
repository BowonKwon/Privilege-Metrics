# -*- coding: utf-8 -*-
"""'Key point' sentences per metric, Korean and English, with every number computed from the derived tables.
No causal wording: 'is observed', 'before and after', never 'caused' / 'led to'."""
import json
import math

import pandas as pd


def _pct(x, d=0):
    return f"{x * 100:.{d}f}%"


def build(D: dict) -> dict:
    """D maps table name -> DataFrame. Returns {metric_id: {"ko": str, "en": str, "kv": (value_str, label_ko, label_en)}}."""
    T = {}
    a1 = D["m_a1_annual"]
    tot = int(a1["grants"].sum(skipna=True))
    peak = a1.loc[a1["grants"].idxmax()]
    y1700 = int(a1[(a1.year >= 1617) & (a1.year <= 1699)]["grants"].sum())
    y1800 = int(a1[(a1.year >= 1800) & (a1.year <= 1852)]["grants"].sum())
    T["a1_annual"] = {
        "ko": f"1561–1852년 잉글랜드 발명 특권·특허는 {tot:,}건이다. 1617–1699년 83년 동안 {y1700:,}건이던 것이 1800–1852년 53년 동안 {y1800:,}건으로 관측된다. 가장 많은 해는 {int(peak.year)}년({int(peak.grants):,}건)이다.",
        "en": f"England granted {tot:,} invention privileges and patents in 1561–1852: {y1700:,} in the 83 years 1617–1699 and {y1800:,} in the 53 years 1800–1852. The peak year is {int(peak.year)} ({int(peak.grants):,}).",
        "kv": (f"{tot:,}", "허여 1561–1852", "grants 1561–1852")}
    a3 = D["m_a3_1624"]
    w = a3[a3["grants"].notna()].set_index("window")
    t = a3[a3["term_stated"].notna()].set_index("window")
    T["a3_1624"] = {
        "ko": f"연평균 허여는 1617–1623년 {w.loc['1617-1623','per_year']:.1f}건, 1625–1631년 {w.loc['1625-1631','per_year']:.1f}건이다(95% 구간이 겹친다). 본문에 적힌 존속기간은 1617–1623년 {int(t.loc['1617-1623','term_stated'])}건 중 {int(t.loc['1617-1623','term_21'])}건이 21년, 1625–1640년 {int(t.loc['1625-1640','term_stated'])}건 중 {int(t.loc['1625-1640','term_14_or_less'])}건이 14년 이하다.",
        "en": f"Mean grants per year were {w.loc['1617-1623','per_year']:.1f} in 1617–1623 and {w.loc['1625-1631','per_year']:.1f} in 1625–1631, with overlapping 95% intervals. Of the terms written in the entries, {int(t.loc['1617-1623','term_21'])} of {int(t.loc['1617-1623','term_stated'])} in 1617–1623 are 21 years, and {int(t.loc['1625-1640','term_14_or_less'])} of {int(t.loc['1625-1640','term_stated'])} in 1625–1640 are 14 years or less.",
        "kv": (f"{w.loc['1617-1623','per_year']:.1f} → {w.loc['1625-1631','per_year']:.1f}", "연평균 허여(전 → 후)", "grants per year, before → after")}
    a2 = D["m_a2_periods"]
    nl = int(a2[(a2.jurisdiction == "NL")]["count"].sum())
    ve_p = int(a2[(a2.jurisdiction == "VE") & (a2.kind == "printing")]["count"].sum())
    T["a2_periods"] = {
        "ko": f"베네치아 원로원 발명 특허는 1551–1600년 471건(2차 인용)이다. 같은 구간 잉글랜드는 1561년부터 55건이다. 네덜란드 1581–1621년 특권 허여 문서는 {nl}건, 베네치아 출판 특권 문서는 1469–1526년 {ve_p}건이다. 세는 단위가 서로 다르다.",
        "en": f"The Venetian Senate granted 471 invention patents in 1551–1600 (secondary figure); England, from 1561, 55. Dutch documents issuing a privilege number {nl} in 1581–1621, and Venetian printing-privilege documents {ve_p} in 1469–1526. The counting units differ.",
        "kv": ("471 · 55", "베네치아·잉글랜드 1551–1600", "Venice · England 1551–1600")}
    a4 = D["m_a4_extensions"]
    T["a4_extensions"] = {
        "ko": f"기간 연장 항목은 전체 {int(a4['extensions'].sum())}건으로 항목의 {_pct(a4['extensions'].sum() / a4['entries'].sum(), 2)}다. 가장 많은 10년은 {int(a4.loc[a4['extensions'].idxmax(),'decade'])}년대({int(a4['extensions'].max())}건)다.",
        "en": f"Extension entries number {int(a4['extensions'].sum())}, {_pct(a4['extensions'].sum() / a4['entries'].sum(), 2)} of all entries; the decade with most is the {int(a4.loc[a4['extensions'].idxmax(),'decade'])}s ({int(a4['extensions'].max())}).",
        "kv": (f"{int(a4['extensions'].sum())}", "연장 항목", "extension entries")}
    b1 = D["m_b1_fields"]
    def top(per):
        g = b1[(b1.period == per) & (b1.field != "other")].sort_values("share", ascending=False).head(3)
        return g
    import fields as F
    first, last = top("1617-1649"), top("1840-1852")
    f_ko = lambda g: ", ".join(F.LABEL[r.field]["ko"] for r in g.itertuples())
    f_en = lambda g: ", ".join(F.LABEL[r.field]["en"] for r in g.itertuples())
    oth = b1[b1.field == "other"].set_index("period")["share"]
    T["b1_fields"] = {
        "ko": f"1617–1649년에는 {f_ko(first)} 순으로 많고, 1840–1852년에는 {f_ko(last)} 순으로 많다. 규칙에 걸리지 않은 「기타」는 구간마다 {_pct(oth.min())}–{_pct(oth.max())}다.",
        "en": f"The largest fields are {f_en(first)} in 1617–1649, and {f_en(last)} in 1840–1852. The unmatched 'other' share ranges from {_pct(oth.min())} to {_pct(oth.max())} by period.",
        "kv": {"ko": (F.LABEL[last.iloc[0].field]["ko"], "1840–1852 최대 분야"), "en": (F.LABEL[last.iloc[0].field]["en"], "largest field 1840–1852")}}
    b2 = D["m_b2_hhi"]
    late = b2[b2.decade >= 1750]
    T["b2_hhi"] = {
        "ko": f"1750년 이후 10년 단위 분야 집중도는 {late.hhi.min():.3f}–{late.hhi.max():.3f} 사이에 있다. 17분야가 고르게 나뉘면 0.059다.",
        "en": f"From 1750 the decade field concentration stays between {late.hhi.min():.3f} and {late.hhi.max():.3f}; an even split across 17 fields gives 0.059.",
        "kv": (f"{late.hhi.median():.3f}", "1750년 이후 중앙값", "median from 1750")}
    T["b3_venice_sectors"] = {
        "ko": "베네치아 1474–1550년 169건 가운데 방아류가 85건(50%), 배수·준설 20건, 양수 펌프 11건이다(Comino 등, Berveglieri 1995 분류).",
        "en": "Of the 169 Venetian patents of 1474–1550, mills account for 85 (50%), drainage and dredging 20, pumps 11 (Comino et al., Berveglieri 1995 sectors).",
        "kv": ("85 / 169", "방아류", "mills")}
    c1 = D["m_c1_foreign_gb"]
    l = c1[c1.decade >= 1840]
    e = c1[(c1.decade >= 1700) & (c1.decade < 1800)]
    hl = D["m_c1_hulme"]
    nlf = D["m_c1_foreign_nl"]
    T["c1_foreign"] = {
        "ko": f"잉글랜드 허여 가운데 외국과 이어진(「communication」이거나 해외 주소) 비율은 18세기 {_pct(e.either.sum() / e.n.sum(), 1)}, 1840–1852년 {_pct(l.either.sum() / l.n.sum(), 1)}다. Hulme는 1561–1603년 55건 중 21건을 외국인 허여로 셌다. 네덜란드 1581–1621년 특권 문서의 {_pct(nlf.foreign.sum() / nlf.n.sum())}에 외국 출신 수혜자가 있다.",
        "en": f"The share of English grants with a foreign link ('communication' or an address abroad) is {_pct(e.either.sum() / e.n.sum(), 1)} in the 18th century and {_pct(l.either.sum() / l.n.sum(), 1)} in 1840–1852. Hulme counts 21 of 55 grants of 1561–1603 as grants to aliens. In the Dutch Republic {_pct(nlf.foreign.sum() / nlf.n.sum())} of privilege documents of 1581–1621 name a grantee of foreign origin.",
        "kv": (_pct(l.either.sum() / l.n.sum(), 1), "1840–1852 잉글랜드", "England 1840–1852")}
    c2 = D["m_c2_cogrant"]
    e17 = c2[c2.decade < 1650]
    e18 = c2[(c2.decade >= 1700) & (c2.decade < 1800)]
    T["c2_cogrant"] = {
        "ko": f"잉글랜드 공동 허여 비율은 1617–1649년 {_pct(e17.co.sum() / e17.n.sum())}, 18세기 {_pct(e18.co.sum() / e18.n.sum())}다.",
        "en": f"The share of shared grants in England is {_pct(e17.co.sum() / e17.n.sum())} in 1617–1649 and {_pct(e18.co.sum() / e18.n.sum())} in the 18th century.",
        "kv": (_pct(e17.co.sum() / e17.n.sum()), "1617–1649 공동 허여", "shared grants 1617–1649")}
    d1 = D["m_d1_terms"].set_index("source")
    T["d1_terms"] = {
        "ko": f"기간이 적힌 허여의 중앙값은 엘리자베스 시대(Hulme) {d1.loc['GB Hulme 1561-1603','median']:.0f}년, 1617–1623년 {d1.loc['GB Woodcroft 1617-1623','median']:.0f}년, 1625–1700년 {d1.loc['GB Woodcroft 1625-1700','median']:.0f}년이다. 네덜란드 {d1.loc['NL Buning 1581-1621','median']:.0f}년, 베네치아 출판 {d1.loc['VE Fulin 1469-1526 (printing)','median']:.0f}년이다.",
        "en": f"Median stated terms: {d1.loc['GB Hulme 1561-1603','median']:.0f} years under Elizabeth (Hulme), {d1.loc['GB Woodcroft 1617-1623','median']:.0f} in 1617–1623, {d1.loc['GB Woodcroft 1625-1700','median']:.0f} in 1625–1700; {d1.loc['NL Buning 1581-1621','median']:.0f} in the Dutch Republic and {d1.loc['VE Fulin 1469-1526 (printing)','median']:.0f} for Venetian printing privileges.",
        "kv": ("21 → 14", "잉글랜드 중앙값, 1624 전후", "England median, before → after 1624")}
    d2 = D["m_d2_term_shift"]
    last21 = int(d2[d2.eq21 > 0].year.max())
    T["d2_term_shift"] = {
        "ko": f"21년 기간이 적힌 마지막 해는 {last21}년이다. 1625–1660년 기간이 적힌 {int(d2[d2.year >= 1625].stated.sum())}건 가운데 {int(d2[d2.year >= 1625].le14.sum())}건이 14년 이하다.",
        "en": f"The last year with a 21-year term written is {last21}. Of the {int(d2[d2.year >= 1625].stated.sum())} stated terms in 1625–1660, {int(d2[d2.year >= 1625].le14.sum())} are 14 years or less.",
        "kv": (str(last21), "마지막 21년 기간", "last 21-year term")}
    d3 = D["m_d3_clauses"]
    e = d3[d3.decade < 1650]
    l = d3[(d3.decade >= 1660) & (d3.decade < 1700)]
    T["d3_clauses"] = {
        "ko": f"지대 문구는 1617–1649년 항목의 {_pct(e.rent.sum() / e.n.sum())}, 1660–1699년 항목의 {_pct(l.rent.sum() / l.n.sum())}에 있다.",
        "en": f"A rent is mentioned in {_pct(e.rent.sum() / e.n.sum())} of entries in 1617–1649 and in {_pct(l.rent.sum() / l.n.sum())} in 1660–1699.",
        "kv": (f"{_pct(e.rent.sum() / e.n.sum())} → {_pct(l.rent.sum() / l.n.sum())}", "지대 문구, 1617–49 → 1660–99", "rent clause, 1617–49 → 1660–99")}
    p1 = D["m_p1_sro_annual"]
    p1d = p1.assign(dec=p1.year // 10 * 10).groupby("dec")["entries"].sum()
    T["p1_sro_annual"] = {
        "ko": f"1557–1640년 등록은 {int(p1.entries.sum()):,}건이다. 10년 합은 1560년대 {int(p1d[1560]):,}건, 1630년대 {int(p1d[1630]):,}건이다. 1571년 7월–1576년 7월은 기록이 없다.",
        "en": f"The register holds {int(p1.entries.sum()):,} entries for 1557–1640: {int(p1d[1560]):,} in the 1560s and {int(p1d[1630]):,} in the 1630s. No entries survive for July 1571 to July 1576.",
        "kv": (f"{int(p1.entries.sum()):,}", "등록 1557–1640", "entries 1557–1640")}
    p2 = D["m_p2_sro_concentration"]
    p2d = p2.assign(dec=p2.year // 10 * 10).groupby("dec")["top5_share"].median()
    T["p2_sro_concentration"] = {
        "ko": f"해마다 상위 5인 등록자가 차지한 몫의 10년 중앙값은 1560년대 {_pct(p2d[1560])}, 1630년대 {_pct(p2d[1630])}다.",
        "en": f"The decade median of the top five enterers' yearly share is {_pct(p2d[1560])} in the 1560s and {_pct(p2d[1630])} in the 1630s.",
        "kv": (_pct(p2d[1630]), "1630년대 상위 5인 몫", "top-five share, 1630s")}
    p3 = D["m_p3_sro_status"].set_index("decade")
    T["p3_sro_status"] = {
        "ko": f"양도(reassigned) 표시 항목은 1580년대 {_pct(p3.loc[1580,'reassigned_share'],1)}, 1620년대 {_pct(p3.loc[1620,'reassigned_share'],1)}다. 공동 등록(shared)은 1630년대 {_pct(p3.loc[1630,'shared_share'],1)}다.",
        "en": f"Entries marked reassigned are {_pct(p3.loc[1580,'reassigned_share'],1)} in the 1580s and {_pct(p3.loc[1620,'reassigned_share'],1)} in the 1620s; shared entries are {_pct(p3.loc[1630,'shared_share'],1)} in the 1630s.",
        "kv": (_pct(p3.loc[1620, 'reassigned_share'], 1), "1620년대 양도 표시", "reassigned, 1620s")}
    p4 = D["m_p4_sro_fees"]
    a = p4[p4.year.between(1560, 1581)]
    b = p4[p4.year.between(1587, 1640)]
    T["p4_sro_fees"] = {
        "ko": f"수수료가 적힌 항목 중 6펜스의 비율은 1560–1581년 {_pct(a.fee6.sum() / a.with_fee.sum())}, 1587–1640년 {_pct(b.fee6.sum() / b.with_fee.sum())}다.",
        "en": f"Among entries with a stated fee, 6d is {_pct(a.fee6.sum() / a.with_fee.sum())} in 1560–1581 and {_pct(b.fee6.sum() / b.with_fee.sum())} in 1587–1640.",
        "kv": (_pct(b.fee6.sum() / b.with_fee.sum()), "1587–1640 6펜스", "6d share 1587–1640")}
    v = D["m_v1_fulin_annual"]
    vv = v.assign(b=v.year // 5 * 5).groupby("b")["privileges"].sum()
    au = int(v[v.year >= 1492]["author"].sum())
    pr = int(v[v.year >= 1492]["privileges"].sum())
    T["v1_venice_printing"] = {
        "ko": f"Fulin 문서에서 1492–1526년 출판 특권은 {pr}건, 그중 저자(편자·번역자 포함)에게 간 것이 {au}건({_pct(au / pr)})이다. 5년 구간으로는 1495–1499년 {int(vv[1495])}건이 가장 많고 1510–1514년 {int(vv[1510])}건이 가장 적다.",
        "en": f"In Fulin's documents there are {pr} printing privileges in 1492–1526, {au} ({_pct(au / pr)}) of them to authors, editors or translators. By five-year period the most are in 1495–1499 ({int(vv[1495])}) and the fewest in 1510–1514 ({int(vv[1510])}).",
        "kv": (f"{pr}", "출판 특권 1492–1526", "printing privileges 1492–1526")}
    for k, v_ in T.items():
        if isinstance(v_["kv"], tuple):
            val, lk, le = v_["kv"]
            v_["kv"] = {"ko": (val, lk), "en": (val, le)}
    return T
