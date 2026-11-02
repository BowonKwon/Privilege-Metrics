# -*- coding: utf-8 -*-
"""Build the static site (ko/en) into site/.

  python src/build_site.py
"""
import gzip
import json
import math
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fields as FL  # noqa: E402
import takeaways  # noqa: E402
from registry import METRICS, PRIOR, SERIES, SITE, SOURCES  # noqa: E402
from site_kit import CSS, JS, esc, fig, fmt, legend, svg_bars, svg_lines, table_html, cap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DER, COD, OUT = ROOT / "data" / "derived", ROOT / "data" / "coding", ROOT / "site"
VERSION = SITE["version"]
BUILD_DATE = "2026-11-03"
REPO = "https://github.com/BowonKwon/Privilege-Metrics"

T = {
    "ko": dict(site=SITE["ko"]["title"], tagline=SITE["ko"]["subtitle"], nav_home="홈", nav_metrics="지표", nav_places="관할", nav_eras="연대",
               nav_prior="선행 결과", nav_reading="읽기용 판", nav_data="데이터", nav_method="방법·한계", lang_other="English",
               definition="정의", formula="공식", reading="읽는 법", caveat="한계", source="자료원", unit="단위", key="핵심",
               reliability="신뢰도 카드", table="표", download="CSV 내려받기", metric_list="지표 목록", license="라이선스", built="생성일", version="판",
               hub="공개 자료 전체", prior="선행 결과", series="계열", year="연도", decade="10년", period="구간", share="비율", n="건수",
               rel={"exact": "집계값 — 구조화된 원자료에서 그대로 셌거나, 쪽 이미지와 대조해 손으로 옮긴 값", "ocr": "OCR 계수 — 스캔 OCR에서 규칙으로 센 값. 아래는 쪽 이미지 표본으로 잰 오류",
                    "sampled": "규칙 분류 — 단어 규칙으로 나눈 값. 아래는 독립 코딩 표본으로 잰 정밀도", "secondary": "2차 인용 — 문헌 수치를 옮긴 값. 이 사이트가 다시 세지 않았다"}),
    "en": dict(site=SITE["en"]["title"], tagline=SITE["en"]["subtitle"], nav_home="Home", nav_metrics="Metrics", nav_places="Jurisdictions", nav_eras="Timeline",
               nav_prior="Prior results", nav_reading="Reading edition", nav_data="Data", nav_method="Method and limits", lang_other="한국어",
               definition="Definition", formula="Formula", reading="How to read it", caveat="Caveats", source="Sources", unit="Unit", key="Key point",
               reliability="Reliability card", table="Table", download="Download CSV", metric_list="All metrics", license="License", built="Built", version="Version",
               hub="All public materials", prior="Prior results", series="Series", year="year", decade="decade", period="period", share="share", n="count",
               rel={"exact": "Exact count: counted straight from a structured source, or transcribed by hand and checked against the page images", "ocr": "OCR count: counted by rule from scanned OCR text; below, the error measured on a sample checked against page images",
                    "sampled": "Rule-based classification: assigned by word rules; below, the precision measured on an independently coded sample", "secondary": "Secondary figure: quoted from the literature and not recounted here"}),
}
JUR = {"GB": {"ko": "잉글랜드", "en": "England"}, "VE": {"ko": "베네치아", "en": "Venice"}, "NL": {"ko": "네덜란드", "en": "Dutch Republic"}}


def page(lang, title, body, depth=1, active="", desc=""):
    t = T[lang]
    root = "../" * depth
    other = "en" if lang == "ko" else "ko"
    hub = "" if lang == "ko" else "en/"
    nav = [("home", f"{root}{lang}/index.html", t["nav_home"]), ("metrics", f"{root}{lang}/metrics/index.html", t["nav_metrics"]),
           ("places", f"{root}{lang}/places.html", t["nav_places"]), ("eras", f"{root}{lang}/eras.html", t["nav_eras"]),
           ("prior", f"{root}{lang}/prior.html", t["nav_prior"]), ("reading", f"{root}{lang}/reading.html", t["nav_reading"]),
           ("data", f"{root}{lang}/data.html", t["nav_data"]), ("method", f"{root}{lang}/method.html", t["nav_method"])]
    navh = "".join(f'<a href="{h}"{" class=\"on\"" if k == active else ""}>{n}</a>' for k, h, n in nav)
    attribution = ("영국 출판업조합 등록부 집계는 Bergel·Gadd 편 Stationers' Register Online(CC BY-SA)을, 네덜란드 집계는 Buning·Looijesteijn 자료(CC BY 4.0)를 이용했다. 나머지는 퍼블릭 도메인 인쇄본에서 직접 셌다."
                   if lang == "ko" else
                   "Stationers' Register counts use Stationers' Register Online, ed. Bergel and Gadd (CC BY-SA); Dutch counts use the Buning and Looijesteijn data (CC BY 4.0). Everything else was counted from public-domain printed sources.")
    full = title if title == t["site"] else f"{title} — {t['site']}"
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full)}</title><meta name="description" content="{esc(desc or t['tagline'])}">
<script>(function(){{var q=new URLSearchParams(location.search).get("theme");if(q==="light"||q==="dark"){{localStorage.setItem("ppm-theme",q)}}else if(q==="auto"){{localStorage.removeItem("ppm-theme")}}var v=localStorage.getItem("ppm-theme");if(v)document.documentElement.setAttribute("data-theme",v)}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600&display=swap" rel="stylesheet">
<style>{CSS}
:lang(ko) .prose p,:lang(ko) .take p,:lang(ko) .card small,:lang(ko) figcaption,:lang(ko) dd{{word-break:keep-all}}
td.num,th.num{{white-space:nowrap}}</style></head><body>
<header><a class="brand" href="{root}{lang}/index.html">{t['site']}</a>
<nav>{navh}</nav>
<div class="right"><button id="theme" class="theme" type="button" aria-label="theme">◑</button><a class="lang" href="{root}{other}/index.html">{t['lang_other']}</a></div></header>
<main>{body}</main>
<footer>{t['site']} · {t['version']} {VERSION} · {t['built']} {BUILD_DATE} · <a href="{REPO}">GitHub</a> · {t['hub']} <a href="https://bowonkwon.github.io/{hub}">bowonkwon.github.io</a><br>{attribution}</footer>
<script>{JS}</script></body></html>"""


def take(text, lang):
    return f'<div class="take"><div class="l">{T[lang]["key"]}</div><p>{esc(text)}</p></div>'


def load():
    D = {p.stem: pd.read_csv(p) for p in DER.glob("m_*.csv")}
    rel = json.loads((DER / "reliability.json").read_text(encoding="utf-8")) if (DER / "reliability.json").exists() else {}
    return D, rel


# ------------------------------------------------------------------ figures per metric
def figure(mid, D, lang):
    ko = lang == "ko"
    if mid == "a1_annual":
        a = D["m_a1_annual"]
        e = a[(a.year <= 1700)]
        l = a[(a.year >= 1700)]
        s1 = svg_lines([("grants", [(r.year, float(r.grants) if not pd.isna(r.grants) else math.nan) for r in e.itertuples()], 0)], ",.0f",
                       bands=[(1604, 1616, "gap" if not ko else "목록 공백"), (1624, 1625, "1624")], xstep=20)
        s2 = svg_lines([("grants", [(r.year, float(r.grants)) for r in l.itertuples()], 0)], ",.0f", xstep=20)
        return (fig(s1, "1561–1700. 음영은 두 목록 사이의 공백인 1604–1616년과 1624년." if ko else "1561–1700. Shaded: 1604–1616, the gap between the two lists, and 1624.")
                + fig(s2, "1700–1852." if ko else "1700–1852."))
    if mid == "a2_periods":
        a = D["m_a2_periods"]
        items = [(f"{JUR[r.jurisdiction][lang]} · {('발명' if r.kind == 'invention' else '출판') if ko else r.kind} · {r.period}{' *' if r.basis == 'secondary' else ''}", float(r['count']), {"GB": 0, "VE": 1, "NL": 2}[r.jurisdiction])
                 for _, r in a[a["period"] != "before 1474"].iterrows() if r.period not in ("1751-1800", "1801-1852")]
        return fig(svg_bars(items, ",.0f", label_w=330), "* 2차 인용(Comino 등). 1751년 이후 잉글랜드는 표에만 둔다." if ko else "* Secondary figure (Comino et al.). England after 1750 is in the table only.")
    if mid == "a3_1624":
        a = D["m_a3_1624"]
        w = a[a.grants.notna()]
        items = [(r.window, float(r.per_year), 0) for r in w.itertuples()]
        err = {r.window: (r.ci_low, r.ci_high) for r in w.itertuples()}
        return fig(svg_bars(items, ".1f", label_w=140, errors=err), "연평균 허여와 95% 포아송 구간." if ko else "Mean grants per year with 95% Poisson intervals.")
    if mid == "a4_extensions":
        a = D["m_a4_extensions"]
        return fig(svg_lines([("ext", [(r.decade, float(r.extensions)) for r in a.itertuples()], 0)], ",.0f", xstep=20), "10년별 연장 항목 수." if ko else "Extension entries per decade.")
    if mid == "b1_fields":
        b = D["m_b1_fields"]
        b = b[b.source == "Woodcroft"]
        per = list(dict.fromkeys(b.period))
        x = {p: i for i, p in enumerate(per)}
        top = b[b.field != "other"].groupby("field")["count"].sum().sort_values(ascending=False).head(4).index.tolist()
        series = [(FL.LABEL[f][lang], [(x[r.period], float(r.share)) for r in b[b.field == f].itertuples()], i) for i, f in enumerate(top)]
        svg = svg_lines(series, ".0%", xstep=1)
        cap_ = ("가로축은 구간 번호(0 = " + per[0] + ", " + str(len(per) - 1) + " = " + per[-1] + "). 많은 네 분야만 그렸다. 전체는 표."
                if ko else "x axis: period index (0 = " + per[0] + ", " + str(len(per) - 1) + " = " + per[-1] + "). The four largest fields only; all fields are in the table.")
        return fig(svg, cap_)
    if mid == "b2_hhi":
        b = D["m_b2_hhi"]
        return fig(svg_lines([("HHI", [(r.decade, float(r.hhi)) for r in b.itertuples()], 0), ("other", [(r.decade, float(r.other_share)) for r in b.itertuples()], 1)], ".2f", xstep=20),
                   "HHI(위)와 「기타」 비율." if ko else "HHI and the 'other' share.")
    if mid == "b3_venice_sectors":
        b = D["m_b3_venice_sectors"]
        return fig(svg_bars([(r.sector_berveglieri, float(r.count), 1) for r in b.itertuples()], ",.0f", label_w=260), "Comino 등 표 A1." if ko else "Comino et al., Table A1.")
    if mid == "c1_foreign":
        c = D["m_c1_foreign_gb"]
        c = c[c.decade >= 1700]
        s = svg_lines([("communication", [(r.decade, float(r.communication_share)) for r in c.itertuples()], 0),
                       ("address abroad" if not ko else "해외 주소", [(r.decade, float(r.foreign_address_share)) for r in c.itertuples()], 1),
                       ("either" if not ko else "둘 중 하나", [(r.decade, float(r.either_share)) for r in c.itertuples()], 2)], ".0%", xstep=20)
        return fig(s, "잉글랜드 1700–1852, 10년별." if ko else "England 1700–1852, by decade.")
    if mid == "c2_cogrant":
        c = D["m_c2_cogrant"]
        return fig(svg_lines([("co", [(r.decade, float(r.co_share)) for r in c.itertuples()], 0)], ".0%", xstep=20), "잉글랜드, 10년별." if ko else "England, by decade.")
    if mid == "d1_terms":
        d = D["m_d1_terms"]
        d = d[d.n_stated > 0]
        items = [(r.source, float(r["median"]), 0) for _, r in d.iterrows()]
        err = {r.source: (r.p25, r.p75) for _, r in d.iterrows()}
        return fig(svg_bars(items, ".0f", label_w=300, errors=err), "중앙값(막대)과 사분위 범위(선)." if ko else "Median (bar) and interquartile range (line).")
    if mid == "d2_term_shift":
        d = D["m_d2_term_shift"]
        return fig(svg_lines([("21", [(r.year, float(r.eq21)) for r in d.itertuples()], 0), ("≤14", [(r.year, float(r.le14)) for r in d.itertuples()], 1)], ",.0f",
                             bands=[(1624, 1625, "1624")], xstep=5), "해마다 21년·14년 이하로 적힌 허여 수." if ko else "Grants per year with a written term of 21 years and of 14 years or less.")
    if mid == "d3_clauses":
        d = D["m_d3_clauses"]
        return fig(svg_lines([("rent", [(r.decade, float(r.rent_share)) for r in d.itertuples()], 0), ("proviso", [(r.decade, float(r.proviso_share)) for r in d.itertuples()], 1)], ".0%", xstep=20),
                   "10년별 언급 비율." if ko else "Share of entries mentioning the clause, by decade.")
    if mid == "p1_sro_annual":
        p = D["m_p1_sro_annual"]
        return fig(svg_lines([("entries", [(r.year, float(r.entries)) for r in p.itertuples()], 0)], ",.0f", bands=[(1571, 1576, "gap"), (1637, 1638, "1637")], xstep=10),
                   "음영: 기록이 없는 1571–1576년, 등록이 의무가 된 1637년." if ko else "Shaded: 1571–1576, for which no entries survive, and 1637, when entrance became compulsory.")
    if mid == "p2_sro_concentration":
        p = D["m_p2_sro_concentration"]
        p = p[p.entries >= 20]
        return fig(svg_lines([("top 5", [(r.year, float(r.top5_share)) for r in p.itertuples()], 0)], ".0%", xstep=10), "등록 20건 이상인 해만." if ko else "Years with at least 20 entries.")
    if mid == "p3_sro_status":
        p = D["m_p3_sro_status"]
        return fig(svg_lines([("reassigned", [(r.decade, float(r.reassigned_share)) for r in p.itertuples()], 0), ("shared", [(r.decade, float(r.shared_share)) for r in p.itertuples()], 1)], ".0%", xstep=10),
                   "10년별." if ko else "By decade.")
    if mid == "p4_sro_fees":
        p = D["m_p4_sro_fees"]
        p = p[p.with_fee >= 10]
        return fig(svg_lines([("6d", [(r.year, float(r.fee6_share)) for r in p.itertuples()], 0)], ".0%", bands=[(1582, 1587, "1582–1587")], xstep=10),
                   "수수료가 적힌 항목 10건 이상인 해만." if ko else "Years with at least 10 entries with a fee.")
    if mid == "v1_venice_printing":
        v = D["m_v1_fulin_annual"]
        v = v.assign(b=v.year // 5 * 5).groupby("b")[["privileges", "author", "printer"]].sum().reset_index()
        s = svg_lines([("all" if not ko else "전체", [(r.b, float(r.privileges)) for r in v.itertuples()], 0),
                       ("author" if not ko else "저자", [(r.b, float(r.author)) for r in v.itertuples()], 1),
                       ("printer" if not ko else "인쇄업자", [(r.b, float(r.printer)) for r in v.itertuples()], 2)], ",.0f", bands=[(1517, 1518, "1517")], xstep=10)
        return fig(s, "5년 구간 합(가로축은 구간 첫해). 1525 구간은 1525–1526년 두 해다." if ko else "Five-year sums (x = first year of the period). The 1525 period covers only 1525–1526.")
    return ""


def col_spec(df, c):
    if not pd.api.types.is_numeric_dtype(df[c]):
        return None
    if c in ("year", "decade", "number"):
        return "d"
    if "share" in c or c.startswith("either_ci"):
        return ".1%"
    if c == "hhi":
        return ".3f"
    v = df[c].dropna()
    return ".2f" if len(v) and (v % 1 != 0).any() else ",.0f"


def table_for(mid, D, lang):
    m = METRICS[mid]
    df = D[m["table"]]
    if mid == "b1_fields":     # shown as field x period shares; the CSV keeps the long form
        w = df[df.source == "Woodcroft"].pivot_table(index="field", columns="period", values="share", aggfunc="first", sort=False)
        w = w.reindex([f for f in FL.FIELD_ORDER if f in w.index])
        w.insert(0, "field_name", [FL.LABEL[f][lang] for f in w.index])
        w = w.reset_index(drop=True)
        cols = [("field_name", "분야" if lang == "ko" else "field", None)] + [(c, c, ".0%") for c in w.columns if c != "field_name"]
        return table_html(w, cols, f"t_{mid}", lang)
    cols = [(c, c.replace("_", " "), col_spec(df, c)) for c in df.columns]
    return table_html(df, cols, f"t_{mid}", lang)


def md(s: str) -> str:
    """Minimal inline markdown for registry text: *italic* and `code`, after escaping."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", s)
    return re.sub(r"[*]([^*]+)[*]", lambda m: "<i>" + m.group(1) + "</i>", s)


def rel_card(mid, rel, lang):
    m = METRICS[mid]
    kind = m["rel"]
    r = rel.get(mid, {})
    rows = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in (r.get(lang) or {}).items())
    return f'<div class="spec rel"><h3><span class="badge">{kind}</span>{T[lang]["reliability"]}</h3><p class="src">{esc(T[lang]["rel"][kind])}</p>{"<dl>" + rows + "</dl>" if rows else ""}</div>'


def metric_page(mid, D, TK, rel, lang):
    m, t = METRICS[mid], T[lang]
    L = m[lang]
    kv = TK[mid]["kv"][lang]
    body = [f'<div class="eyebrow"><span class="tag layer">{m["series"]} · {esc(SERIES[m["series"]][lang])}</span></div>',
            f'<div class="mhero"><h1>{esc(L["name"])}</h1><div class="big">{esc(kv[0])}<small>{esc(kv[1])}</small></div></div>',
            take(TK[mid][lang], lang)]
    body.append(f'<div class="spec"><dl><dt>{t["definition"]}</dt><dd>{esc(L["definition"])}</dd><dt>{t["formula"]}</dt><dd class="formula">{esc(L["formula"])}</dd>'
                f'<dt>{t["reading"]}</dt><dd>{esc(L["reading"])}</dd><dt>{t["caveat"]}</dt><dd>{esc(L["caveat"])}</dd></dl></div>')
    body.append(figure(mid, D, lang))
    body.append(f'<h2>{t["table"]}</h2><p class="files"><a href="../../data/{m["table"]}.csv">{t["download"]} · {m["table"]}.csv</a></p>')
    body.append(table_for(mid, D, lang))
    body.append(rel_card(mid, rel, lang))
    if m.get("prior"):
        body.append(f'<h2>{t["prior"]}</h2><ul class="prose">' + "".join(f'<li>{md(PRIOR[p][lang])} <span class="src">— {md(PRIOR[p]["cite"])}</span></li>' for p in m["prior"]) + "</ul>")
    body.append(f'<h2>{t["source"]}</h2><ul class="prose">' + "".join(f'<li>{md(SOURCES[s][lang])} <span class="src">({esc(SOURCES[s]["license"])}, <a href="{SOURCES[s]["url"]}">{esc(SOURCES[s]["url"])}</a>)</span></li>' for s in m["sources"]) + "</ul>")
    body.append(f'<div class="links"><a href="index.html">← {t["metric_list"]}</a></div>')
    return page(lang, L["name"], "".join(body), depth=2, active="metrics", desc=TK[mid][lang])


def cards(D, TK, lang, ids=None, depth=1):
    pre = "metrics/" if depth == 1 else ""
    out = ['<div class="cards">']
    for mid, m in METRICS.items():
        if ids and mid not in ids:
            continue
        kv = TK[mid]["kv"][lang]
        out.append(f'<a class="card s-{ {"A": "A", "B": "B", "C": "C", "D": "D", "P": "E"}[m["series"]] }" href="{pre}{mid}.html"><b>{esc(m[lang]["name"])}</b>'
                   f'<span class="kv">{esc(kv[0])}<small>{esc(kv[1])}</small></span><small>{esc(m[lang]["definition"][:90])}…</small></a>')
    out.append("</div>")
    return "".join(out)


def metrics_index(D, TK, lang):
    t = T[lang]
    body = [f"<h1>{t['metric_list']}</h1><p class='lead'>{'지표 ' + str(len(METRICS)) + '개. 계열마다 묶었다.' if lang == 'ko' else str(len(METRICS)) + ' metrics, grouped by series.'}</p>"]
    for s, lab in SERIES.items():
        ids = [k for k, m in METRICS.items() if m["series"] == s]
        body.append(f"<h2>{s} · {esc(lab[lang])}</h2>" + cards(D, TK, lang, ids, depth=2))
    return page(lang, t["metric_list"], "".join(body), depth=2, active="metrics")


def home(D, TK, lang):
    t = T[lang]
    a1, p1 = D["m_a1_annual"], D["m_p1_sro_annual"]
    v1, a2 = D["m_v1_fulin_annual"], D["m_a2_periods"]
    nl = int(a2[a2.jurisdiction == "NL"]["count"].sum())
    stats = [(f"{int(a1.grants.sum(skipna=True)):,}", "잉글랜드 발명 허여 1561–1852" if lang == "ko" else "English invention grants 1561–1852", "metrics/a1_annual.html"),
             (f"{int(p1.entries.sum()):,}", "런던 출판업조합 등록 1557–1640" if lang == "ko" else "Stationers' Register entries 1557–1640", "metrics/p1_sro_annual.html"),
             (f"{int(v1.privileges.sum()):,}", "베네치아 출판 특권 문서 1469–1526" if lang == "ko" else "Venetian printing-privilege documents 1469–1526", "metrics/v1_venice_printing.html"),
             (f"{nl:,}", "네덜란드 발명 특권 문서 1581–1621" if lang == "ko" else "Dutch invention-privilege documents 1581–1621", "metrics/a2_periods.html")]
    lines = [TK[k][lang] for k in ("a3_1624", "d2_term_shift", "c1_foreign", "p3_sro_status", "v1_venice_printing")]
    hero = (f'<div class="hero"><div class="glyph">1624</div><h1>{t["site"]}</h1><p class="lead">{esc(t["tagline"])}</p></div>')
    nlp = int(a2[(a2.jurisdiction == "NL") & (a2.kind == "invention")]["count"].sum()) if "kind" in a2 else nl
    if lang == "ko":
        paras = [
            "근대 특허법과 저작권법이 생기기 전에는 새 기계를 혼자 만들거나 새 책을 혼자 찍을 권리를 법률이 정해 주지 않았다. "
            "베네치아 원로원, 잉글랜드 국왕, 네덜란드 연방의회가 청원한 사람에게 하나씩 내주었다. 이것이 특권이다. 허여는 문서로 남았고, "
            "19세기의 문서 정리자들이 그 문서를 목록으로 엮었다.",
            f"이 사이트는 그 목록을 한 건씩 센다. 잉글랜드는 Hulme이 정리한 1561–1603년 허여 55건, Woodcroft가 번호를 매긴 1617–1852년 14,359번, "
            f"런던 출판업조합 등록부의 1557–1640년 기재 {int(p1.entries.sum()):,}건이다. 베네치아는 Fulin이 모은 1469–1526년 출판 관련 문서 256건, "
            f"네덜란드는 Buning·Looijesteijn이 정리한 1581–1621년 특권 문서 {nlp:,}건이다. 베네치아 발명 특허는 직접 세지 못해 문헌의 수치를 2차 인용으로 싣는다.",
            "묻는 것은 넷이다. 해마다 몇 건이 나갔나, 어느 분야였나, 누가 받았나(외국인, 여럿이 함께 받은 경우), 몇 년 동안 어떤 조건으로 주어졌나. "
            "1624년 잉글랜드 독점법 앞뒤로 허여에 적힌 존속기간이 21년에서 14년으로 옮겨 가는 것이, 이렇게 세어 보아야 드러나는 변화의 한 예다.",
            "수치마다 단위와 원자료를 붙였다. 목록마다 세는 단위가 특허 번호, 허여, 등록 기재, 문서로 달라서 관할끼리 그대로 견줄 수 없다. "
            "지표 면마다 다른 사람이 쪽 이미지나 원문을 다시 읽어 맞춰 본 일치율(신뢰도 카드)과 한계를 함께 두었다. "
            "법이 무엇을 바꾸었는지는 말하지 않는다. 어느 해 앞뒤로 무엇이 관측되는지만 적는다.",
            f"처음이라면 아래 「핵심」 문장과 A 계열 지표부터 보면 된다. 나라별로는 <a href='places.html'>{t['nav_places']}</a>, "
            f"연표는 <a href='eras.html'>{t['nav_eras']}</a>, 수치 없이 흐름만 읽으려면 <a href='reading.html'>{t['nav_reading']}</a>을 연다. "
            f"세는 규칙은 <a href='method.html'>{t['nav_method']}</a>, 원자료와 코드는 <a href='data.html'>{t['nav_data']}</a>에 있다.",
        ]
    else:
        paras = [
            "Before modern patent and copyright law, no statute gave anyone the sole right to build a new machine or print a new book. "
            "The Venetian Senate, the English Crown and the Dutch States General granted that right one petitioner at a time; the grant was a privilege. "
            "The grants left documents, and nineteenth-century archivists bound them into lists.",
            f"This site counts those lists one grant at a time. For England: Hulme's 55 grants of 1561–1603, Woodcroft's numbers 1 to 14,359 for 1617–1852, "
            f"and {int(p1.entries.sum()):,} entries in the London Stationers' Register for 1557–1640. For Venice: the 256 printing documents of 1469–1526 collected by Fulin. "
            f"For the Dutch Republic: {nlp:,} privilege documents of 1581–1621 from the data of Buning and Looijesteijn. Venetian invention patents could not be counted here; "
            "figures from the literature are shown as secondary.",
            "Four questions run through the metrics: how many grants were made each year, in which trades, to whom (foreigners, grants shared by several people), "
            "and for how long and on what terms. One change these counts show is the term written in English grants moving from 21 years to 14 around the Statute of Monopolies of 1624.",
            "Every figure carries its unit and its source. The lists count in different units (patent numbers, grants, register entries, documents), so jurisdictions cannot be compared as they stand. "
            "Each metric page also has a reliability card, the agreement found when another reader went back to the page images or the original text, and its caveats. "
            "The site does not say what a law changed; it reports what is observed before and after a given year.",
            f"To start, read the key points below and the A metrics. By country, open <a href='places.html'>{t['nav_places']}</a>; for dates, "
            f"<a href='eras.html'>{t['nav_eras']}</a>; for a narrative without tables, the <a href='reading.html'>{t['nav_reading']}</a>. "
            f"The counting rules are under <a href='method.html'>{t['nav_method']}</a>, and the sources and code under <a href='data.html'>{t['nav_data']}</a>.",
        ]
    intro = "<div class='prose intro'>" + "".join(f"<p>{x}</p>" for x in paras) + "</div>"
    body = [hero, intro, '<div class="stats">' + "".join(f'<a class="stat" href="{h}"><div class="n">{n}</div><small>{esc(s)}</small></a>' for n, s, h in stats) + "</div>",
            f'<div class="take"><div class="l">{t["key"]}</div>' + "".join(f"<p>{esc(x)}</p>" for x in lines) + "</div>"]
    for s, lab in SERIES.items():
        ids = [k for k, m in METRICS.items() if m["series"] == s]
        body.append(f"<h2>{s} · {esc(lab[lang])}</h2>" + cards(D, TK, lang, ids, depth=1))
    return page(lang, t["site"], "".join(body), depth=1, active="home")


def places(D, TK, lang):
    ko = lang == "ko"
    t = T[lang]
    blocks = {
        "GB": (["a1_annual", "a3_1624", "b1_fields", "c1_foreign", "d1_terms", "d2_term_shift", "d3_clauses", "p1_sro_annual", "p3_sro_status"],
               "1561–1603년 Hulme 목록 55건, 1617–1852년 Woodcroft 목록 14,359번, 1557–1640년 출판업조합 등록 10,453건. 1604–1616년은 두 목록 사이의 공백이다." if ko else
               "Hulme's list of 55 grants for 1561–1603, Woodcroft's 14,359 numbers for 1617–1852 and 10,453 Stationers' Register entries for 1557–1640. 1604–1616 falls between the two lists."),
        "VE": (["a2_periods", "b3_venice_sectors", "v1_venice_printing", "d1_terms"],
               "발명 특허는 문헌 수치(2차 인용)만 싣는다. 이 사이트가 확인한 건별 원천은 Berveglieri 2020의 레게스토(2,130건)이고 아직 옮기지 않았다. 그보다 앞서 Mandich(1936·1948)가 1474–1550년 109건을 옮기고 분류했다(Comino 등 2017). 출판 특권은 Fulin 1882의 문서 256건을 코딩했다." if ko else
               "Invention patents are shown only as figures from the literature (secondary). The record-level source checked here is Berveglieri's 2020 calendar (2,130 grants), not yet transcribed; earlier, Mandich (1936, 1948) transcribed and classified 109 grants of 1474–1550 (Comino et al. 2017). Printing privileges: Fulin's 256 documents of 1882, coded here."),
        "NL": (["a2_periods", "c1_foreign", "d1_terms"],
               "Buning·Looijesteijn 자료(1581–1621, CC BY 4.0)를 다시 셌다. 문서 성격이 특권 허여인 것만 센다." if ko else
               "The Buning and Looijesteijn data (1581–1621, CC BY 4.0), recounted here; only documents that issue a privilege are counted."),
    }
    body = [f"<h1>{t['nav_places']}</h1>"]
    for j, (ids, txt) in blocks.items():
        body.append(f"<h2>{JUR[j][lang]}</h2><p class='prose'>{esc(txt)}</p>" + cards(D, TK, lang, ids, depth=1))
    return page(lang, t["nav_places"], "".join(body), depth=1, active="places")


def eras(D, TK, lang):
    ko = lang == "ko"
    ev = [(1469, "베네치아, 요한네스 데 스피라에게 5년 인쇄 특권(Fulin 1번)" if ko else "Venice: five-year printing privilege to Johannes de Spira (Fulin no. 1)"),
          (1474, "베네치아 원로원 발명 특허법(Parte, 3월 19일)" if ko else "Venetian Senate patent act (parte of 19 March)"),
          (1486, "베네치아, 사벨리코에게 저자 특권(Fulin 문서 가운데 저자에게 간 가장 이른 것, 3번)" if ko else "Venice: privilege to the author Sabellico (the earliest to an author among Fulin's documents, no. 3)"),
          (1517, "베네치아 원로원, 기존 출판 특권을 거두고 새 책에만 특권을 주기로 의결" if ko else "Venetian Senate revokes existing printing privileges and limits new ones to new books"),
          (1557, "런던 출판업조합 칙허, 등록부 기재 시작(SRO 1번 1557-07-19)" if ko else "Stationers' Company chartered; register entries begin (SRO no. 1, 1557-07-19)"),
          (1561, "잉글랜드, Hulme 목록 1번(흰 비누)" if ko else "England: Hulme's No. I (white soap)"),
          (1581, "네덜란드 Buning 자료 시작" if ko else "Dutch Republic: the Buning data begin"),
          (1617, "Woodcroft 목록 1번" if ko else "Woodcroft's No. 1"),
          (1624, "잉글랜드 독점법(21 Jac. I c. 3). 새 발명 특허를 14년 이하로" if ko else "Statute of Monopolies (21 Jac. I c. 3): patents for new inventions limited to 14 years or less"),
          (1637, "출판업조합 등록이 의무가 됨(SRO)" if ko else "Entrance in the Stationers' Register becomes compulsory (SRO)"),
          (1710, "앤 여왕법. 이 사이트의 출판 자료는 1640년에서 끝나 그 전후는 담지 못한다" if ko else "Statute of Anne; this site's printing data end in 1640 and cannot show the years around it"),
          (1852, "Woodcroft 목록 끝(10월 1일). 목록은 1852년 특허법(15 & 16 Vict. c. 83) 제32조에 따라 편찬되었다(표제면)" if ko else "Woodcroft's list ends (1 October); it was compiled under the Patent Law Amendment Act, 15 & 16 Vict. c. 83, s. 32 (title page)")]
    a1, p1, v1 = D["m_a1_annual"], D["m_p1_sro_annual"], D["m_v1_fulin_annual"]
    s = svg_lines([("GB" if not ko else "잉글랜드 발명", [(r.year, float(r.grants)) for r in a1[a1.year <= 1700].itertuples() if not pd.isna(r.grants)], 0),
                   ("VE" if not ko else "베네치아 출판", [(r.year, float(r.privileges)) for r in v1.itertuples()], 1)], ",.0f",
                  bands=[(1474, 1475, "1474"), (1517, 1518, "1517"), (1624, 1625, "1624")], xstep=25)
    body = [f"<h1>{T[lang]['nav_eras']}</h1>", fig(s, "연도별 수, 1469–1700. 음영은 1474·1517·1624년." if ko else "Counts per year, 1469–1700. Shaded: 1474, 1517, 1624."),
            "<div class='wrap'><table><thead><tr><th class='num'>" + T[lang]["year"] + "</th><th></th></tr></thead><tbody>" +
            "".join(f"<tr><td class='num'>{y}</td><td>{esc(x)}</td></tr>" for y, x in ev) + "</tbody></table></div>",
            "<p class='src'>" + ("연표의 연도·사건은 각 자료원(Fulin·Hulme·Woodcroft·SRO)과 법령 명칭에서 가져왔다." if ko else "Years and events are taken from the sources used (Fulin, Hulme, Woodcroft, SRO) and the titles of the statutes.") + "</p>"]
    return page(lang, T[lang]["nav_eras"], "".join(body), depth=1, active="eras")


def prior_page(lang):
    t = T[lang]
    body = [f"<h1>{t['nav_prior']}</h1><p class='lead'>{'선행 수치. 원문에서 확인한 것을 싣되, 원문을 보지 못하고 다른 문헌을 거쳐 옮긴 것은 「2차 인용」으로 표시했다. 이 사이트의 계수와 나란히 본다.' if lang == 'ko' else 'Prior figures, checked in the original publications except those marked as secondary citations, which are taken from another work. Read them next to this site’s counts.'}</p><ul class='prose'>"]
    for k, p in PRIOR.items():
        body.append(f"<li>{md(p[lang])} <span class='src'>— {md(p['cite'])}</span></li>")
    body.append("</ul>")
    return page(lang, t["nav_prior"], "".join(body), depth=1, active="prior")


DATA_FILES = [("woodcroft_entries.csv.gz", "CC BY 4.0", "woodcroft"), ("hulme_1561_1603.csv", "CC BY 4.0", "hulme"), ("fulin_coding.csv", "CC BY 4.0", "fulin"),
              ("sro/sro_entries.csv.gz", "CC BY-SA 4.0", "sro"), ("sro/sro_site_decade_counts.csv", "CC BY-SA 4.0", "sro")]


def data_page(D, lang):
    ko = lang == "ko"
    t = T[lang]
    rows = [f"<tr><td><a href='../data/{f}'>{f}</a></td><td>{lic}</td><td>{esc(SOURCES[s]['license'])}</td></tr>" for f, lic, s in DATA_FILES]
    rows += [f"<tr><td><a href='../data/{k}.csv'>{k}.csv</a></td><td>CC BY 4.0</td><td>—</td></tr>" for k in sorted(D)]
    body = [f"<h1>{t['nav_data']}</h1>",
            "<p class='prose'>" + ("레코드 표와 지표 표를 CSV로 낸다. 각 파일의 라이선스와 원자료 라이선스는 data/datapackage.json 에도 적었다. 출판업조합 등록 표는 원자료 조건에 따라 CC BY-SA 4.0으로 별도 폴더(data/sro/)에 둔다. 네덜란드 원자료는 다시 배포하지 않고 DOI로만 잇는다." if ko else
                                   "Record tables and metric tables are published as CSV. Each file's license and its source license are also listed in data/datapackage.json. The Stationers' Register table is CC BY-SA 4.0, as its source requires, and sits in its own folder (data/sro/). The Dutch source data are not redistributed; they are linked by DOI.") + "</p>",
            "<div class='wrap'><table><thead><tr><th>file</th><th>" + t["license"] + "</th><th>source</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>",
            "<p class='files'><a href='../data/datapackage.json'>datapackage.json</a> <a href='../data/reliability.json'>reliability.json</a></p>"]
    return page(lang, t["nav_data"], "".join(body), depth=1, active="data")


def method_page(rel, lang):
    ko = lang == "ko"
    t = T[lang]
    secs = METHOD[lang]
    body = [f"<h1>{t['nav_method']}</h1><div class='prose'>"]
    for h, ps in secs:
        body.append(f"<h2>{esc(h)}</h2>" + "".join(f"<p>{esc(p)}</p>" for p in ps))
    body.append("</div>")
    return page(lang, t["nav_method"], "".join(body), depth=1, active="method")


METHOD = {"ko": [], "en": []}     # filled from method_text.py
READING = {"ko": [], "en": []}


def reading_page(lang):
    t = T[lang]
    body = [f"<h1>{t['nav_reading']}</h1><div class='prose'>"]
    for h, ps in READING[lang]:
        body.append(f"<h2>{esc(h)}</h2>" + "".join(f"<p>{esc(p)}</p>" for p in ps))
    body.append("</div>")
    return page(lang, t["nav_reading"], "".join(body), depth=1, active="reading")


def write_data(D):
    dd = OUT / "data"
    (dd / "sro").mkdir(parents=True, exist_ok=True)
    for k, df in D.items():
        df.to_csv(dd / f"{k}.csv", index=False, encoding="utf-8")
    W = pd.read_csv(DER / "woodcroft_entries.csv")
    with gzip.open(dd / "woodcroft_entries.csv.gz", "wt", encoding="utf-8", newline="") as f:
        W.to_csv(f, index=False)
    shutil.copy(COD / "hulme_1561_1603.csv", dd / "hulme_1561_1603.csv")
    shutil.copy(COD / "fulin_coding.csv", dd / "fulin_coding.csv")
    S = pd.read_csv(DER / "sro_entries.csv")
    with gzip.open(dd / "sro" / "sro_entries.csv.gz", "wt", encoding="utf-8", newline="") as f:
        S.to_csv(f, index=False)
    shutil.copy(DER / "sro_site_decade_counts.csv", dd / "sro" / "sro_site_decade_counts.csv")
    if (DER / "reliability.json").exists():
        shutil.copy(DER / "reliability.json", dd / "reliability.json")
    res = []
    for f, lic, s in DATA_FILES:
        res.append({"path": f, "license": lic, "source": SOURCES[s]["en"], "source_license": SOURCES[s]["license"], "source_url": SOURCES[s]["url"]})
    for k in sorted(D):
        res.append({"path": f"{k}.csv", "license": "CC BY 4.0", "derived_from": [SOURCES[s]["url"] for s in next((m["sources"] for m in METRICS.values() if m["table"] == k), [])]})
    (dd / "datapackage.json").write_text(json.dumps({"name": "privilege-metrics", "title": SITE["en"]["title"], "version": VERSION, "created": BUILD_DATE,
                                                     "licenses": [{"name": "CC-BY-4.0"}, {"name": "CC-BY-SA-4.0", "note": "data/sro/ only"}],
                                                     "resources": res}, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    import method_text
    m_, r_ = method_text.build()
    METHOD.update(m_)
    READING.update(r_)
    D, rel = load()
    TK = takeaways.build(D)
    if OUT.exists():
        shutil.rmtree(OUT)
    for lang in ("ko", "en"):
        (OUT / lang / "metrics").mkdir(parents=True, exist_ok=True)
        (OUT / lang / "index.html").write_text(home(D, TK, lang), encoding="utf-8")
        (OUT / lang / "metrics" / "index.html").write_text(metrics_index(D, TK, lang), encoding="utf-8")
        for mid in METRICS:
            (OUT / lang / "metrics" / f"{mid}.html").write_text(metric_page(mid, D, TK, rel, lang), encoding="utf-8")
        (OUT / lang / "places.html").write_text(places(D, TK, lang), encoding="utf-8")
        (OUT / lang / "eras.html").write_text(eras(D, TK, lang), encoding="utf-8")
        (OUT / lang / "prior.html").write_text(prior_page(lang), encoding="utf-8")
        (OUT / lang / "data.html").write_text(data_page(D, lang), encoding="utf-8")
        (OUT / lang / "method.html").write_text(method_page(rel, lang), encoding="utf-8")
        (OUT / lang / "reading.html").write_text(reading_page(lang), encoding="utf-8")
    (OUT / "index.html").write_text('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                                    '<meta http-equiv="refresh" content="0; url=ko/index.html"><title>From Privilege to Patent</title></head><body>'
                                    '<p><a href="ko/index.html">한국어</a> · <a href="en/index.html">English</a></p></body></html>', encoding="utf-8")
    write_data(D)
    n = sum(1 for _ in OUT.rglob("*.html"))
    print("pages", n, "files", sum(1 for _ in OUT.rglob("*") if _.is_file()))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
