# -*- coding: utf-8 -*-
"""Build the static site (ko/en) into docs/ (site/ in the build layout; see paths.py).

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
import fig_notes as FN  # noqa: E402
from registry import METRICS, PRIOR, SERIES, SITE, SOURCES  # noqa: E402
from site_kit import CSS, JS, esc, fig, fig_n, fmt, legend, svg_bars, svg_lines, table_html, cap, col_label  # noqa: E402
from paths import COD, DER, OUT, find, need  # noqa: E402

VERSION = SITE["version"]
BUILD_DATE = "2026-11-24"
REPO = "https://github.com/BowonKwon/Privilege-Metrics"

T = {
    "ko": dict(site=SITE["ko"]["title"], tagline=SITE["ko"]["subtitle"], nav_home="홈", nav_metrics="지표", nav_places="관할", nav_eras="연대",
               nav_prior="선행 결과", nav_reading="읽기용 판", nav_data="데이터", nav_method="방법·한계", lang_other="English",
               definition="정의", formula="공식", reading="읽는 법", caveat="한계", source="자료원", unit="단위", key="핵심",
               reliability="신뢰도 카드", table="표", download="CSV 내려받기", metric_list="지표 목록", license="라이선스", built="생성일", version="판",
               hub="공개 자료 전체", prior="선행 결과", series="계열", year="연도", decade="10년", period="구간", share="비율", n="건수", file="파일", theme="화면 테마",
               rel={"exact": "집계값 — 구조화된 원자료에서 그대로 셌거나, 쪽 이미지와 대조해 손으로 옮긴 값", "ocr": "OCR 계수 — 스캔 OCR에서 규칙으로 센 값. 아래는 쪽 이미지 표본으로 잰 오류",
                    "sampled": "규칙 분류 — 단어 규칙으로 나눈 값. 아래는 독립 코딩 표본으로 잰 정밀도", "secondary": "2차 인용 — 문헌 수치를 옮긴 값. 이 사이트가 다시 세지 않았다"},
               badge={"exact": "집계값", "ocr": "OCR 계수", "sampled": "규칙 분류", "secondary": "2차 인용"}),
    "en": dict(site=SITE["en"]["title"], tagline=SITE["en"]["subtitle"], nav_home="Home", nav_metrics="Metrics", nav_places="Jurisdictions", nav_eras="Timeline",
               nav_prior="Prior results", nav_reading="Reading edition", nav_data="Data", nav_method="Method and limits", lang_other="한국어",
               definition="Definition", formula="Formula", reading="How to read it", caveat="Caveats", source="Sources", unit="Unit", key="Key point",
               reliability="Reliability card", table="Table", download="Download CSV", metric_list="All metrics", license="License", built="Built", version="Version",
               hub="All public materials", prior="Prior results", series="Series", year="Year", decade="Decade", period="Period", share="Share", n="Count", file="File", theme="Theme",
               rel={"exact": "Exact count: counted straight from a structured source, or transcribed by hand and checked against the page images", "ocr": "OCR count: counted by rule from scanned OCR text; below, the error measured on a sample checked against page images",
                    "sampled": "Rule-based classification: assigned by word rules; below, the precision measured on an independently coded sample", "secondary": "Secondary figure: quoted from the literature and not recounted here"},
               badge={"exact": "exact", "ocr": "ocr", "sampled": "sampled", "secondary": "secondary"}),
}
JUR = {"GB": {"ko": "잉글랜드", "en": "England"}, "VE": {"ko": "베네치아", "en": "Venice"}, "NL": {"ko": "네덜란드", "en": "Dutch Republic"}}

# 1.0.3: navigation on leaf pages (breadcrumb, same-series list, previous/next)
LEAF_CSS = (' main.wide{max-width:1300px} .crumbs{font-size:.84rem;color:var(--fg3);margin:-.4rem 0 .9rem} .crumbs .sep{margin:0 .25rem}'
            ' .crumbs [aria-current]{color:var(--fg2)} .leaf{display:grid;grid-template-columns:230px minmax(0,1fr);gap:2rem;align-items:start}'
            ' .leafbody{min-width:0} .sibs{position:sticky;top:4.2rem;max-height:calc(100vh - 5rem);overflow:auto;font-size:.84rem;border-right:1px solid var(--line);padding-right:.8rem}'
            ' .sibs ol,.sibs-m ol{list-style:none;margin:.2rem 0 .8rem;padding:0} .sibs li a,.sibs-m li a{display:block;padding:.18rem .4rem;border-radius:6px;color:var(--fg2)}'
            ' .sibs li a:hover,.sibs-m li a:hover{background:var(--bg2);text-decoration:none} .sibs a[aria-current],.sibs-m a[aria-current]{background:var(--bg2);color:var(--fg);font-weight:600}'
            ' .sibs summary,.sibs-m summary{cursor:pointer;font-weight:600;color:var(--fg);margin:.3rem 0} .sibs-m{display:none;border:1px solid var(--line);border-radius:10px;padding:.4rem .8rem;margin:0 0 1rem;font-size:.9rem}'
            ' .pn{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;border-top:1px solid var(--line);margin-top:2.4rem;padding-top:1rem;font-size:.92rem}'
            ' .pn a{overflow-wrap:anywhere} .pn a[rel=next]{margin-left:auto;text-align:right} .pn small{display:block;color:var(--fg3)}'
            ' @media(max-width:860px){.leaf{display:block}.sibs{display:none}.sibs-m{display:block}} @media print{.crumbs,.sibs,.sibs-m,.pn{display:none}.leaf{display:block}}')
LEAF_JS = (';document.addEventListener("keydown",function(e){if(e.altKey||e.ctrlKey||e.metaKey||e.shiftKey)return;var t=e.target;'
           'if(t&&t.closest&&t.closest("input,textarea,select,[contenteditable]"))return;var a=null;if(e.key==="ArrowLeft")a=document.querySelector("a[rel=prev]");'
           'else if(e.key==="ArrowRight")a=document.querySelector("a[rel=next]");if(a){location.href=a.href}});'
           'var sb=document.querySelector(".sibs"),cu=sb&&sb.querySelector("a[aria-current]");if(cu){sb.scrollTop=cu.offsetTop-sb.clientHeight/2}')
LEAF_T = {"ko": dict(crumbs="위치", sibs="같은 계열의 지표", others="다른 지표", pn="이전·다음 지표", next_group="다음 계열"),
          "en": dict(crumbs="Breadcrumb", sibs="Metrics in this series", others="Other metrics", pn="Previous and next metric", next_group="Next series")}


def metric_siblings(lang, mid):
    """Breadcrumb and sibling groups for a metric page, computed from the registry in the order of the metric list page
    (series by series), so a new metric appears without editing any link list."""
    t = T[lang]
    groups = [(s, f"{s} · {SERIES[s][lang]}", [(m[lang]["name"], f"{k}.html") for k, m in METRICS.items() if m["series"] == s]) for s in SERIES]
    return dict(crumbs=[(t["nav_home"], "../index.html"), (t["nav_metrics"], "index.html")], cur=f"{mid}.html",
                groups=[(lab, items) for _, lab, items in groups if items], anchors=[f"index.html#s-{k}" for k, _, items in groups if items])


def leaf_html(lang, leaf, body):
    """Breadcrumb, same-series list (sidebar on wide screens, folded box on narrow ones) and previous/next links.
    leaf = dict(crumbs=[(label, href)...], groups=[(group label, [(label, href), ...]), ...], cur=href of this page,
    anchors=[href of each group's heading]). At the end of a series 'next' continues with the next series and says so."""
    L = LEAF_T[lang]
    flat = [(lab, href, gi, glab) for gi, (glab, items) in enumerate(leaf["groups"]) for lab, href in items]
    idx = next(i for i, x in enumerate(flat) if x[1] == leaf["cur"])
    cur_g = flat[idx][2]
    sep = " <span class='sep' aria-hidden='true'>›</span> "
    crumbs = sep.join(f'<a href="{h}">{esc(l)}</a>' for l, h in leaf["crumbs"])
    if leaf.get("anchors"):
        crumbs += f'{sep}<a href="{leaf["anchors"][cur_g]}">{esc(leaf["groups"][cur_g][0])}</a>'
    crumbs += f"{sep}<span aria-current='page'>{esc(flat[idx][0])}</span>"

    def lists():
        out = []
        for gi, (glab, items) in enumerate(leaf["groups"]):
            lis = "".join(f'<li><a href="{h}"' + (' aria-current="page"' if h == leaf["cur"] else "") + f'>{esc(l)}</a></li>' for l, h in items)
            out.append(f'<details{" open" if gi == cur_g else ""}><summary>{esc(glab)} <small>({len(items)})</small></summary><ol>{lis}</ol></details>')
        return "".join(out)

    side = f'<aside class="sibs"><nav aria-label="{L["sibs"]}">{lists()}</nav></aside>'
    mobile = (f'<details class="sibs-m"><summary>{L["others"]} ({len(flat)})</summary>'
              f'<nav aria-label="{L["sibs"]}">{lists()}</nav></details>')
    pn = []
    if idx > 0:
        pv = flat[idx - 1]
        pn.append(f'<a rel="prev" href="{pv[1]}">← {esc(pv[0])}</a>')
    if idx + 1 < len(flat):
        nx = flat[idx + 1]
        note = f'<small>{L["next_group"]}: {esc(nx[3])}</small> ' if nx[2] != cur_g else ""
        pn.append(f'<a rel="next" href="{nx[1]}">{note}{esc(nx[0])} →</a>')
    pnav = f'<nav class="pn" aria-label="{L["pn"]}">{"".join(pn)}</nav>'
    return (f'<nav class="crumbs" aria-label="{L["crumbs"]}">{crumbs}</nav><div class="leaf">{side}<div class="leafbody">{mobile}'
            f'{body}{pnav}</div></div>')


_WIDE_SVG = re.compile(r"""<svg\b[^>]*\bviewBox=(["'])0 0 (\d+)(?:\.\d+)? [^"']*\1[^>]*>.*?</svg>""", re.S)


def wrap_wide_svgs(body: str) -> str:
    """Put every chart at least 500 units wide in a <div class="sx"> that carries its width (1.1). On a narrow screen the
    stylesheet lets that box scroll sideways and draws the chart at its own size, so chart text keeps the size it was laid
    out for instead of shrinking to 4px. On wider screens the box changes nothing."""
    def one(m):
        w = int(m.group(2))
        return f'<div class="sx" style="--vw:{w}">{m.group(0)}</div>' if w >= 500 else m.group(0)
    return _WIDE_SVG.sub(one, body)


import site_nav  # 1.1.2: section ids, a section list on pages with three or more sections, a button back to it
METHOD_IDS = ["counted", "woodcroft", "fields", "reliability", "prior-checks", "not-done", "versions"]
READING_IDS = ["counting", "around-1624", "recipients", "printing", "using"]


def page(lang, title, body, depth=1, active="", desc="", rel="index.html", leaf=None, toc=True):
    """rel: this page's path under the language folder; the language switch points to the same path in the other tree.
    leaf: sibling navigation for a leaf page (metric_siblings), drawn by leaf_html."""
    t = T[lang]
    # 1.1.2: every section heading gets a link to itself; pages with three or more sections get a section list
    # (toc=False where the page already has its own list: metric pages beside the series list, the jurisdictions page).
    body, _items = site_nav.anchor_html(body, lang, rel)
    if toc:
        body = site_nav.with_toc(body, site_nav.page_toc(lang, _items), lang)
    if leaf:
        body = leaf_html(lang, leaf, body)
    body = wrap_wide_svgs(body)
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
td.num,th.num{{white-space:nowrap}}{LEAF_CSS if leaf else ""}{site_nav.NAV_CSS}</style></head><body>
<header><a class="brand" href="{root}{lang}/index.html">{t['site']}</a>
<nav>{navh}</nav>
<div class="right"><a class="hub" href="https://bowonkwon.github.io/{'' if lang == 'ko' else 'en/'}">{'공개 자료 허브' if lang == 'ko' else 'All public materials'}</a><button id="theme" class="theme" type="button" aria-label="{t['theme']}">◑</button><a class="lang" href="{root}{other}/{rel}" hreflang="{other}">{t['lang_other']}</a></div></header>
<main{' class="wide"' if leaf else ""}>{body}</main>
<footer>{t['site']} · {t['version']} {VERSION} · {t['built']} {BUILD_DATE} · <a href="{REPO}">GitHub</a> · {t['hub']} <a href="https://bowonkwon.github.io/{hub}">bowonkwon.github.io</a><br>{attribution}</footer>
<script>{JS}{LEAF_JS if leaf else ""}{site_nav.NAV_JS}</script></body></html>"""


def take(text, lang):
    return f'<div class="take"><div class="l">{T[lang]["key"]}</div><p>{esc(text)}</p></div>'


def load():
    D = {p.stem: pd.read_csv(p) for p in DER.glob("m_*.csv")}
    missing = sorted({m["table"] for m in METRICS.values()} - set(D))
    if missing:
        raise FileNotFoundError(f"metric tables missing in {DER}: {missing} (run metrics.py)")
    rel = json.loads(need(DER / "reliability.json").read_text(encoding="utf-8"))
    return D, rel


# ------------------------------------------------------------------ figures per metric
YEAR = ("연도", "year")
DEC = ("10년 구간의 첫 해", "first year of the decade")
LINE_AX = {
    "a1_annual": [("허여 수(건/년)", "grants per year") + YEAR] * 2,
    "a4_extensions": [("연장 항목 수(10년 합)", "extension entries per decade") + DEC],
    "b1_fields": [("허여 가운데 그 분야의 비율", "share of grants in the field", "구간", "period")],
    "b2_hhi": [("분야 집중도 HHI(클수록 몇 분야에 몰림)", "field concentration, HHI (higher = more concentrated)") + DEC,
               ("허여 가운데 「기타」의 비율", "share of grants classed as 'other'") + DEC],
    "c1_foreign": [("허여 가운데 비율", "share of grants") + DEC], "c2_cogrant": [("허여 가운데 공동 허여의 비율", "share of grants made to more than one person") + DEC],
    "d2_term_shift": [("허여 수(건/년)", "grants per year") + YEAR], "d3_clauses": [("항목 가운데 그 조항을 언급한 비율", "share of entries mentioning the clause") + DEC],
    "p1_sro_annual": [("등록 항목 수(건/년)", "register entries per year") + YEAR], "p2_sro_concentration": [("그해 등록 가운데 상위 5인의 몫", "share of the year's entries held by the top five") + YEAR],
    "p3_sro_status": [("등록 항목 가운데 비율", "share of register entries") + DEC],
    "p4_sro_fees": [("수수료가 적힌 항목 가운데 6펜스의 비율", "share of sixpence fees among entries with a fee") + YEAR],
    "v1_venice_printing": [("출판 특권 문서 수(5년 합)", "printing privileges per five years", "5년 구간의 첫 해", "first year of the five-year period")],
}
BAR_X = {"a2_periods": ("건수(관할마다 세는 단위가 다르다)", "count (the unit differs by jurisdiction)"), "a3_1624": ("연평균 허여 수(건/년)", "mean grants per year"),
         "b3_venice_sectors": ("특허 수(건)", "patents"), "d1_terms": ("존속기간(년)", "term (years)")}
# 1.1: Korean names for the sectors of the Venetian table; the source's English name stays beside each
SECTOR_KO = {"Mills — cereals": "방아(곡물)", "Mills — metals": "가공 기계(금속)", "Mills — textiles": "가공 기계(직물)", "Mills — wood saws": "제재기(톱)", "Mills — multiple usage": "가공 기계(여러 용도)",
             "Fabrics": "직물", "Paint": "도료", "Bread and food": "빵·식품", "Pottery and Porcelain Vases": "도기·자기", "Agricultural machines": "농기계",
             "Drainage, mud removal": "배수·준설", "Hydraulic pumps": "양수 펌프", "Armour and weapons": "갑옷·무기", "Arsenal": "아르세날레(조선소)", "Mining": "광업",
             "Perpetual Motion": "영구 기관", "Miscellaneous": "기타"}
LIST_KO = {"Hulme": "Hulme 목록", "Woodcroft": "Woodcroft 목록", "Buning": "Buning 자료", "Fulin": "Fulin 문서"}
LIST_EN = {"Hulme": "Hulme's list", "Woodcroft": "Woodcroft's list", "Buning": "the Buning data", "Fulin": "Fulin's documents"}
GLOSS = {
    "ko": ("낱말: 허여(許與)는 특권이나 특허를 내려 주는 일이다. Hulme과 Woodcroft는 잉글랜드의 독점 허여·특허를 목록으로 엮은 사람이고(각각 1561–1603년, 1617–1852년), "
           "Fulin은 베네치아 인쇄 관련 문서(1469–1526년)를, Buning은 네덜란드 특허(1581–1621년) 자료를 엮었다. SRO는 런던 출판업조합의 등록부를 옮긴 Stationers' Register Online이다. 이 면에서 쓴 자료의 서지는 아래 「자료원」에, 다섯 자료 모두의 서지는 방법 면에 있다."),
    "en": ("Names: Hulme and Woodcroft compiled lists of English monopoly grants and patents (1561–1603 and 1617–1852); Fulin edited documents on Venetian printing (1469–1526); "
           "Buning's data cover Dutch patents (1581–1621); SRO is Stationers' Register Online, a transcription of the register of the London Stationers' Company. References for the sources used on this page are under Sources below; those for all five are on the method page."),
}
# 1.1.1: how English statutes are cited (regnal year and chapter), for the pages that cite one
STATUTE_GLOSS = {
    "ko": "법령 인용: 1963년 이전의 잉글랜드·영국 의회 법률은 회기가 열린 국왕의 재위 연도와, 그 회기에 통과한 법률들에 차례로 붙인 장(chapter) 번호로 부른다. 21 Jac. I c. 3은 제임스 1세(라틴어 이름 Jacobus) 재위 21년 회기 잉글랜드 의회의 제3장이고, 15 & 16 Vict. c. 83은 빅토리아 여왕 재위 15년과 16년에 걸친 회기 영국 의회의 제83장이다. s. 32는 그 법의 제32조(section 32)다.",
    "en": "Statute citations: Acts of the English and, later, British Parliament passed before 1963 are cited by the regnal year of the session and the chapter number given to each Act passed in that session. 21 Jac. I c. 3 is chapter 3 of the session of the 21st year of James I (Jacobus), an Act of the English Parliament; 15 & 16 Vict. c. 83 is chapter 83 of the session spanning the 15th and 16th years of Victoria, an Act of the Parliament of the United Kingdom; s. 32 is section 32 of that Act.",
}
_SAMPLE_RE = re.compile(r"\bR2[a-z]?(?:-chg)?\b")
_DICT_RE = re.compile(r"\br[0-9]\b")
_FIELD_KEY_RE = re.compile(r"(?<![A-Za-z_])(" + "|".join(sorted((re.escape(k) for k in FL.LABEL), key=len, reverse=True)) + r")(?= [0-9]+/[0-9]+)")


def rel_gloss(text: str, lang: str) -> str:
    """1.1.1: plain-language notes for the words that the reliability card actually uses."""
    ko = lang == "ko"
    out = []
    frac = re.search(r"([0-9]+)/([0-9]+)", text)
    if frac:
        k, n = frac.groups()
        out.append(f"「{k}/{n}」처럼 적힌 수는 견주어 본 {n}항목 가운데 두 값이 같았던 {k}항목이다. 무엇과 무엇을 견주었는지는 줄 이름에 있다. 「이미지 대조」「전사」「재코딩」「분야 일치」 줄은 이 사이트의 값과 다른 사람이 쪽 이미지나 본문을 다시 읽거나 분류를 다시 매긴 값이다." if ko
                   else f"A figure such as {k}/{n} means that two values agree on {k} of the {n} entries checked. What is compared with what is in the row name: the rows on image checks, transcription, recoding and field agreement compare the site's value with the value another reader found or assigned from the page image or the text.")
        if "chg" in text:
            out.append("다만 「같은 항목의 사전 r6」 줄은 앞 판 사전(r6)이 매긴 분야와 코더를, 「앞 판의 측정」 줄은 앞 판 사전(r6)과 그 판의 표본(R2d)을 코딩한 코더를, 「코더 간 일치」 줄은 두 코더끼리를 견준 수다. 「r7만 맞음」「r6만 맞음」은 두 코더가 같은 답을 낸 항목 가운데 한쪽 사전만 그 답과 같았던 수이고, 「둘 다 틀림」은 어느 사전도 그 답과 같지 않았던 수다." if ko
                       else "But the row on dictionary r6 compares the field given by the previous dictionary (r6) with the coder; the row on the previous measurement compares r6 with the coders of its own sample (R2d); the row on agreement between coders compares the two coders with each other; 'only r7 right' and 'only r6 right' count, among the entries on which both coders gave the same answer, those where only one dictionary matched that answer, and 'both wrong' those where neither did.")
    if "CI" in text:
        out.append("95% CI(95% 신뢰구간, 윌슨 방식)는 표본의 일치율로 전체의 실제 일치율을 어림한 범위다. 같은 방법으로 표본을 거듭 뽑아 이런 구간을 만들면 대략 100번에 95번꼴로 실제 값을 담는다. 다른 조건이 비슷하면 표본이 작을수록 넓다." if ko
                   else "95% CI (95% confidence interval, Wilson method) is a range for the true rate of agreement estimated from the sample: intervals made this way from repeated samples would contain the true value about 95 times in 100. Other things being similar, the smaller the sample, the wider it is.")
    if "κ" in text:
        out.append("κ(코헨 카파)는 두 판단이 우연히 같아질 몫을 뺀 일치도다. 1이면 완전히 같고, 0이면 우연히 맞는 정도다." if ko
                   else "κ (Cohen's kappa) is agreement with the part expected by chance removed: 1 is complete agreement, 0 is no better than chance.")
    if "가중" in text or "weighted" in text:
        out.append("표본은 분야마다 정한 수(일반 분야 11항목, 「기타」 25항목)를 뽑은 것이라 실제 허여의 분야 구성과 다르다. 그래서 분야별 일치율에 실제 허여의 분야 비중(「기타」 포함)을 곱해 더한 값을 「가중한 정밀도」로 함께 적는다. 이 카드의 95% CI는 가중하지 않은 표본 일치율(예: 163/212)에 붙인 근사 구간이고, 가중한 정밀도의 신뢰구간은 아니다." if ko
                   else "The sample takes a set number per field (11 per field, 25 for 'other'), so its mix differs from that of the grants; the weighted precision therefore multiplies each field's agreement by that field's share of the grants ('other' included) and adds them up. The 95% CI on this card is an approximate interval for the unweighted share in the sample (for example 163/212), not a confidence interval for the weighted precision.")
    samples = sorted(set(_SAMPLE_RE.findall(text)))
    dicts = sorted(set(_DICT_RE.findall(text)))
    if samples or dicts:
        parts = []
        if samples:
            strat = [x for x in samples if not x.endswith("-chg")]
            chg = [x for x in samples if x.endswith("-chg")]
            ko_s = f"표본 이름({'·'.join(samples)}) — 검증하려고 뽑은 항목 묶음이다." + (f" 이 카드의 {'·'.join(strat)}는 허여를 분야별로 나눈 뒤 분야마다 무작위로 뽑은 묶음(층화 표본)이다." if strat else "") + (f" {'·'.join(chg)}는 사전을 바꿀 때 분야가 바뀐 허여 가운데서 단순 무작위로 뽑은 묶음이다." if chg else "")
            en_s = f"Sample names ({', '.join(samples)}): sets of entries drawn for checking." + (f" On this card, {' and '.join(strat)} {'is a stratified sample' if len(strat) == 1 else 'are stratified samples'}, the grants divided by field and drawn at random within each field." if strat else "") + (f" {', '.join(chg)} {'is a simple random sample' if len(chg) == 1 else 'are simple random samples'} from the grants whose field changed with the new dictionary." if chg else "")
            parts.append(ko_s if ko else en_s)
        if dicts:
            parts.append((f"사전 이름({'·'.join(dicts)}) — 분야를 가르는 단어 규칙(분야 사전)의 판 번호다." if ko
                          else f"Dictionary names ({', '.join(dicts)}): versions of the word rules that assign fields (the field dictionary)."))
        out.append(" ".join(parts) + (" 경위는 방법 면에 있다." if ko else " The method page gives the history."))
    if "전사" in text or "transcription" in text:
        out.append("전사는 문서를 읽어 그대로 옮겨 적은 것이다." if ko else "Transcription is reading a document and copying it out.")
    if "재코딩" in text or "recod" in text:
        out.append("재코딩은 다른 사람이 같은 항목을 다시 읽고 분류를 다시 매긴 것이다." if ko else "Recoding is another person reading the same entry and assigning its categories again.")
    if "communication" in text:
        out.append("communication은 목록 본문에 해외에서 전해진 발명이라고 적힌 허여다." if ko
                   else "'Communication' marks a grant whose text says the invention was communicated from abroad.")
    return " ".join(out)


N_FIELDS = len([f for f in FL.LABEL if f != "other"])   # 17


_REL = {}
_REL_REC = {}     # record tables the chart notes count from (Woodcroft entries, Fulin coding)


def fig_notes(svg, key, D, lang):
    """1.1.4: a chart with its one-line introduction and its notes; every number in them is computed in fig_notes.py."""
    if not svg:
        return ""
    if not _REL:
        _REL.update(json.loads(need(DER / "reliability.json").read_text(encoding="utf-8")))
    if "W" not in _REL_REC:
        _REL_REC["W"] = pd.read_csv(find(DER, "woodcroft_entries.csv"), low_memory=False)
        _REL_REC["Fc"] = pd.read_csv(need(COD / "fulin_coding.csv"), dtype=str)
    ctx = dict(FL=FL, N_FIELDS=N_FIELDS, source_label=source_label, JUR=JUR, SECTOR=SECTOR_KO, rel=_REL, METRICS=METRICS, W=_REL_REC["W"], Fc=_REL_REC["Fc"])
    intro, parts = FN.checked(key, D, lang, ctx)
    return fig_n(svg, intro, parts, lang)


def source_label(src: str, lang: str) -> str:
    """'GB Woodcroft 1625-1700' -> 'England · Woodcroft's list 1625–1700' (1.1)."""
    parts = src.split(" ", 2)
    if len(parts) < 3 or parts[0] not in JUR:
        return src
    rest = parts[2].replace("-", "–")
    if lang == "ko":
        rest = rest.replace(" (printing)", "(출판)")
    return f"{JUR[parts[0]][lang]} · {(LIST_KO if lang == 'ko' else LIST_EN).get(parts[1], parts[1])} {rest}"


def figure(mid, D, lang):
    ko = lang == "ko"
    N = lambda en, k: k if ko else cap(en, "en")      # series / band name per language, sentence case in English
    from site_kit import svg_lines as svg_lines_, svg_bars as svg_bars_
    ax = iter(LINE_AX.get(mid, []))
    F = lambda svg, key: fig_notes(svg, key, D, lang)   # 1.1.4: intro line above, plain-language notes below (fig_notes.py)

    def svg_lines(*a, **k):   # 1.1: every line chart names both axes
        y_ko, y_en, x_ko, x_en = next(ax, ("", "", "", ""))
        return svg_lines_(*a, lang=lang, ylabel=(y_ko if ko else y_en), xlabel=(x_ko if ko else x_en), **k)

    def svg_bars(*a, **k):
        if mid in BAR_X and "xlabel" not in k:
            k["xlabel"] = BAR_X[mid][0 if ko else 1]
        return svg_bars_(*a, lang=lang, **k)
    if mid == "a1_annual":
        a = D["m_a1_annual"]
        e = a[(a.year <= 1700)]
        l = a[(a.year >= 1700)]
        s1 = svg_lines([(N("grants", "허여"), [(r.year, float(r.grants) if not pd.isna(r.grants) else math.nan) for r in e.itertuples()], 0)], ",.0f",
                       bands=[(1604, 1616, N("gap", "목록 공백")), (1624, 1625, "1624")], xstep=20)
        s2 = svg_lines([(N("grants", "허여"), [(r.year, float(r.grants)) for r in l.itertuples()], 0)], ",.0f", xstep=20)
        return F(s1, "a1_e") + F(s2, "a1_l")
    if mid == "a2_periods":
        a = D["m_a2_periods"]
        items = [(f"{JUR[r.jurisdiction][lang]} · {('발명' if r.kind == 'invention' else '출판') if ko else r.kind} · {r.period}{' *' if r.basis == 'secondary' else ''}", float(r['count']), {"GB": 0, "VE": 1, "NL": 2}[r.jurisdiction])
                 for _, r in a[a["period"] != "before 1474"].iterrows() if r.period not in ("1751-1800", "1801-1852")]
        return F(svg_bars(items, ",.0f", label_w=330), "a2")
    if mid == "a3_1624":
        a = D["m_a3_1624"]
        w = a[a.grants.notna()]
        items = [(r.window, float(r.per_year), 0) for r in w.itertuples()]
        err = {r.window: (r.ci_low, r.ci_high) for r in w.itertuples()}
        return F(svg_bars(items, ".1f", label_w=140, errors=err), "a3")
    if mid == "a4_extensions":
        a = D["m_a4_extensions"]
        # A decade absent from the table is a decade with no grants at all in the annual list (the 1650s): the count is a true zero, not a gap.
        g = D["m_a1_annual"]
        have = {int(r.decade): float(r.extensions) for r in a.itertuples()}
        pts = [(dc, have[dc] if dc in have else (0.0 if g[(g.year >= dc) & (g.year < dc + 10)].grants.sum() == 0 else math.nan)) for dc in range(int(a.decade.min()), int(a.decade.max()) + 1, 10)]
        return F(svg_lines([(N("extension entries", "연장 항목"), pts, 0)], ",.0f", xstep=20), "a4")
    if mid == "b1_fields":
        b = D["m_b1_fields"]
        b = b[b.source == "Woodcroft"]
        per = list(dict.fromkeys(b.period))
        x = {p: i for i, p in enumerate(per)}
        top = b[b.field != "other"].groupby("field")["count"].sum().sort_values(ascending=False).head(4).index.tolist()
        series = [(N(FL.LABEL[f]["en"], FL.LABEL[f]["ko"]), [(x[r.period], float(r.share)) for r in b[b.field == f].itertuples()], i) for i, f in enumerate(top)]
        dash = lambda pr: pr.replace("-", "–")     # period keys use a hyphen in the data; the labels use an en dash
        svg = svg_lines(series, ".0%", xstep=1, xnames={i: dash(pr) for pr, i in x.items()})
        return F(svg, "b1")
    if mid == "b2_hhi":
        b = D["m_b2_hhi"]
        # 1.1.1: HHI (an index) and the 'other' share (a proportion) are drawn in two charts with their own axes; the values are those of the table.
        s_h = svg_lines([("HHI", [(r.decade, float(r.hhi)) for r in b.itertuples()], 0)], ".2f", xstep=20,
                        hline=(1 / N_FIELDS, (f"{N_FIELDS}분야에 고르게 나뉠 때 {1 / N_FIELDS:.3f}" if ko else f"{1 / N_FIELDS:.3f} if spread evenly over {N_FIELDS} fields")))
        s_o = svg_lines([(N("other", "기타"), [(r.decade, float(r.other_share)) for r in b.itertuples()], 1)], ".0%", xstep=20)
        return F(s_h, "b2_h") + F(s_o, "b2_o")
    if mid == "b3_venice_sectors":
        b = D["m_b3_venice_sectors"]
        return F(svg_bars([((f"{SECTOR_KO.get(r.sector_berveglieri, r.sector_berveglieri)} ({r.sector_berveglieri})" if ko else r.sector_berveglieri), float(r.count), 1) for r in b.itertuples()], ",.0f", label_w=390), "b3")
    if mid == "c1_foreign":
        c = D["m_c1_foreign_gb"]
        c = c[c.decade >= 1700]
        s = svg_lines([(N("communication", "communication"), [(r.decade, float(r.communication_share)) for r in c.itertuples()], 0),
                       (N("address abroad", "해외 주소"), [(r.decade, float(r.foreign_address_share)) for r in c.itertuples()], 1),
                       (N("either", "둘 중 하나"), [(r.decade, float(r.either_share)) for r in c.itertuples()], 2)], ".0%", xstep=20)
        return F(s, "c1")
    if mid == "c2_cogrant":
        c = D["m_c2_cogrant"]
        return F(svg_lines([(N("shared grants", "공동 허여"), [(r.decade, float(r.co_share)) for r in c.itertuples()], 0)], ".0%", xstep=20), "c2")
    if mid == "d1_terms":
        d = D["m_d1_terms"]
        d = d[d.n_stated > 0]
        items = [(source_label(r.source, lang), float(r["median"]), 0) for _, r in d.iterrows()]
        err = {source_label(r.source, lang): (r.p25, r.p75) for _, r in d.iterrows()}
        return F(svg_bars(items, ".0f", label_w=360, errors=err), "d1")
    if mid == "d2_term_shift":
        d = D["m_d2_term_shift"]
        # A year absent from the table is a year with no grants in the annual list (1643–1659 and others): both counts are true zeros, not gaps.
        g = D["m_a1_annual"].set_index("year").grants
        have = {int(r.year): r for r in d.itertuples()}
        yrs = range(int(d.year.min()), int(d.year.max()) + 1)
        val = lambda y, col: float(getattr(have[y], col)) if y in have else (0.0 if g.get(y, math.nan) == 0 else math.nan)
        return F(svg_lines([(N("21 years", "21년"), [(y, val(y, "eq21")) for y in yrs], 0), (N("≤14 years", "14년 이하"), [(y, val(y, "le14")) for y in yrs], 1)], ",.0f",
                               bands=[(1624, 1625, "1624")], xstep=5), "d2")
    if mid == "d3_clauses":
        d = D["m_d3_clauses"]
        return F(svg_lines([(N("rent", "지대"), [(r.decade, float(r.rent_share)) for r in d.itertuples()], 0), (N("proviso", "단서"), [(r.decade, float(r.proviso_share)) for r in d.itertuples()], 1)], ".0%", xstep=20), "d3")
    if mid == "p1_sro_annual":
        p = D["m_p1_sro_annual"]
        return F(svg_lines([(N("entries", "등록"), [(r.year, math.nan if r.gap else float(r.entries)) for r in p.itertuples()], 0)], ",.0f", bands=[(1571, 1576, N("gap", "기록 없음")), (1637, 1638, "1637")], xstep=10), "p1")
    if mid == "p2_sro_concentration":
        p = D["m_p2_sro_concentration"]
        p = p[p.entries >= 20]
        return F(svg_lines([(N("top five", "상위 5인"), [(r.year, float(r.top5_share)) for r in p.itertuples()], 0)], ".0%", xstep=10), "p2")
    if mid == "p3_sro_status":
        p = D["m_p3_sro_status"]
        return F(svg_lines([(N("reassigned", "양도"), [(r.decade, float(r.reassigned_share)) for r in p.itertuples()], 0), (N("shared", "공동 등록"), [(r.decade, float(r.shared_share)) for r in p.itertuples()], 1)], ".0%", xstep=10), "p3")
    if mid == "p4_sro_fees":
        p = D["m_p4_sro_fees"]
        p = p[p.with_fee >= 10]
        return F(svg_lines([(N("6d", "6펜스"), [(r.year, float(r.fee6_share)) for r in p.itertuples()], 0)], ".0%", bands=[(1582, 1587, "1582–1587")], xstep=10), "p4")
    if mid == "v1_venice_printing":
        v = D["m_v1_fulin_annual"]
        v = v.assign(b=v.year // 5 * 5).groupby("b")[["privileges", "author", "printer"]].sum().reset_index()
        s = svg_lines([(N("all", "전체"), [(r.b, float(r.privileges)) for r in v.itertuples()], 0),
                       (N("author", "저자"), [(r.b, float(r.author)) for r in v.itertuples()], 1),
                       (N("printer", "인쇄업자"), [(r.b, float(r.printer)) for r in v.itertuples()], 2)], ",.0f", bands=[(1517, 1518, "1517")], xstep=10)
        return F(s, "v1")
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
        cols = [("field_name", col_label("field_name", lang), None)] + [(c, c.replace("-", "–"), ".0%") for c in w.columns if c != "field_name"]
        return table_html(w, cols, f"t_{mid}", lang)
    keyed = [c for c in ("top_field", "our_field") if c in df.columns]
    if keyed:   # 1.1.1: field keys shown by their names on the page; the CSV keeps the keys
        df = df.copy()
        for c in keyed:
            df[c] = df[c].map(lambda v: FL.LABEL[v][lang] if isinstance(v, str) and v in FL.LABEL else v)
    cols = [(c, col_label(c, lang), col_spec(df, c)) for c in df.columns]
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
    dt = {"원자료": "자료원", "출처": "자료원"} if lang == "ko" else {}      # reliability.json keeps its keys; the page uses one term
    items = list((r.get(lang) or {}).items())
    # 1.1.1: field keys in the per-field row are shown by their names (reliability.json keeps the keys)
    named = lambda v: _FIELD_KEY_RE.sub(lambda mm: FL.LABEL[mm.group(1)][lang], v)
    rows = "".join(f"<dt>{esc(dt.get(k, k))}</dt><dd>{esc(named(v))}</dd>" for k, v in items)
    note = rel_gloss(" ".join(f"{k} {v}" for k, v in items), lang)
    note_html = f"<p class='src gloss'>{esc(note)}</p>" if note else ""
    return f'<div class="spec rel"><h3><span class="badge">{T[lang]["badge"][kind]}</span>{T[lang]["reliability"]}</h3><p class="src">{esc(T[lang]["rel"][kind])}</p>{"<dl>" + rows + "</dl>" if rows else ""}{note_html}</div>'


def metric_page(mid, D, TK, rel, lang):
    m, t = METRICS[mid], T[lang]
    L = m[lang]
    kv = [cap(x, lang) for x in TK[mid]["kv"][lang]]
    body = [f'<div class="eyebrow"><span class="tag layer">{m["series"]} · {esc(SERIES[m["series"]][lang])}</span></div>',
            f'<div class="mhero"><h1>{esc(L["name"])}</h1><div class="big{" long" if len(kv[0]) > 12 else ""}">{esc(kv[0])}<small>{esc(kv[1])}</small></div></div>',
            take(TK[mid][lang], lang)]
    body.append(f'<div class="spec"><dl><dt>{t["definition"]}</dt><dd>{esc(L["definition"])}</dd><dt>{t["formula"]}</dt><dd class="formula">{esc(L["formula"])}</dd>'
                f'<dt>{t["reading"]}</dt><dd>{esc(L["reading"])}</dd><dt>{t["caveat"]}</dt><dd>{esc(L["caveat"])}</dd></dl></div>')
    body.append(figure(mid, D, lang))
    body.append(f"<p class='src'>{esc(GLOSS[lang])}{(' ' + esc(STATUTE_GLOSS[lang])) if ' c. ' in L['definition'] else ''}</p>")   # 1.1; statute note 1.1.1
    body.append(f'<h2 id="table">{t["table"]}</h2><p class="files"><a href="../../data/{m["table"]}.csv">{t["download"]} · {m["table"]}.csv</a></p>')
    body.append(table_for(mid, D, lang))
    body.append(rel_card(mid, rel, lang))
    if m.get("prior"):
        body.append(f'<h2 id="prior">{t["prior"]}</h2><ul class="prose">' + "".join(f'<li>{md(PRIOR[p][lang])} <span class="src">— {md(PRIOR[p]["cite"])}</span></li>' for p in m["prior"]) + "</ul>")
    body.append(f'<h2 id="sources">{t["source"]}</h2><ul class="prose">' + "".join(f'<li>{md(SOURCES[s][lang])} <span class="src">({esc(SOURCES[s]["license_ko" if lang == "ko" else "license"])}; <a href="{SOURCES[s]["url"]}">{esc(SOURCES[s]["url"])}</a>)</span></li>' for s in m["sources"]) + "</ul>")
    body.append(f'<div class="links"><a href="index.html">← {t["metric_list"]}</a></div>')
    return page(lang, L["name"], "".join(body), depth=2, active="metrics", desc=TK[mid][lang], rel=f"metrics/{mid}.html", toc=False,
                leaf=metric_siblings(lang, mid))


def cards(D, TK, lang, ids=None, depth=1):
    pre = "metrics/" if depth == 1 else ""
    out = ['<div class="cards">']
    for mid, m in METRICS.items():
        if ids and mid not in ids:
            continue
        kv = [cap(x, lang) for x in TK[mid]["kv"][lang]]
        out.append(f'<a class="card s-{ {"A": "A", "B": "B", "C": "C", "D": "D", "P": "E"}[m["series"]] }" href="{pre}{mid}.html"><b>{esc(m[lang]["name"])}</b>'
                   f'<span class="kv">{esc(kv[0])}<small>{esc(kv[1])}</small></span><small>{esc(m[lang]["definition"][:90])}…</small></a>')
    out.append("</div>")
    return "".join(out)


def metrics_index(D, TK, lang):
    t = T[lang]
    body = [f"<h1>{t['metric_list']}</h1><p class='lead'>{'지표 ' + str(len(METRICS)) + '개. 계열마다 묶었다.' if lang == 'ko' else str(len(METRICS)) + ' metrics, grouped by series.'}</p>"]
    for s, lab in SERIES.items():
        ids = [k for k, m in METRICS.items() if m["series"] == s]
        body.append(f"<h2 id='s-{s}'>{s} · {esc(lab[lang])}</h2>" + cards(D, TK, lang, ids, depth=2))
    return page(lang, t["metric_list"], "".join(body), depth=2, active="metrics", rel="metrics/index.html")


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
        body.append(f"<h2 id='s-{s}'>{s} · {esc(lab[lang])}</h2>" + cards(D, TK, lang, ids, depth=1))
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
    jump = " · ".join(f"<a href='#j-{j}'>{JUR[j][lang]}</a>" for j in blocks)       # 1.0.3: one page, three sections
    body = [f"<h1>{t['nav_places']}</h1><nav class='jump' aria-label='{'관할' if ko else 'Jurisdictions'}'>{jump}</nav>"]
    for j, (ids, txt) in blocks.items():
        body.append(f"<h2 id='j-{j}'>{JUR[j][lang]}</h2><p class='prose'>{esc(txt)}</p>" + cards(D, TK, lang, ids, depth=1))
    return page(lang, t["nav_places"], "".join(body), depth=1, active="places", rel="places.html", toc=False)


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
    # 1.1.1: the two series count different things, so each has its own chart and axis (before 1.1.1 they shared one axis).
    e1 = a1[a1.year <= 1700]
    s_v = svg_lines([("Venetian printing" if not ko else "베네치아 출판", [(r.year, float(r.privileges)) for r in v1.itertuples()], 1)], ",.0f",
                    bands=[(1474, 1475, "1474"), (1517, 1518, "1517")], xstep=10, lang=lang,
                    ylabel=("베네치아 출판 특권 문서 수(건/년)" if ko else "Venetian printing privileges per year"), xlabel=("연도" if ko else "year"))
    s_e = svg_lines([("English inventions" if not ko else "잉글랜드 발명", [(r.year, float(r.grants)) for r in e1.itertuples() if not pd.isna(r.grants)], 0)], ",.0f",
                    bands=[(1604, 1616, "목록 공백" if ko else "gap"), (1624, 1625, "1624")], xstep=20, lang=lang,
                    ylabel=("잉글랜드 발명 독점 허여·특허 수(건/년)" if ko else "English invention grants and patents per year"), xlabel=("연도" if ko else "year"))
    intro = ("<p>아래 두 그림은 연표에 나오는 두 자료의 해마다 건수다. 위 그림 「베네치아 출판」은 Fulin이 엮은 문서 가운데 이 사이트가 출판 특권으로 분류한 문서의 수이고, 아래 그림 「잉글랜드 발명」은 Hulme과 Woodcroft의 목록에 실린 독점 허여·특허의 수다. 세는 것도, 다루는 기간도 달라 그림을 나누었다. 두 그림의 높이를 서로 견주지 않는다.</p>"
             if ko else "<p>The two charts below give the yearly counts of the two sources on the timeline. The first, 'Venetian printing', counts the documents edited by Fulin that this site classes as printing privileges; the second, 'English inventions', counts the monopoly grants and patents in the lists of Hulme and Woodcroft. They count different things over different years, so they are drawn apart; their heights are not to be compared.</p>")
    body = [f"<h1>{T[lang]['nav_eras']}</h1>", intro, fig_notes(s_v, "eras_v", D, lang), fig_notes(s_e, "eras_e", D, lang),
            "<div class='wrap'><table><thead><tr><th class='num'>" + T[lang]["year"] + "</th><th>" + ("사건" if ko else "Event") + "</th></tr></thead><tbody>" +
            "".join(f"<tr><td class='num'>{y}</td><td>{esc(x)}</td></tr>" for y, x in ev) + "</tbody></table></div>",
            "<p class='src'>" + ("연표의 연도·사건은 각 자료원(Fulin·Hulme·Woodcroft·SRO)과 법령 명칭에서 가져왔다." if ko else "Years and events are taken from the sources used (Fulin, Hulme, Woodcroft, SRO) and the titles of the statutes.") + " " + esc(STATUTE_GLOSS[lang]) + "</p>"]
    return page(lang, T[lang]["nav_eras"], "".join(body), depth=1, active="eras", rel="eras.html")


def prior_page(lang):
    t = T[lang]
    lead = ("선행 수치. 원문에서 확인한 것을 싣되, 원문을 보지 못하고 다른 문헌을 거쳐 옮긴 것은 「2차 인용」으로 표시했다. 이 사이트의 계수와 나란히 본다." if lang == "ko" else
            "Prior figures, checked in the original publications except those marked as secondary citations, which are taken from another work. Read them next to this site's counts.")
    body = [f"<h1>{t['nav_prior']}</h1><p class='lead'>{esc(lead)}</p><ul class='prose'>"]
    for k, p in PRIOR.items():
        body.append(f"<li>{md(p[lang])} <span class='src'>— {md(p['cite'])}</span></li>")
    body.append("</ul>")
    return page(lang, t["nav_prior"], "".join(body), depth=1, active="prior", rel="prior.html")


DATA_FILES = [("woodcroft_entries.csv.gz", "CC BY 4.0", "woodcroft"), ("hulme_1561_1603.csv", "CC BY 4.0", "hulme"), ("fulin_coding.csv", "CC BY 4.0", "fulin"),
              ("sro/sro_entries.csv.gz", "CC BY-SA 4.0", "sro"), ("sro/sro_site_decade_counts.csv", "CC BY-SA 4.0", "sro")]


def data_page(D, lang):
    ko = lang == "ko"
    t = T[lang]
    rows = [f"<tr><td><a href='../data/{f}'>{f}</a></td><td>{lic}</td><td>{esc(SOURCES[s]['license_ko' if ko else 'license'])}</td></tr>" for f, lic, s in DATA_FILES]
    rows += [f"<tr><td><a href='../data/{k}.csv'>{k}.csv</a></td><td>CC BY 4.0</td><td>—</td></tr>" for k in sorted(D)]
    body = [f"<h1>{t['nav_data']}</h1>",
            "<p class='prose'>" + ("레코드 표와 지표 표를 CSV로 낸다. 각 파일의 라이선스와 원자료 라이선스는 data/datapackage.json 에도 적었다. 출판업조합 등록 표는 원자료 조건에 따라 CC BY-SA 4.0으로 별도 폴더(data/sro/)에 둔다. 네덜란드 원자료는 다시 배포하지 않고 DOI로만 잇는다." if ko else
                                   "Record tables and metric tables are published as CSV. Each file's license and its source license are also listed in data/datapackage.json. The Stationers' Register table is CC BY-SA 4.0, as its source requires, and sits in its own folder (data/sro/). The Dutch source data are not redistributed; they are linked by DOI.") + "</p>",
            "<div class='wrap'><table><thead><tr><th>" + t["file"] + "</th><th>" + t["license"] + "</th><th>" + ("원자료 라이선스" if ko else "Source license") + "</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>",
            "<p class='files'><a href='../data/datapackage.json'>datapackage.json</a> <a href='../data/reliability.json'>reliability.json</a></p>"]
    return page(lang, t["nav_data"], "".join(body), depth=1, active="data", rel="data.html")


def method_page(rel, lang):
    ko = lang == "ko"
    t = T[lang]
    secs = METHOD[lang]
    body = [f"<h1>{t['nav_method']}</h1><div class='prose'>"]
    assert len(secs) == len(METHOD_IDS), "method sections and METHOD_IDS differ in number"
    for i, (h, ps) in zip(METHOD_IDS, secs):
        body.append(f'<h2 id="{i}">{esc(h)}</h2>' + "".join(f"<p>{esc(p)}</p>" for p in ps))
    body.append("</div>")
    return page(lang, t["nav_method"], "".join(body), depth=1, active="method", rel="method.html")


METHOD = {"ko": [], "en": []}     # filled from method_text.py
READING = {"ko": [], "en": []}


def reading_page(lang):
    t = T[lang]
    body = [f"<h1>{t['nav_reading']}</h1><div class='prose'>"]
    assert len(READING[lang]) == len(READING_IDS), "reading sections and READING_IDS differ in number"
    for i, (h, ps) in zip(READING_IDS, READING[lang]):
        body.append(f'<h2 id="{i}">{esc(h)}</h2>' + "".join(f"<p>{esc(p)}</p>" for p in ps))
    body.append("</div>")
    return page(lang, t["nav_reading"], "".join(body), depth=1, active="reading", rel="reading.html")


def write_data(D):
    dd = OUT / "data"
    (dd / "sro").mkdir(parents=True, exist_ok=True)
    for k, df in D.items():
        df.to_csv(dd / f"{k}.csv", index=False, encoding="utf-8")
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    with gzip.open(dd / "woodcroft_entries.csv.gz", "wt", encoding="utf-8", newline="") as f:
        W.to_csv(f, index=False)
    shutil.copy(need(COD / "hulme_1561_1603.csv"), dd / "hulme_1561_1603.csv")
    shutil.copy(need(COD / "fulin_coding.csv"), dd / "fulin_coding.csv")
    S = pd.read_csv(find(DER, "sro_entries.csv"))
    with gzip.open(dd / "sro" / "sro_entries.csv.gz", "wt", encoding="utf-8", newline="") as f:
        S.to_csv(f, index=False)
    shutil.copy(find(DER, "sro_site_decade_counts.csv"), dd / "sro" / "sro_site_decade_counts.csv")
    shutil.copy(need(DER / "reliability.json"), dd / "reliability.json")
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
