# -*- coding: utf-8 -*-
"""1.1.4: plain-language notes for every chart, Korean and English.

notes(key, D, lang, ctx) returns (intro, [(heading, text), ...]). The intro is one line above the chart; the parts go in
the caption under it: In short / How the chart works / Reading one value / The numbers / Easy to misread / Terms.
Every number is computed here from the metric tables (D) and reliability.json (ctx["rel"]); none is typed by hand.
A check that fails (an assumption the wording rests on) stops the build instead of printing a wrong sentence.
"""
import math
import re

import pandas as pd

H = {"ko": {"short": "한눈에", "how": "그림 보는 법", "one": "숫자 하나 읽어 보기", "nums": "수로 보면", "mis": "잘못 읽기 쉬운 것", "terms": "낱말 풀이"},
     "en": {"short": "In short", "how": "How the chart works", "one": "Reading one value", "nums": "The numbers", "mis": "Easy to misread", "terms": "Terms"}}


def n(x) -> str:
    return f"{int(round(float(x))):,}"


def pc(x, d=1) -> str:
    return f"{float(x) * 100:.{d}f}%"


def f1(x) -> str:
    return f"{float(x):.1f}"


def ranges(years) -> list:
    ys = sorted(int(y) for y in years)
    out, s = [], None
    for i, y in enumerate(ys):
        if s is None:
            s = y
        if i == len(ys) - 1 or ys[i + 1] != y + 1:
            out.append((s, y))
            s = None
    return out


def yr_list(years, lang) -> str:
    parts = [(f"{a}" if a == b else f"{a}–{b}") for a, b in ranges(years)]
    if lang == "ko":
        return "·".join(parts) + "년"
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def dec(d, lang) -> str:
    return f"{int(d)}년대" if lang == "ko" else f"{int(d)}s"


def J(num: str, pair: str = "은는") -> str:
    """num followed by the Korean topic particle that fits how the number is read aloud (20 이십은, 42 사십이는, 0.105 ...오는)."""
    digits = re.sub(r"[^0-9.]", "", str(num))
    if "." in digits:
        last = digits.rstrip("0").split(".")[-1][-1:] or digits.split(".")[0][-1:]
        zeros = 0
    else:
        stripped = digits.rstrip("0")
        zeros = len(digits) - len(stripped)
        last = stripped[-1:] if stripped else "0"
    if zeros:
        batchim = {1: True, 2: True, 3: False}.get(zeros, True)      # 십 백 천 만
    else:
        batchim = last in "013678"                                    # 영 일 삼 육 칠 팔 have a final consonant
    return f"{num}{pair[0] if batchim else pair[1]}"


def _check(cond, msg):
    if not cond:
        raise SystemExit(f"fig_notes: {msg}")


def _cov(spec: str) -> list:
    """'1561-1603, 1617-1852' -> [(1561, 1603), (1617, 1852)]; '-1473' -> []."""
    out = []
    for part in spec.split(","):
        m = re.fullmatch(r"\s*(\d{4})-(\d{4})\s*", part)
        if m:
            out.append((int(m.group(1)), int(m.group(2))))
    return out


def _rel_nums(rel, mid):
    ko = rel.get(mid, {}).get("ko", {})
    simple = next((v for k, v in ko.items() if "층화 표본" in k), "")
    weighted = next((v for k, v in ko.items() if "가중" in k), "")
    other = re.search(r"\bother ([0-9]+)/([0-9]+)", next((v for k, v in ko.items() if k == "분야별 일치"), ""))
    ms = re.match(r"([0-9]+)/([0-9]+) \(([0-9]+)%", simple)
    _check(ms and weighted and other, f"reliability figures for {mid} not found")
    return dict(k=int(ms.group(1)), n=int(ms.group(2)), simple=ms.group(3) + "%", weighted=weighted, ok=int(other.group(1)), on=int(other.group(2)))


def notes(key, D, lang, ctx):
    ko = lang == "ko"
    h = H[lang]
    FL = ctx["FL"]
    L = lambda f: FL.LABEL[f][lang]
    a1 = D["m_a1_annual"]
    W = ctx["W"]
    P = []
    W53 = W[W.year > 1852]                                   # entries sealed after 1852 (Woodcroft's list runs on into 1853)
    after_oct = int(((W.year == 1852) & (W.date.fillna("").astype(str) > "1852-10-01")).sum())
    y53 = int(W53.date.isna().sum())
    late_ko = f"Woodcroft 목록은 표제에 1852년 10월 1일까지라고 적지만, 여백의 날인일로는 1852년 가운데 10월 1일 뒤가 {after_oct}항목이고 1853년으로 기록된 항목이 {len(W53)}개다(그 가운데 {y53}개는 연도만 확인)"
    late_en = f"Woodcroft's title runs to 1 October 1852, but by the sealing dates in the margin {after_oct} entries fall after that day in 1852 and {len(W53)} are recorded under 1853 ({y53} of them by year only)"

    def add(k, text):
        P.append((h[k], text))

    # ------------------------------------------------------------------ A
    if key in ("a1_e", "eras_e"):
        e = a1[a1.year <= 1700]
        hul = a1[a1.year <= 1603].grants.sum()
        w = a1[(a1.year >= 1617) & (a1.year <= 1700)]
        mx = e.loc[e.grants.idxmax()]
        zero_w = w[w.grants == 0].year.tolist()
        zero_h = a1[(a1.year <= 1603) & (a1.grants == 0)].year.tolist()
        gap = a1[a1.grants.isna()].year.tolist()
        _check(ranges(gap) == [(1604, 1616)], "a1 gap is not 1604-1616")
        intro = ("잉글랜드의 두 목록에 실린 발명 독점 허여·특허가 해마다 몇 건인지, 1561년부터 1700년까지 그린 그림이다." if ko else
                 "How many new monopoly grants and patents for inventions England's two lists give for each year, 1561–1700.")
        add("short", (f"1561–1603년 43년 동안 {n(hul)}건, 1617–1700년 84년 동안 {n(w.grants.sum())}건이다. 이 그림에서 가장 많은 해는 {int(mx.year)}년({n(mx.grants)}건)이다." if ko else
                      f"{n(hul)} in the 43 years 1561–1603 and {n(w.grants.sum())} in the 84 years 1617–1700. The largest year in this chart is {int(mx.year)} ({n(mx.grants)})."))
        trade = int(D["m_c1_hulme"].hulme_trade.sum())
        add("how", (f"가로는 연도, 세로는 그해 허여 수(건)다. 선이 높을수록 그해 허여가 많다. 1603년까지는 Hulme 목록의 건수(발명이 아닌 거래 규제 허여 {trade}건 포함), 1617년부터는 Woodcroft 목록의 번호 항목에서 기간 연장 항목을 뺀 수다. "
                    "넓은 음영 「목록 공백」은 두 목록 사이의 1604–1616년으로, 목록이 없어 선을 끊었다. 좁은 음영 「1624」는 독점법이 나온 해다. 해마다 선 위의 점 근처에 커서를 두면 그해 값이 보인다(목록 공백에는 값이 없다)." if ko else
                    f"Across: year; up: grants in that year. The higher the line, the more grants that year. To 1603 the count is Hulme's list (including {trade} grants regulating trade, not inventions); from 1617 it is the numbered entries of Woodcroft's list less the extensions of existing patents. "
                    "The wide shaded band, 'Gap', is 1604–1616, between the two lists: there is no list, so the line breaks. The narrow band '1624' is the year of the Statute of Monopolies. Hover near the point for a year on the line to see its value (the gap has none)."))
        add("one", (f"{int(mx.year)}년 값 {J(n(mx.grants))} Woodcroft 목록에서 그해로 센 새 허여 항목이 {n(mx.grants)}개라는 뜻이다. 연도는 목록 여백의 날인일을 기본으로 하고, 여백에 연도만 남았거나 날짜가 읽히지 않은 항목은 쪽 이미지나 앞뒤 항목으로 보완했다." if ko else
                    f"The value for {int(mx.year)}, {n(mx.grants)}, means that {n(mx.grants)} new grant entries in Woodcroft's list are counted in that year. The year comes from the sealing date printed in the margin; where only the year survives there or the date cannot be read, the page image or the neighbouring entries fill it in."))
        add("mis", (f"1604–1616년의 빈자리는 0건이 아니라 이 사이트가 쓰는 목록이 없는 해다. 반대로 선이 바닥(0)에 닿는 해는 목록이 있는데 그해 허여가 없는 해다 — 1617년 뒤로는 {yr_list(zero_w, lang)}, Hulme 목록에서는 {int(a1[a1.year <= 1603].shape[0])}해 가운데 {len(zero_h)}해다. "
                    f"1603년까지와 1617년부터는 엮은 사람과 고른 범위가 다른 두 목록이라, 그 사이의 높이 차이를 그대로 이어 읽지 않는다. 음영 「1624」는 해를 표시할 뿐, 그해에 수가 바뀌었다는 뜻이 아니다(앞뒤 비교는 「{ctx['METRICS']['a3_1624']['ko']['name']}」 면)." if ko else
                    f"The empty stretch 1604–1616 is not zero: the site has no list for those years. Where the line touches the floor (0), a list exists and has no grant that year: after 1617 in {yr_list(zero_w, lang)}, and in {len(zero_h)} of the {int(a1[a1.year <= 1603].shape[0])} years of Hulme's list. "
                    f"The years to 1603 and from 1617 come from two lists made by different compilers with different scopes, so the step between them is not one continuous series. The band '1624' marks the year only; it does not say the count changed then (the before-and-after comparison is on the page '{ctx['METRICS']['a3_1624']['en']['name']}')."))
        add("terms", ("허여(許與) = 특권이나 특허를 내려 주는 일. 기간 연장 = 이미 있는 특허의 기간을 늘리거나 확인해 준 항목(새 허여가 아니어서 뺐다). 날인일 = 특허장에 봉인을 찍은 날." if ko else
                      "Grant = the act of conferring a privilege or patent. Extension = an entry that lengthens or confirms an existing patent (not a new grant, so left out). Sealing date = the day the patent was sealed."))
        if key == "eras_e":
            intro = (f"잉글랜드 발명 독점 허여·특허가 해마다 몇 건인지, 1561년부터 1700년까지 그린 그림이다(지표 면 「{ctx['METRICS']['a1_annual']['ko']['name']}」의 앞 그림과 같은 값)." if ko else
                     f"English invention grants and patents per year, 1561–1700 (the same values as the first chart on the metric page '{ctx['METRICS']['a1_annual']['en']['name']}').")
            P[:] = [p for p in P if p[0] != h["terms"]]
        return intro, P

    if key == "a1_l":
        l = a1[a1.year >= 1700]
        mx = l.loc[l.grants.idxmax()]
        m0 = a1[(a1.year >= 1700) & (a1.year <= 1709)].grants.mean()
        m1 = a1[(a1.year >= 1840) & (a1.year <= 1849)].grants.mean()
        ex = int(a1[a1.year == int(mx.year)].woodcroft_extensions.iloc[0])
        intro = ("같은 수를 1700년부터 1852년까지 그린 그림이다. 수가 훨씬 커서 위 그림과 세로 눈금을 따로 잡았다." if ko else
                 "The same count for 1700–1852. The numbers are far larger, so this chart has its own vertical scale.")
        add("short", (f"1700–1709년에는 한 해 평균 {f1(m0)}건, 1840–1849년에는 한 해 평균 {f1(m1)}건이다. 가장 많은 해는 {int(mx.year)}년({n(mx.grants)}건)이다." if ko else
                      f"An average of {f1(m0)} a year in 1700–1709 and {f1(m1)} a year in 1840–1849. The largest year is {int(mx.year)} ({n(mx.grants)})."))
        add("how", ("가로는 연도, 세로는 그해 허여 수(건)다. 모두 Woodcroft 목록의 번호 항목에서 기간 연장 항목을 뺀 수다. 해마다 선 위의 점 근처에 커서를 두면 그해 값이 보인다." if ko else
                    "Across: year; up: grants in that year, all from Woodcroft's list (numbered entries less extensions). Hover near the point for a year on the line to see its value."))
        add("one", (f"{int(mx.year)}년 값 {J(n(mx.grants))} Woodcroft 목록에서 그해로 센 새 특허 항목이 {n(mx.grants)}개라는 뜻이다. 그해 목록에는 이 밖에 기간 연장 항목이 {ex}개 더 있다." if ko else
                    f"The value for {int(mx.year)}, {n(mx.grants)}, means {n(mx.grants)} new patent entries in Woodcroft's list are counted in that year; the list has {ex} extension entries for that year besides."))
        late_g = int((W53.kind == "grant").sum())
        add("mis", (f"위 그림과 세로 눈금이 달라 두 그림의 선 높이를 견주지 않는다. 1700년은 두 그림에 모두 들어 있다. {late_ko}. 1853년의 새 허여 {late_g}건은 이 그림과 표에 없으니, 마지막 해 1852년은 다른 해와 셈의 조건이 같다고 하기 어렵다. 수는 목록에 실린 새 허여 항목의 수이지, 그해 나온 발명 전부의 수가 아니다." if ko else
                    f"The vertical scale differs from the chart above, so the heights of the two lines are not to be compared. 1700 is in both charts. {late_en}. The {late_g} new grants of 1853 are not in this chart or its table, so the last year, 1852, is not on the same footing as the others. The count is of new grant entries in the list, not of all inventions made that year."))
        return intro, P

    if key == "a2":
        a = D["m_a2_periods"]
        hul = D["m_c1_hulme"]
        drawn = a[(a["period"] != "before 1474") & ~a.period.isin(["1751-1800", "1801-1852"])]
        left = a[~a.index.isin(drawn.index)]
        partial = []
        for _, r in drawn.iterrows():
            if r.basis == "secondary":
                continue
            p0, p1_ = (int(x) for x in r.period.split("-"))
            eff = [(max(p0, c0), min(p1_, c1)) for c0, c1 in _cov(r.coverage) if max(p0, c0) <= min(p1_, c1)]
            if eff != [(p0, p1_)]:
                kind = ("발명" if r.kind == "invention" else "출판") if ko else r.kind
                span = ("·" if ko else ", ").join(f"{x}–{y}" for x, y in eff)
                partial.append((f"{ctx['JUR'][r.jurisdiction][lang]} {kind} {r.period}", span))
        shortp = []
        for _, r in drawn.iterrows():
            p0, p1_ = (int(x) for x in r.period.split("-"))
            if p1_ - p0 + 1 < 50:
                kind = ("발명" if r.kind == "invention" else "출판") if ko else r.kind
                shortp.append((f"{ctx['JUR'][r.jurisdiction][lang]} {kind} {r.period}", p1_ - p0 + 1))
        ve = drawn[(drawn.jurisdiction == "VE") & (drawn.kind == "invention")].sort_values("period")
        last = ve.iloc[-1]
        trade = int(hul.hulme_trade.sum())
        ex_txt = ", ".join(f"{('1474년 이전 베네치아 임시 특권' if r.period == 'before 1474' else '잉글랜드 ' + r.period) if ko else ('Venetian ad hoc privileges before 1474' if r.period == 'before 1474' else 'England ' + r.period)} {n(r['count'])}" for _, r in left.iterrows())
        intro = ("잉글랜드·베네치아·네덜란드의 발명·출판 특권이 대체로 반세기 구간마다 자료에 몇 건 있는지 막대로 늘어놓은 그림이다." if ko else
                 "How many invention and printing privileges the sources give for England, Venice and the Dutch Republic, mostly by half-century, as bars.")
        add("how", (f"막대 하나가 「관할 · 종류 · 구간」 하나다. 막대가 길수록 그 구간에 센 건수가 많다. 색은 관할을 가른다(이름 맨 앞). 별표(*)는 이 사이트가 세지 않고 Comino 등에서 옮긴 2차 인용이다. 다음은 그림에 없고 표에만 있다: {ex_txt}." if ko else
                    f"Each bar is one jurisdiction, kind and period, as named. The longer the bar, the more counted in that period. Colour marks the jurisdiction (the first word of the name). An asterisk (*) marks a secondary figure, quoted from Comino et al. and not counted here. These are in the table only, not in the chart: {ex_txt}."))
        add("one", (f"「베네치아 · 발명 · {last.period} *」의 {J(n(last['count']))} Comino 등이 Berveglieri의 자료로 적은 그 50년의 원로원 특허 수다. 같은 50년을 Kostylo는 {n(last.alt_count)}건으로 적는다(표의 「다른 계수」)." if ko else
                    f"'Venice · invention · {last.period} *', {n(last['count'])}, is the number of Senate patents in those fifty years as given by Comino et al. from Berveglieri's data; Kostylo gives {n(last.alt_count)} for the same years (the table's 'Other count')."))
        add("mis", (("관할마다 세는 단위가 달라(베네치아 발명은 원로원 특허, 네덜란드는 특권 허여 문서, 잉글랜드는 허여, 베네치아 출판은 Fulin이 모은 문서) 막대 길이를 관할끼리 그대로 견줄 수 없다. "
                     "구간 이름부터 50년이 안 되는 막대가 있다: " + "; ".join(f"{a_}은 {y_}년" for a_, y_ in shortp) + ". 이름은 50년이지만 자료가 그 기간을 다 덮지 않는 막대도 있다: " + "; ".join(f"{a_} → {b_}년" for a_, b_ in partial) + ". "
                     f"잉글랜드 1551-1600의 Hulme 목록에는 거래 규제 허여 {trade}건이 들어 있다. 어느 막대든 자료에 실린 수이지, 실제로 내려진 특권 전부의 수가 아니다.") if ko else
                    ("The unit differs by jurisdiction (Senate patents for Venetian inventions, privilege documents for the Dutch Republic, grants for England, Fulin's documents for Venetian printing), so bar lengths are not to be compared across jurisdictions as they stand. "
                     "Some periods are shorter than fifty years by name: " + "; ".join(f"{a_} is {y_} years" for a_, y_ in shortp) + ". Others are fifty years by name, but the source does not cover all of them: " + "; ".join(f"{a_} covers {b_}" for a_, b_ in partial) + ". "
                     f"Hulme's list in England 1551-1600 includes {trade} grants regulating trade. Every bar is the number in the sources, not the number of all privileges ever granted.")))
        add("terms", ("원로원 = 베네치아 공화국의 의결 기구(Senato). 2차 인용 = 다른 연구에 실린 수를 옮겨 온 값." if ko else
                      "Senate = the deliberative council of the Venetian Republic (Senato). Secondary figure = a number taken over from another study."))
        return intro, P

    if key == "a3":
        a = D["m_a3_1624"]
        w = a[a.grants.notna()].reset_index(drop=True)
        t = a[a.term_stated.notna()]
        _check(list(w.window) == ["1617-1623", "1625-1631", "1632-1638"] and (w.years == 7).all(), "a3 windows changed")
        r0 = w.iloc[0]
        dsh = lambda x: x.replace("-", "–")
        ovl = [(w.window[i], w.window[j]) for i in range(len(w)) for j in range(i + 1, len(w)) if max(w.ci_low[i], w.ci_low[j]) <= min(w.ci_high[i], w.ci_high[j])]
        ovl_ko = "·".join(f"{dsh(a)}년과 {dsh(b)}년" for a, b in ovl) or "없음"
        ovl_en = "; ".join(f"{dsh(a)} and {dsh(b)}" for a, b in ovl) or "none"
        intro = ("1624년 독점법 앞뒤로 7년씩, 한 해 평균 몇 건의 허여가 있었는지 견준 그림이다." if ko else
                 "Mean grants per year in the seven years before and after the 1624 Statute of Monopolies.")
        add("short", (f"1617–1623년 한 해 평균 {f1(w.per_year[0])}건, 1625–1631년 {f1(w.per_year[1])}건으로 비슷하고, 그다음 7년(1632–1638년)은 {f1(w.per_year[2])}건이다." if ko else
                      f"{f1(w.per_year[0])} a year in 1617–1623 and {f1(w.per_year[1])} in 1625–1631, about the same; the next seven years, 1632–1638, have {f1(w.per_year[2])}."))
        add("how", ("막대 하나가 7년 구간 하나다. 막대 길이는 그 7년의 허여 수를 7로 나눈 연평균(건/년)이다. 막대에 겹쳐 그은 가는 가로선은 95% 신뢰구간이다. 셋째 막대(1632–1638년)는 1625–1631년의 그다음 7년이다. 1624년 자체는 어느 막대에도 넣지 않았다." if ko else
                    "Each bar is one seven-year window; its length is the window's grants divided by 7 (mean grants per year). The thin horizontal line across each bar is the 95% confidence interval. The third bar (1632–1638) is the seven years after 1625–1631. 1624 itself is in no bar."))
        add("one", (f"1617–1623년 막대 {J(f1(r0.per_year))} 그 7년의 허여 {n(r0.grants)}건을 7로 나눈 값(건/년)이다. 가는 선은 연평균 {f1(r0.ci_low)}–{f1(r0.ci_high)}건/년이다." if ko else
                    f"The 1617–1623 bar, {f1(r0.per_year)}, is that window's {n(r0.grants)} grants divided by 7 (grants per year); its thin line runs from {f1(r0.ci_low)} to {f1(r0.ci_high)} grants per year."))
        add("mis", (f"앞뒤 수가 비슷하다는 것은 수를 견준 것일 뿐, 법이 허여 수를 바꾸었다거나 바꾸지 않았다는 증거가 아니다. 1617년 앞의 목록은 1603년에서 끊겨 더 긴 앞 기간과 견줄 수 없다. 가는 선이 서로 겹치는 막대끼리는(여기서는 {ovl_ko}) 이 정도 건수로는 그 차이가 우연인지 가리기 어렵다. 다만 겹침을 보는 것은 차이를 검정한 것이 아니다. "
                    f"아래 표에는 두 종류의 줄이 있다. 위 세 줄(연평균)이 막대이고, 아래 세 줄은 본문에 적힌 존속기간을 {', '.join(x.replace('-', '–') for x in t.window)}년으로 나누어 센 것이다. 그래서 존속기간 줄의 구간이 막대 구간과 다르고, 그 줄에 해당하지 않는 칸은 비어 있다(0이 아니다)." if ko else
                    f"Similar numbers before and after are a comparison of counts only; they are no evidence that the Act changed, or did not change, the number of grants. The list before 1617 stops in 1603, so no longer earlier period can be compared. Where the thin lines of two bars overlap (here {ovl_en}), counts this small cannot tell whether the difference is more than chance; looking at the overlap is not itself a test of the difference. "
                    f"The table below has two kinds of row: the first three (mean per year) are the bars; the last three count the terms written in the entries, split into {', '.join(x.replace('-', '–') for x in t.window)}. So the term rows use different windows from the bars, and cells that do not apply to a row are empty (not zero)."))
        add("terms", ("95% 신뢰구간(포아송 정확 구간) = 허여가 서로 상관없이 일정한 평균 빈도로 생긴다고 보는 포아송 분포를 가정하고, 그 7년의 건수로 연평균이 있을 법한 범위를 어림한 것. 같은 평균 빈도 아래에서 7년을 관측하고 이 구간을 계산하는 일을 거듭하면, 구간이 실제 연평균을 담는 비율이 95% 이상이 되도록 만든 것이다. "
                      "독점법 = 1624년 잉글랜드 의회의 Statute of Monopolies(21 Jac. I c. 3). 새 발명 특허를 14년 이하로 정했다." if ko else
                      "95% confidence interval (Poisson exact interval) = the range in which the mean per year plausibly lies, estimated from the window's count on the assumption that grants arise independently at a steady average rate (a Poisson distribution); if seven years were observed again and again at the same average rate, intervals made this way would contain the true mean at least 95 times in 100. "
                      "Statute of Monopolies = the 1624 Act of the English Parliament, 21 Jac. I c. 3, which limited patents for new inventions to 14 years or less."))
        return intro, P

    if key == "a4":
        a = D["m_a4_extensions"]
        tot_e, tot_n = int(a.extensions.sum()), int(a.entries.sum())
        mx = a.loc[a.extensions.idxmax()]
        first, last_ = a.iloc[0], a.iloc[-1]
        notext = int(a1.woodcroft_no_text.sum())
        absent = [d for d in range(int(a.decade.min()), int(a.decade.max()) + 1, 10) if d not in set(a.decade)]
        for d in absent:
            _check(a1[(a1.year >= d) & (a1.year < d + 10)].grants.sum() == 0, f"a4 decade {d} absent but has grants")
        intro = ("Woodcroft 목록에서 이미 있는 특허의 기간을 늘리거나 확인해 준 항목이 10년마다 몇 개인지 그린 그림이다." if ko else
                 "How many entries in Woodcroft's list lengthened or confirmed an existing patent, by decade.")
        add("short", (f"모두 합쳐 {tot_e}개로, 전체 항목 {n(tot_n)}개의 {pc(tot_e / tot_n, 2)}다. 가장 많은 10년은 {dec(mx.decade, lang)}({int(mx.extensions)}개)다." if ko else
                      f"{tot_e} in all, {pc(tot_e / tot_n, 2)} of the {n(tot_n)} entries. The largest decade is the {dec(mx.decade, lang)} ({int(mx.extensions)})."))
        add("how", ("선이 꺾이는 점 하나가 10년 하나다. 가로는 10년 구간의 첫 해(1830은 1830–1839년), 세로는 그 10년의 연장 항목 수(개)다. 지표 이름은 비율이지만 그림은 건수를 그렸다. 비율은 아래 표의 「비율」 열에 있다." if ko else
                    "Each corner of the line is one decade. Across: first year of the decade (1830 = 1830–1839); up: extension entries in that decade. The metric is named a share, but the chart draws counts; the share is in the table's 'Share' column."))
        add("one", (f"{dec(mx.decade, lang)} 값 {J(str(int(mx.extensions)))} 그 10년 Woodcroft 항목 {n(mx.entries)}개 가운데 {int(mx.extensions)}개가 연장 항목이라는 뜻이다({pc(mx.share, 2)})." if ko else
                    f"The {dec(mx.decade, lang)} value, {int(mx.extensions)}, means {int(mx.extensions)} of that decade's {n(mx.entries)} entries are extensions ({pc(mx.share, 2)})."))
        add("mis", (f"10년마다 항목 수가 크게 달라({dec(first.decade, lang)} {n(first.entries)}개, {dec(mx.decade, lang)} {n(mx.entries)}개) 건수가 늘었다고 비율이 늘었다는 뜻이 아니다. "
                    f"{'·'.join(dec(d, lang) for d in absent)}는 목록에 그 10년의 허여가 하나도 없어 0으로 그렸다(목록이 있는 10년의 0이다). 첫 10년({dec(first.decade, lang)})은 1617–1619년이다. 마지막 점({dec(last_.decade, lang)})에는 날인일이 1853년인 {len(W53)}항목도 들어 있다({late_ko}). "
                    f"OCR이 본문을 잃은 {notext}번호는 연장인지 알 수 없어 연장이 아닌 쪽에 두었다. 합계는 이 사이트의 분류에서 연장으로 잡힌 항목의 수이고, 연장과 새 허여의 경계가 애매한 항목도 있다." if ko else
                    f"The number of entries differs hugely from decade to decade ({n(first.entries)} in the {dec(first.decade, lang)}, {n(mx.entries)} in the {dec(mx.decade, lang)}), so a larger count is not a larger share. "
                    f"The {', '.join(dec(d, lang) for d in absent)} {'is' if len(absent) == 1 else 'are'} drawn at 0 because the list has no grant at all in {'that decade' if len(absent) == 1 else 'those decades'} (a zero where a list exists). The first decade ({dec(first.decade, lang)}) covers 1617–1619. The last point ({dec(last_.decade, lang)}) also holds the {len(W53)} entries sealed in 1853 ({late_en}). "
                    f"The {notext} numbers whose text the OCR lost cannot be told apart and are put with the non-extensions. The total is the number of entries this site's classification counts as extensions; some entries lie on the line between an extension and a new grant."))
        return intro, P

    # ------------------------------------------------------------------ B
    if key == "b1":
        b = D["m_b1_fields"]
        b = b[b.source == "Woodcroft"]
        per = list(dict.fromkeys(b.period))
        top = b[b.field != "other"].groupby("field")["count"].sum().sort_values(ascending=False).head(4).index.tolist()
        lastp, firstp = per[-1], per[0]
        lb = b[(b.period == lastp) & b.field.isin(top)].sort_values("share", ascending=False)
        r_last = lb.iloc[0]
        fb = b[(b.period == firstp) & (b.field != "other")].sort_values("share", ascending=False).iloc[0]
        rel = _rel_nums(ctx["rel"], "b1_fields")
        dash = lambda s: s.replace("-", "–")
        ln = lambda p: int(p[5:]) - int(p[:4]) + 1
        names = ", ".join(L(f) for f in top) if ko else ", ".join(f"'{L(f)}'" for f in top)
        intro = ("Woodcroft 목록의 허여를 발명 명칭으로 분야를 나눈 뒤, 구간마다 큰 네 분야가 차지한 비율을 그린 그림이다." if ko else
                 "Woodcroft's grants divided into fields by the title of the invention: the share of the four largest fields in each period.")
        add("short", (f"{dash(lastp)}년에 네 분야 가운데 몫이 가장 큰 것은 {L(r_last.field)}({pc(r_last.share)})다." if ko else
                      f"In {dash(lastp)} the largest of the four is '{L(r_last.field)}' ({pc(r_last.share)})."))
        notext = int(a1.woodcroft_no_text.sum())
        add("how", (f"선 하나가 분야 하나이고, 선 끝에 분야 이름이 있다. 가로는 Woodcroft 목록을 나눈 {len(per)}구간, 세로는 그 구간에서 본문이 읽힌 허여 가운데 그 분야로 분류된 것의 비율이다(분모에는 「기타」가 들어 있고, OCR이 본문을 잃은 {notext}번호는 빠진다). 분야는 명칭에 단어 규칙을 차례로 적용해 처음 맞는 것으로 정했다. 네 분야({names})는 「기타」를 빼고 1617–1852년 전체 건수가 많은 순으로 골랐다. 모든 분야는 아래 표에 있다." if ko else
                    f"Each line is one field, named at its end. Across: the {len(per)} periods into which Woodcroft's list is divided; up: the share of the period's grants with readable text that were classed in that field (the total includes 'other'; the {notext} numbers whose text the OCR lost are left out). A field is the first word rule, applied in order, that matches the title. The four ({names}) are the largest by count over 1617–1852 once 'other' is set aside; every field is in the table below."))
        add("one", (f"{dash(lastp)}년 {L(r_last.field)} {pc(r_last.share)}는 그 구간 허여 {n(r_last.n)}건 가운데 {n(r_last['count'])}건이 그 분야로 분류되었다는 뜻이다." if ko else
                    f"The share of '{L(r_last.field)}' in {dash(lastp)}, {pc(r_last.share)}, means {n(r_last['count'])} of that period's {n(r_last.n)} grants were classed in that field."))
        add("mis", (f"구간 길이가 서로 달라({dash(firstp)}년은 {ln(firstp)}년, {dash(lastp)}년은 이름으로 {ln(lastp)}년이고 1852년까지만 센다) 선의 기울기를 구간끼리 견줄 수 없다. 그림에 없는 분야도 큰 몫일 수 있다 — {dash(firstp)}년에 가장 큰 분야는 {L(fb.field)}({pc(fb.share)})다. "
                    f"비율이 줄었다고 그 분야의 허여 수가 줄었다는 뜻은 아니다(구간마다 전체 허여 수가 다르다 — 수는 표). 분야는 명칭의 단어 규칙으로 정한 것이라, 독립 코더가 본문을 읽고 매긴 분야와 표본 {rel['n']}건 가운데 {rel['k']}건({rel['simple']})이 같고, 분야 비중으로 가중하면 {rel['weighted']}다. 몇 %포인트의 차이에는 무게를 두지 않는다." if ko else
                    f"The periods differ in length ({dash(firstp)} is {ln(firstp)} years, {dash(lastp)} {ln(lastp)} by name, counted to 1852 only), so slopes cannot be compared from one period to the next. A field not drawn can still be large: in {dash(firstp)} the largest field is '{L(fb.field)}' ({pc(fb.share)}). "
                    f"A falling share does not mean fewer grants in that field (the total differs by period; counts are in the table). Fields are set by word rules on the title; they match the field an independent coder gave after reading the entry in {rel['k']} of {rel['n']} sampled grants ({rel['simple']}), {rel['weighted']} when weighted by field size. Differences of a few percentage points carry little weight."))
        add("terms", ("분야 사전 = 명칭의 낱말로 분야를 정하는 규칙 목록. 「기타」 = 어느 규칙에도 걸리지 않은 허여. 가중 정밀도 = 사전이 어느 분야로 넣은 표본 가운데 독립 코더도 같은 분야로 넣은 비율을 분야마다 구하고, 사전이 분류한 전체 허여에서 그 분야가 차지하는 몫으로 가중해 더한 값(방법 면)." if ko else
                      "Field dictionary = the list of word rules that assigns a field from the title. 'Other' = a grant no rule matched. Weighted precision = for each field, the share of the sampled grants the dictionary put in it that the independent coder put in the same field, weighted by that field's share of all grants as the dictionary classes them, and added up (method page)."))
        return intro, P

    if key in ("b2_h", "b2_o"):
        b = D["m_b2_hhi"]
        nf = ctx["N_FIELDS"]
        gaps = [d for d in range(int(b.decade.min()), int(b.decade.max()) + 1, 10) if d not in set(b.decade.astype(int))]
        gap_t = ("·" if ko else ", ").join(dec(d, lang) for d in gaps)
        first, last_ = b.iloc[0], b.iloc[-1]
        lg = int(((W53.kind == "grant") & W53.parsed.astype(bool)).sum())
        notext = int(a1.woodcroft_no_text.sum())
        edge0 = (f"첫 점({dec(first.decade, lang)})은 1617–1619년({int(first.n)}건)이다. 마지막 점({dec(last_.decade, lang)})에는 날인일이 1853년인 허여 {lg}건도 들어 있다. " if ko else
                 f"The first point ({dec(first.decade, lang)}) covers 1617–1619 ({int(first.n)} grants). The last ({dec(last_.decade, lang)}) also holds the {lg} grants sealed in 1853. ")
        if key == "b2_h":
            edge = edge0 + (f"HHI는 본문이 읽힌 허여 가운데 {nf}분야 중 하나로 분류된 것만으로 계산한다(「기타」와 OCR이 본문을 잃은 {notext}번호는 빠진다 — 예: {dec(first.decade, lang)}는 {int(first.n)}건 가운데 {int(first.classified)}건)." if ko else
                            f"HHI is computed only on the grants with readable text that were classed in one of the {nf} fields ('other' and the {notext} numbers whose text the OCR lost are left out; in the {dec(first.decade, lang)}, for example, {int(first.classified)} of {int(first.n)}).")
        else:
            edge = edge0 + (f"분모는 본문이 읽힌 허여다(OCR이 본문을 잃은 {notext}번호는 빠진다)." if ko else
                            f"The total is the grants with readable text (the {notext} numbers whose text the OCR lost are left out).")
        if key == "b2_h":
            hmax = b.loc[b.hhi.idxmax()]
            late = b[b.decade >= 1770]
            hi = b[b.hhi > 0.2]
            ex = b[b.decade == 1840].iloc[0]
            intro = ("10년마다 허여가 몇 분야에 몰렸는지를 지수 하나(HHI)로 그린 그림이다." if ko else
                     "How far each decade's grants concentrate in a few fields, as one index (HHI).")
            add("short", (f"1770년대부터는 {late.hhi.min():.3f}–{late.hhi.max():.3f} 사이에 머문다. 0.2를 넘는 값은 {('·'.join(f'{dec(r.decade, lang)}({int(r.classified)}건)' for r in hi.itertuples()))}처럼 분류된 허여가 적은 10년뿐이다." if ko else
                          f"From the 1770s it stays between {late.hhi.min():.3f} and {late.hhi.max():.3f}. Values above 0.2 come only from decades with few classified grants: {', '.join(f'the {dec(r.decade, lang)} ({int(r.classified)})' for r in hi.itertuples())}."))
            add("how", (f"선이 꺾이는 점 하나가 10년 하나다. 가로는 10년 구간의 첫 해, 세로는 HHI다. HHI는 「기타」를 뺀 분류된 허여에서 분야마다의 몫을 제곱해 더한 값으로, 한 분야가 다 차지하면 1이고 {nf}분야에 똑같이 나뉘면 가장 작은 값 {1 / nf:.3f}(점선)이다. 선이 위에 있을수록 허여가 몇 분야에 몰려 있다. {gap_t}는 허여가 없어 선을 끊었다." if ko else
                        f"Each corner of the line is one decade. Across: first year of the decade; up: HHI, the sum of the squared shares of the fields among the classified grants ('other' excluded). It is 1 if one field takes everything and at its smallest, {1 / nf:.3f} (dotted line), if the grants are split equally over {nf} fields. The higher the line, the more the grants concentrate in a few fields. The line breaks at the {gap_t}, which have no grants."))
            add("one", (f"{dec(ex.decade, lang)} 값 {J(f'{ex.hhi:.3f}')} 그 10년 분류된 허여 {n(ex.classified)}건의 분야 몫을 제곱해 더한 값이다. 반올림하기 전 값으로 1을 나누면 약 {1 / ex.hhi:.1f}이다 — 허여가 약 {1 / ex.hhi:.0f}분야에 똑같이 나뉜 것과 같은 정도의 몰림이라는 뜻이다." if ko else
                        f"The {dec(ex.decade, lang)} value, {ex.hhi:.3f}, is the sum of the squared field shares of that decade's {n(ex.classified)} classified grants. One divided by the unrounded value is about {1 / ex.hhi:.1f}: as concentrated as if the grants were split equally over about {1 / ex.hhi:.0f} fields."))
            add("mis", (f"가장 높은 값은 {dec(hmax.decade, lang)}의 {hmax.hhi:.3f}인데, 그 10년에 분야를 가른 허여는 {int(hmax.classified)}건뿐이다 — 허여가 적은 10년의 값은 크게 흔들린다. HHI는 어느 분야에 몰렸는지는 말하지 않는다(아래 표의 「가장 큰 분야」). 「기타」로 빠진 허여는 계산에 들어가지 않는다(아래 그림). {edge}" if ko else
                        f"The highest value, {hmax.hhi:.3f} in the {dec(hmax.decade, lang)}, rests on only {int(hmax.classified)} classified grants; values for decades with few grants swing widely. HHI does not say which field the grants concentrate in (the table's 'Largest field'). Grants classed 'other' are not in the calculation (next chart). {edge}"))
            add("terms", ("HHI(허핀달 지수, Herfindahl–Hirschman index) = 몫을 제곱해 더한 집중도 지수. 시장 점유율의 집중을 잴 때 흔히 쓴다." if ko else
                          "HHI (Herfindahl–Hirschman index) = a concentration index: the sum of the squared shares. It is commonly used for market shares."))
        else:
            omax = b.loc[b.other_share.idxmax()]
            late = b[b.decade >= 1810]
            rel = _rel_nums(ctx["rel"], "b2_hhi")
            intro = ("10년마다 허여 가운데 분야를 정하지 못한 「기타」가 얼마나 되는지 그린 그림이다." if ko else
                     "The share of each decade's grants that could not be put in a field ('other').")
            add("short", (f"1810년대부터는 {pc(late.other_share.min(), 0)}–{pc(late.other_share.max(), 0)} 사이다. 가장 높은 10년은 {dec(omax.decade, lang)}({pc(omax.other_share, 0)})다." if ko else
                          f"From the 1810s it is between {pc(late.other_share.min(), 0)} and {pc(late.other_share.max(), 0)}. The highest decade is the {dec(omax.decade, lang)} ({pc(omax.other_share, 0)})."))
            add("how", (f"가로는 10년 구간의 첫 해, 세로는 그 10년 본문이 읽힌 허여 가운데 {nf}분야 어디에도 넣지 못한 허여의 비율이다. 위의 HHI와 뜻도 단위도 다른 값이라 따로 그렸다. {gap_t}는 허여가 없어 선을 끊었다." if ko else
                        f"Across: first year of the decade; up: the share of that decade's grants with readable text that fit none of the {nf} fields. It differs from HHI above in meaning and in unit, so it has a chart of its own. The line breaks at the {gap_t}, which have no grants."))
            add("one", (f"{dec(omax.decade, lang)} {pc(omax.other_share)}는 그 10년 허여 {n(omax.n)}건 가운데 {n(omax.n - omax.classified)}건이 「기타」라는 뜻이다. 그래서 그 10년의 HHI는 나머지 {n(omax.classified)}건으로 계산했다." if ko else
                        f"The {dec(omax.decade, lang)} value, {pc(omax.other_share)}, means {n(omax.n - omax.classified)} of that decade's {n(omax.n)} grants are 'other', so its HHI rests on the other {n(omax.classified)}."))
            add("mis", (f"「기타」가 많다고 새 분야의 발명이 많았다는 뜻이 아니다. 단어 규칙이 명칭을 알아보지 못한 몫이다. 규칙이 「기타」로 둔 표본 {rel['on']}건 가운데 독립 코더도 「기타」로 본 것은 {rel['ok']}건이다(신뢰도 카드). {edge}" if ko else
                        f"A large 'other' share does not mean many inventions in new fields; it is the part the word rules did not recognise. Of {rel['on']} sampled grants the rules left as 'other', the independent coder also put {rel['ok']} in 'other' (reliability card). {edge}"))
        return intro, P

    if key == "b3":
        b = D["m_b3_venice_sectors"]
        ve = D["m_a2_periods"]
        tot = int(b["count"].sum())
        mills = b[b.our_field == "mills"]
        _check(mills.sector_berveglieri.str.startswith("Mills").all() and not b[b.our_field != "mills"].sector_berveglieri.str.startswith("Mills").any(), "b3 mills sectors")
        rest = b[(b.our_field != "mills")].sort_values("count", ascending=False).head(3)
        vsum = int(ve[(ve.jurisdiction == "VE") & (ve.kind == "invention") & ve.period.isin(["1474-1500", "1501-1550"])]["count"].sum())
        nm = ctx["SECTOR"]
        nm_ = (lambda s: nm.get(s, s)) if ko else (lambda s: s)
        intro = ("베네치아 원로원이 1474–1550년에 내준 발명 특허를 Comino 등이 분야별로 센 표를 막대로 옮긴 그림이다." if ko else
                 "Venetian Senate patents of 1474–1550 by sector, as counted by Comino et al., drawn as bars.")
        add("short", (f"합계 {tot}건 가운데 원문에서 Mills로 시작하는 {len(mills)}갈래(이 사이트 분야로는 {L('mills')})가 {int(mills['count'].sum())}건({pc(mills['count'].sum() / tot, 0)})이다. 그다음은 " + ", ".join(f"{nm_(r.sector_berveglieri)} {int(r['count'])}건" for _, r in rest.iterrows()) + "이다." if ko else
                      f"Of {tot} in all, the {len(mills)} sectors whose names begin with Mills (this site's field '{L('mills')}') take {int(mills['count'].sum())} ({pc(mills['count'].sum() / tot, 0)}). Next come " + ", ".join(f"{r.sector_berveglieri} ({int(r['count'])})" for _, r in rest.iterrows()) + "."))
        add("how", ("막대 하나가 원문 표(Comino 등 표 A1)의 분야 하나다. 막대가 길수록 그 분야의 특허가 많다. 괄호 안이 원문의 영어 분야 이름이고, 한국어 이름은 이 사이트가 붙였다. 막대는 크기순이 아니고 표의 순서대로다. 색은 한 가지라 뜻이 없다." if ko else
                    "Each bar is one sector of the source's table (Comino et al., Table A1); the longer the bar, the more patents in it. The bars follow the order of the table, not size. There is one colour only; it carries no meaning."))
        add("one", (f"「방아(곡물)」 {J(str(int(b[b.sector_berveglieri == 'Mills — cereals']['count'].iloc[0])))} 곡물을 빻는 방아에 관한 특허가 {int(b[b.sector_berveglieri == 'Mills — cereals']['count'].iloc[0])}건이라는 뜻이다." if ko else
                    f"'Mills — cereals', {int(b[b.sector_berveglieri == 'Mills — cereals']['count'].iloc[0])}, means {int(b[b.sector_berveglieri == 'Mills — cereals']['count'].iloc[0])} patents for mills that grind grain."))
        same = vsum == tot
        add("mis", (("이 사이트가 세지 않은 2차 인용이다. " + (f"합계 {tot}건은 같은 문헌이 적은 1474–1500년과 1501–1550년 원로원 특허 수의 합({vsum}건)과 같다. " if same else f"합계 {tot}건은 같은 문헌의 1474–1550년 기간 건수 합({vsum}건)과 다르다. ") +
                     "아래 표의 「이 사이트 분야」는 이 사이트가 원문 분야를 잉글랜드 분야 사전에 맞춰 본 것이라, 잉글랜드 그림의 분야와 견줄 때는 대응이 우리 판단임을 감안한다.") if ko else
                    ("This is a secondary figure, not counted here. " + (f"The total, {tot}, equals the sum of the same source's Senate patents for 1474–1500 and 1501–1550 ({vsum}). " if same else f"The total, {tot}, differs from the same source's count for 1474–1550 ({vsum}). ") +
                     "The table's 'Field here' is this site's matching of the source's sectors to the English field dictionary; the match is our judgement, which matters when comparing with the English charts.")))
        add("terms", ("원로원 = 베네치아 공화국의 의결 기구(Senato). 아르세날레 = 베네치아의 국영 조선소(Arsenale)." if ko else
                      "Senate = the deliberative council of the Venetian Republic (Senato). Arsenal = the state shipyard of Venice (Arsenale)."))
        return intro, P

    # ------------------------------------------------------------------ C
    if key == "c1":
        c = D["m_c1_foreign_gb"]
        c = c[c.decade >= 1700]
        pre = c[c.decade <= 1800]
        ex = c[c.decade == 1840].iloc[0]
        lst = c.iloc[-1]
        ov = int(ex.communication + ex.foreign_address - ex.either)
        ovd = int(((c.communication + c.foreign_address - c.either) > 0).sum())
        lg = int(((W53.kind == "grant") & W53.parsed.astype(bool)).sum())
        _check(ov >= 0, "c1 overlap negative")
        intro = ("잉글랜드 허여 가운데 외국과 이어진 것이 10년마다 얼마나 되는지, 1700년부터 세 가지 기준으로 그린 그림이다." if ko else
                 "The share of English grants with a link abroad, by decade from 1700, by three measures.")
        add("short", (f"「둘 중 하나」는 1700년대부터 1800년대까지 10년마다 {pc(pre.either_share.max())} 이하이고, {dec(ex.decade, lang)} {pc(ex.either_share)}, {dec(lst.decade, lang)} {pc(lst.either_share)}다." if ko else
                      f"'Either' is at most {pc(pre.either_share.max())} in every decade from the 1700s to the 1800s, {pc(ex.either_share)} in the {dec(ex.decade, lang)} and {pc(lst.either_share)} in the {dec(lst.decade, lang)}."))
        add("how", ("선이 셋이다. 「communication」은 목록 본문에 해외에서 전해진 발명이라고 적힌 허여, 「해외 주소」는 목록에 적힌 수혜자 주소가 브리튼 제도 밖인 허여, 「둘 중 하나」는 둘 가운데 하나라도 해당하는 허여의 비율이다. 가로는 10년 구간의 첫 해, 세로는 그 10년 본문이 읽힌 허여 가운데 비율이다." if ko else
                    "Three lines: 'Communication', grants whose text says the invention was communicated from abroad; 'Address abroad', grants whose recorded address for the grantee is outside the British Isles; 'Either', grants with one or both. Across: first year of the decade; up: share of that decade's grants with readable text."))
        add("one", (f"{dec(ex.decade, lang)} 「둘 중 하나」 {pc(ex.either_share)}는 허여 {n(ex.n)}건 가운데 {n(ex.either)}건이다. 「communication」 {n(ex.communication)}건과 「해외 주소」 {n(ex.foreign_address)}건을 더하면 {n(ex.communication + ex.foreign_address)}건인데, 둘 다 해당하는 {ov}건이 겹쳐 {n(ex.either)}건이 된다." if ko else
                    f"'Either' in the {dec(ex.decade, lang)}, {pc(ex.either_share)}, is {n(ex.either)} of {n(ex.n)} grants. 'Communication' ({n(ex.communication)}) plus 'Address abroad' ({n(ex.foreign_address)}) makes {n(ex.communication + ex.foreign_address)}, but {ov} grants are both, so 'Either' is {n(ex.either)}."))
        add("mis", (f"국적이나 실제 거주를 센 것이 아니다(목록에는 국적이 없다). 목록에 적힌 문구와 주소로만 셌으므로, 그런 표지 없이 외국과 이어진 허여는 빠진다. 「둘 중 하나」는 두 가지에 다 해당하는 허여가 있는 10년에는 두 선의 합보다 작고(그림의 {len(c)}구간 가운데 {ovd}구간), 없으면 합과 같다. 마지막 점({dec(lst.decade, lang)})에는 날인일이 1853년인 허여 {lg}건도 들어 있다. 1700년 전 잉글랜드 값은 아래 표에, Hulme(1561–1603)과 네덜란드 값은 데이터 면의 CSV에 있다." if ko else
                    f"This is neither nationality nor actual residence (the list gives no nationality). It is counted only from the wording and addresses written in the list, so grants linked abroad without such a mark are missed. 'Either' is smaller than the two lines added in decades with grants that are both ({ovd} of the {len(c)} decades drawn) and equal to it where there are none. The last point ({dec(lst.decade, lang)}) also holds the {lg} grants sealed in 1853. English values before 1700 are in the table below; Hulme (1561–1603) and the Dutch values are in the CSV files on the data page."))
        add("terms", ("communication = 목록 본문에 해외에서 전해진 발명이라고 적힌 허여. 브리튼 제도 = 그레이트브리튼섬과 아일랜드섬, 그 둘레의 섬들." if ko else
                      "Communication = a grant whose text says the invention was communicated from abroad. British Isles = Great Britain, Ireland and the islands around them."))
        return intro, P

    if key == "c2":
        c = D["m_c2_cogrant"]
        g = D["m_c1_foreign_gb"].set_index("decade").n
        early = c[c.decade <= 1640]
        late = c[c.decade >= 1700]
        lo, hi_ = late.loc[late.co_share.idxmin()], late.loc[late.co_share.idxmax()]
        ex = c[c.decade == 1630].iloc[0]
        small = c.loc[c.n.idxmin()]
        gp = W[W.parsed.astype(bool) & (W.kind == "grant")]
        drop = int(gp.n_grantees.isna().sum())
        _check(drop == int(gp[gp.n_grantees.isna()].margin_names.isna().sum()), "c2: grants without a grantee count do not all lack margin names")
        _check(drop == int((g - c.set_index("decade").n.reindex(g.index)).sum()), "c2: dropped grants do not match the two tables")
        lg = int(((W53.kind == "grant") & W53.parsed.astype(bool) & W53.n_grantees.notna()).sum())
        intro = ("잉글랜드 허여 가운데 둘 이상이 함께 받은 것이 10년마다 얼마나 되는지 그린 그림이다." if ko else
                 "The share of English grants made to more than one person, by decade.")
        add("short", (f"1617–1649년에는 {pc(early.co_share.min(), 0)}–{pc(early.co_share.max(), 0)}이고, 1700년대부터는 {pc(lo.co_share)}({dec(lo.decade, lang)})에서 {pc(hi_.co_share)}({dec(hi_.decade, lang)}) 사이를 오간다." if ko else
                      f"{pc(early.co_share.min(), 0)}–{pc(early.co_share.max(), 0)} in 1617–1649; from the 1700s it moves between {pc(lo.co_share)} ({dec(lo.decade, lang)}) and {pc(hi_.co_share)} ({dec(hi_.decade, lang)})."))
        add("how", ("선이 꺾이는 점 하나가 10년 하나다. 가로는 10년 구간의 첫 해, 세로는 그 10년 허여 가운데 수혜자가 둘 이상인 허여의 비율이다. 수혜자 수는 Woodcroft 목록 여백에 찍힌 성(姓)의 수로 셌다. 1650년대는 허여가 없어 선을 끊었다." if ko else
                    "Each corner of the line is one decade. Across: first year of the decade; up: share of that decade's grants with two or more grantees, counted from the surnames printed in the margin of Woodcroft's list. The line breaks at the 1650s, which have no grants."))
        add("one", (f"{dec(ex.decade, lang)} {pc(ex.co_share)}는 허여 {n(ex.n)}건 가운데 {n(ex.co)}건에 여백의 성이 둘 이상 찍혔다는 뜻이다." if ko else
                    f"The {dec(ex.decade, lang)} value, {pc(ex.co_share)}, means {n(ex.co)} of {n(ex.n)} grants have two or more surnames in the margin."))
        add("mis", (f"{dec(small.decade, lang)} {pc(small.co_share, 0)}는 허여 {int(small.n)}건 가운데 {int(small.co)}건이다 — 허여가 적은 10년의 값은 크게 흔들린다. 분모는 본문이 읽히고 여백의 성이 하나라도 잡힌 허여다 — 여백의 성이 하나도 잡히지 않은 허여 {drop}건(모든 10년을 합친 수)은 뺐다. 여백의 성이 OCR에서 빠지거나 둘로 갈리면 값이 흔들린다. 첫 점(1610년대)은 1617–1619년이고, 마지막 점(1850년대)에는 날인일이 1853년인 허여 {lg}건도 들어 있다." if ko else
                    f"The {dec(small.decade, lang)} value, {pc(small.co_share, 0)}, is {int(small.co)} of {int(small.n)} grants: values for decades with few grants swing widely. The total is the grants with readable text and at least one surname caught in the margin; the {drop} grants with none caught (all decades together) are left out. A surname dropped by the OCR, or split in two, moves the value. The first point (1610s) covers 1617–1619; the last (1850s) also holds the {lg} grants sealed in 1853."))
        return intro, P

    # ------------------------------------------------------------------ D
    if key == "d1":
        d = D["m_d1_terms"]
        d = d[d.n_stated > 0].reset_index(drop=True)
        lab = lambda s: ctx["source_label"](s, lang)
        hu = d.iloc[0]
        _check(hu.source.startswith("GB Hulme") and int(hu.n_stated) % 2 == 1, "d1 first row is not Hulme with an odd count")
        flat = d[(d.p25 == d.p75)]
        w20 = W[W.year >= 1820]
        t20 = w20[w20.term_years.notna()]
        t20x = int((t20.kind == "extension").sum())
        ext_t = {lab(r.source): int(((W.kind == "extension") & W.term_years.notna() & W.year.between(int(r.source[-9:-5]), int(r.source[-4:]))).sum()) for _, r in d.iterrows() if "Woodcroft" in r.source}
        ext_t = {k: v for k, v in ext_t.items() if v}
        intro = ("허여 문서와 목록 항목에 적힌 존속기간을 자료·시기마다 모아, 한가운데 값과 가운데 절반의 범위를 그린 그림이다." if ko else
                 "The terms written in the grants and list entries, by source and period: the middle value and the range of the middle half.")
        add("short", (("가운데 값은 " + ", ".join(f"{lab(r.source)} {int(r['median'])}년" for _, r in d.iterrows()) + "이다.") if ko else
                      ("Middle values: " + "; ".join(f"{lab(r.source)} {int(r['median'])} years" for _, r in d.iterrows()) + ".")))
        add("how", ("막대 하나가 자료·시기 하나다. 막대 길이는 적힌 기간의 중앙값(년)이다. 막대에 겹쳐 그은 가는 가로선은 사분위 범위로, 값의 가운데 절반이 이 안에 든다. 가는 선의 양 끝 값은 표의 「1사분위」「3사분위」 열에 있다. 가는 선이 보이지 않는 막대는 가운데 절반이 모두 한 값이다(" + ", ".join(lab(s) for s in flat.source) + ") — 선이 빠진 것이 아니다." if ko else
                    "Each bar is one source and period; its length is the median written term (years). The thin horizontal line across it is the interquartile range, which holds the middle half of the values. The ends of the thin lines are in the table's 'Lower quartile' and 'Upper quartile' columns. A bar with no visible thin line has its whole middle half at one value (" + "; ".join(lab(s) for s in flat.source) + "); the line is not missing."))
        add("one", (f"{lab(hu.source)} 막대 {J(str(int(hu['median'])))} 기간이 적힌 {int(hu.n_stated)}건을 짧은 것부터 늘어놓았을 때 한가운데({(int(hu.n_stated) + 1) // 2}번째) 값이 {int(hu['median'])}년이라는 뜻이다. 가는 선 {int(hu.p25)}–{int(hu.p75)}년 안에 가운데 절반이 든다." if ko else
                    f"The {lab(hu.source)} bar, {int(hu['median'])}, means that with its {int(hu.n_stated)} written terms in order from shortest, the middle one (the {(int(hu.n_stated) + 1) // 2}th) is {int(hu['median'])} years; the middle half lies within {int(hu.p25)}–{int(hu.p75)} years."))
        big = d.loc[d.n_stated.idxmax()]
        _check(big["min"] == big["max"], "d1 largest source does not have a single value")
        add("mis", (f"기간이 적힌 것만 셌고, 막대마다 건수가 크게 다르다({n(d.n_stated.min())}–{n(d.n_stated.max())}건 — 표의 「기간 적힘」). Woodcroft 집계는 1819년에서 끝난다. 1820년부터의 항목은 대부분 기간을 적지 않아({n(len(w20))}항목 가운데 기간이 적힌 것 {len(t20)}개, 그 가운데 {t20x}개는 연장 항목) 막대와 표의 줄을 두지 않았다. 법정 기간 14년을 가정해 채우지 않았다. {lab(big.source)}는 {n(big.n_stated)}건 모두 {int(big['min'])}년이다. 가운데 절반 밖의 값도 있다 — 표의 최소·최대와 「값별 건수」. Woodcroft 막대는 기간이 적힌 항목을 셌고, 이 사이트의 분류로 기간 연장인 항목도 들어 있다(" + ", ".join(f"{k} {v}개" for k, v in ext_t.items()) + ")." if ko else
                    f"Only written terms are counted, and the counts differ greatly by bar ({n(d.n_stated.min())}–{n(d.n_stated.max())}; the table's 'Terms stated'). The Woodcroft count ends in 1819. Entries from 1820 on mostly do not state a term ({len(t20)} of {n(len(w20))} do, {t20x} of them extensions), so there is no bar and no row in the table; the statutory 14 years was not assumed. In {lab(big.source)} all {n(big.n_stated)} are {int(big['min'])} years. Values outside the middle half exist too: see the table's minimum, maximum and counts by value. The Woodcroft bars count entries with a written term, including those this site's classification counts as extensions (" + "; ".join(f"{k}: {v}" for k, v in ext_t.items()) + ")."))
        add("terms", ("중앙값 = 값을 크기순으로 늘어놓았을 때 한가운데 값(개수가 짝수면 가운데 두 값의 평균). 사분위 범위 = 아래에서 4분의 1 되는 값(1사분위)부터 4분의 3 되는 값(3사분위)까지. 가운데 절반의 경계를 가리키는 값이라, 같은 값이 많으면 그 안에 절반보다 많은 값이 들 수 있다." if ko else
                      "Median = the middle value when the values are put in order (with an even count, the average of the middle two). Interquartile range = from the value a quarter of the way up (lower quartile) to the value three quarters of the way up (upper quartile); these mark the edges of the middle half, so with many equal values more than half can fall inside."))
        return intro, P

    if key == "d2":
        d = D["m_d2_term_shift"]
        pre, post = d[d.year < 1624], d[d.year > 1624]
        other = int((d.stated - d.le14 - d.eq21).sum())
        zero = [y for y in range(int(d.year.min()), int(d.year.max()) + 1) if y not in set(d.year)]
        for y in zero:
            _check(a1.set_index("year").grants.get(y, -1) == 0, f"d2 year {y} absent but has grants")
        ex = pre.loc[pre.eq21.idxmax()]
        last21 = int(post[post.eq21 > 0].year.max())
        mxn = int(d[["le14", "eq21"]].max().max())
        n_ext = int(a1[(a1.year >= 1617) & (a1.year <= 1700)].woodcroft_extensions.sum())
        ext_y = a1[(a1.year >= 1617) & (a1.year <= 1700) & (a1.woodcroft_extensions > 0)].year.tolist()
        one0 = d[((d.le14 == 0) != (d.eq21 == 0))].shape[0]
        intro = ("1617–1700년 해마다, 본문에 적힌 첫 기간이 21년인 Woodcroft 항목과 14년 이하인 항목이 몇 개인지 두 선으로 그린 그림이다." if ko else
                 "For each year 1617–1700, how many entries in Woodcroft's list have a first written term of 21 years and how many of 14 years or less, as two lines.")
        add("short", (f"1617–1623년에는 기간이 적힌 {n(pre.stated.sum())}항목 가운데 21년이 {n(pre.eq21.sum())}항목, 1625–1700년에는 {n(post.stated.sum())}항목 가운데 14년 이하가 {n(post.le14.sum())}항목이다." if ko else
                      f"In 1617–1623, {n(pre.eq21.sum())} of {n(pre.stated.sum())} entries with a written term have 21 years; in 1625–1700, {n(post.le14.sum())} of {n(post.stated.sum())} have 14 years or less."))
        add("how", (f"가로는 연도, 세로는 그해 항목 수다. 새 허여 항목에 더해 기간이 적힌 기간 연장 항목도 센다(1617–1700년에 연장 항목은 {n_ext}개, {yr_list(ext_y, lang)}). 선 둘은 「21년」과 「14년 이하」다. 좁은 음영은 독점법이 나온 1624년이다. 둘 다 아닌 기간(15–20년, 22년 이상)은 그리지 않았다 — 1617–1700년에 {other}항목이고, 표의 「기간 적힘」에서 두 열을 뺀 수다." if ko else
                    f"Across: year; up: entries that year, new grants and also extension entries with a written term ({n_ext} extension {'entry' if n_ext == 1 else 'entries'} in 1617–1700, in {yr_list(ext_y, lang)}). The two lines are '21 years' and '≤14 years'. The narrow band is 1624, the year of the Statute of Monopolies. Other terms (15–20 years, over 21) are not drawn: {other} in 1617–1700, the table's 'Terms stated' less the two columns."))
        add("one", (f"{int(ex.year)}년 「21년」 {J(str(int(ex.eq21)))} 그해 기간이 적힌 항목 {int(ex.stated)}개 가운데 {int(ex.eq21)}개의 첫 기간이 21년이라는 뜻이다." if ko else
                    f"'21 years' in {int(ex.year)}, {int(ex.eq21)}, means {int(ex.eq21)} of that year's {int(ex.stated)} entries with a written term have a first term of 21 years."))
        add("mis", (f"두 선이 함께 0에 닿는 {yr_list(zero, lang)}은 그해 목록에 항목이 없는 해다(0이고, 목록이 빠진 해가 아니다). 한 선만 0인 해({one0}해)는 그 기간의 항목이 그해 없다는 뜻일 뿐이다. 한 해 건수가 몇 건뿐이라(한 선의 한 해 최대 {mxn}건) 선이 크게 출렁인다. 음영 「1624」는 해를 표시할 뿐이다. 1624년 앞에도 14년 이하가 {n(pre.le14.sum())}항목 있고, 뒤에도 21년이 {n(post.eq21.sum())}항목 남는다(마지막은 {last21}년). 이 표는 기록에 적힌 기간을 셀 뿐, 법이 기간을 바꾸었다는 증거가 아니다." if ko else
                    f"Where both lines touch 0 — {yr_list(zero, lang)} — the list has no entry that year (zero, not a missing list). Where only one line is at 0 ({one0} years), there is just no entry with that term that year. With only a few entries a year (at most {mxn} on one line in one year) the lines swing widely. The band '1624' marks the year only. Before 1624 there are already {n(pre.le14.sum())} terms of 14 years or less, and after it {n(post.eq21.sum())} of 21 years remain (the last in {last21}). The table counts the terms written in the record; it is no evidence that the Act changed them."))
        add("terms", ("첫 기간 = 한 항목에 기간이 여럿 적혔을 때(광산권·아일랜드에 대한 기간 등) 맨 앞에 적힌 기간." if ko else
                      "First term = where an entry gives several terms (for mines, for Ireland and so on), the one written first."))
        return intro, P

    if key == "d3":
        d = D["m_d3_clauses"]
        pmax = d.loc[d.proviso_share.idxmax()]
        early = d[d.decade <= 1640]
        mid = d[(d.decade >= 1660) & (d.decade <= 1670)]
        later = d[d.decade >= 1680]
        rent_late = int(later.rent.sum())
        small = d.loc[d.n.idxmin()]
        intro = ("1617–1759년 Woodcroft 항목 요약에 지대 문구와 단서 문구가 든 항목의 비율을 10년마다 그린 그림이다." if ko else
                 "The share of Woodcroft's entries, 1617–1759, whose summary mentions a rent or a proviso, by decade.")
        add("short", (f"지대 문구는 1640년대까지 {pc(early.rent_share.min(), 0)}–{pc(early.rent_share.max(), 0)}, 1660·1670년대 {pc(mid.rent_share.min(), 0)}–{pc(mid.rent_share.max(), 0)}이고, 1680년대부터는 {rent_late}건뿐이다. 단서 문구는 {dec(pmax.decade, lang)}에 {pc(pmax.proviso_share)}로 가장 높다." if ko else
                      f"Rent is mentioned in {pc(early.rent_share.min(), 0)}–{pc(early.rent_share.max(), 0)} of entries up to the 1640s and {pc(mid.rent_share.min(), 0)}–{pc(mid.rent_share.max(), 0)} in the 1660s–1670s; from the 1680s only {rent_late} {'entry mentions' if rent_late == 1 else 'entries mention'} it. The proviso is highest in the {dec(pmax.decade, lang)} ({pc(pmax.proviso_share)})."))
        add("how", ("선 둘은 「지대」와 「단서」다. 가로는 10년 구간의 첫 해, 세로는 그 10년 항목 가운데 그 문구가 든 항목의 비율이다. 1650년대는 항목이 없어 선을 끊었다." if ko else
                    "The two lines are 'Rent' and 'Proviso'. Across: first year of the decade; up: share of that decade's entries mentioning it. The line breaks at the 1650s, which have no entries."))
        add("one", (f"{dec(pmax.decade, lang)} 「단서」 {pc(pmax.proviso_share)}는 항목 {n(pmax.n)}개 가운데 {n(pmax.proviso)}개의 요약에 단서·무효 문구가 있다는 뜻이다." if ko else
                    f"'Proviso' in the {dec(pmax.decade, lang)}, {pc(pmax.proviso_share)}, means {n(pmax.proviso)} of {n(pmax.n)} entry summaries mention a proviso or a void clause."))
        add("mis", (f"Woodcroft가 쓴 요약의 문구를 센 것이라, 특허장 원문에 그 조항이 있었는지는 알 수 없다. 요약을 쓰는 방식이 바뀌어도 선이 움직일 수 있다. {dec(small.decade, lang)}의 {pc(small.rent_share, 0)}·{pc(small.proviso_share, 0)}는 항목 {int(small.n)}개의 값이다. 첫 점(1610년대)은 1617–1619년이다." if ko else
                    f"This counts wording in Woodcroft's summaries; whether the letters patent themselves had the clause is not known, and a change in how the summaries were written can also move the lines. The {dec(small.decade, lang)} values, {pc(small.rent_share, 0)} and {pc(small.proviso_share, 0)}, come from {int(small.n)} entries. The first point (1610s) covers 1617–1619."))
        add("terms", ("지대(rent) = 특허를 받은 사람이 왕실에 바치기로 한 돈. 단서(proviso) = 특허장에 붙은 조건. 무효(void) 조항 = 어떤 경우 특허를 없던 것으로 한다는 조항." if ko else
                      "Rent = money the patentee undertook to pay the Crown. Proviso = a condition attached to the patent. Void clause = a clause that makes the patent void in some case."))
        return intro, P

    # ------------------------------------------------------------------ P
    if key == "p1":
        p = D["m_p1_sro_annual"]
        ok = p[~p.gap]
        gap = p[p.gap].year.tolist()
        mx, mn = ok.loc[ok.entries.idxmax()], ok.loc[ok.entries.idxmin()]
        intro = ("1557–1640년 런던 출판업조합 등록부에 해마다 몇 건의 출판 허가가 적혔는지 그린 그림이다." if ko else
                 "How many entries for books the Stationers' Register in London records each year, 1557–1640.")
        add("short", (f"기록이 남은 해의 등록은 해마다 {n(mn.entries)}–{n(mx.entries)}건이고, 가장 많은 해는 {int(mx.year)}년({n(mx.entries)}건)이다." if ko else
                      f"In the years with records, {n(mn.entries)}–{n(mx.entries)} entries a year; the largest year is {int(mx.year)} ({n(mx.entries)})."))
        add("how", (f"가로는 연도, 세로는 그해 등록 항목 수다. 넓은 음영 「기록 없음」은 기재가 남지 않은 때로, 선에서 {yr_list(gap, lang)}을 빼고 끊었다. 좁은 음영 「1637」은 등록이 의무가 된 해다." if ko else
                    f"Across: year; up: register entries that year. The wide band, 'Gap', is the time for which no entries survive; the line leaves out {yr_list(gap, lang)} and breaks there. The narrow band '1637' is the year registration became compulsory."))
        add("one", (f"{int(mx.year)}년 값 {J(n(mx.entries))} 그해 날짜의 등록 항목이 {n(mx.entries)}건이라는 뜻이다. 한 항목에 저작이 여럿 들 수 있어, 그해 등록된 저작은 {n(mx.works)}건이다(표의 「저작」)." if ko else
                    f"The value for {int(mx.year)}, {n(mx.entries)}, means {n(mx.entries)} entries dated that year; one entry can cover several works, so {n(mx.works)} works were entered that year (the table's 'Works')."))
        add("mis", (f"등록 수는 출판된 책의 수가 아니다. 1637년 전에는 등록이 의무가 아니어서 등록하지 않고 낸 책도 있을 수 있다. 끊긴 {yr_list(gap, lang)}은 0건이 아니라 기록이 남지 않은 해다(표에서는 「기록 공백」 표시). 기록이 없는 때는 1571년 7월부터 1576년 7월까지다. 1571년은 그림과 표에서 통째로 공백으로 두었고, 1576년 값({n(p[p.year == 1576].entries.iloc[0])}건)은 7월부터 남은 일부의 값이다." if ko else
                    f"Entries are not the number of books published. Before 1637 registration was not compulsory, so some books may have appeared without one. The break at {yr_list(gap, lang)} is not zero but years with no surviving record (marked 'Gap' in the table). The record is missing from July 1571 to July 1576. 1571 is left blank as a whole in the chart and the table, and the 1576 value ({n(p[p.year == 1576].entries.iloc[0])}) covers only the part from July."))
        add("terms", ("출판업조합(Stationers' Company) = 런던의 인쇄·서적 상인 조합. 등록 = 책을 찍을 권리를 조합 등록부에 적는 일. SRO = 이 등록부를 옮긴 Stationers' Register Online." if ko else
                      "Stationers' Company = the London guild of printers and booksellers. Entry = recording the right to print a book in the Company's register. SRO = Stationers' Register Online, the transcription used here."))
        return intro, P

    if key == "p2":
        p = D["m_p2_sro_concentration"]
        out = p[p.entries < 20]
        q = p[p.entries >= 20]
        head, tail = q[q.year <= 1566], q[q.year >= 1631]
        mx = q.loc[q.year.idxmax()]
        intro = ("해마다 등록 가운데 가장 많이 등록한 다섯 사람의 몫을 그린 그림이다." if ko else
                 "The share of each year's entries held by the five people who entered most that year.")
        add("short", (f"그림에 그린 해의 값을 평균하면 1557–1566년 {pc(head.top5_share.mean(), 0)}({len(head)}해), 1631–1640년 {pc(tail.top5_share.mean(), 0)}({len(tail)}해)다." if ko else
                      f"Averaging the years drawn: {pc(head.top5_share.mean(), 0)} in 1557–1566 ({len(head)} years) and {pc(tail.top5_share.mean(), 0)} in 1631–1640 ({len(tail)} years)."))
        add("how", (f"가로는 연도, 세로는 그해 등록 가운데 상위 5인의 몫이다. 선이 높을수록 등록이 몇 사람에게 몰렸다. 등록이 20건 이상인 해만 그렸다 — 빠진 해({yr_list(out.year, lang)})와 기록이 없는 1571–1575년에서 선을 끊었다(기록은 1571년 7월부터 1576년 7월까지 없다 — 1571년은 통째로 빼고, 1576년은 7월부터의 값이다)." if ko else
                    f"Across: year; up: the top five's share of that year's entries. The higher the line, the more the entries concentrate in a few people. Only years with at least 20 entries are drawn; the line breaks at the year left out ({yr_list(out.year, lang)}) and at 1571–1575, which have no record (the record is missing from July 1571 to July 1576; 1571 is left out whole and 1576 has records from July only)."))
        add("one", (f"{int(mx.year)}년 {pc(mx.top5_share)}는 그해 등록 {n(mx.entries)}건 가운데 상위 5인의 몫을 더하면 {mx.top5_share * mx.entries:.1f}건어치라는 뜻이다. 여럿이 함께 등록한 항목은 사람 수로 나누어 세므로, 사람마다의 몫은 소수가 될 수 있다." if ko else
                    f"The value for {int(mx.year)}, {pc(mx.top5_share)}, means the top five's shares add up to {mx.top5_share * mx.entries:.1f} of that year's {n(mx.entries)} entries; an entry made by several people is split among them, so one person's share can be a fraction."))
        add("mis", (f"같은 사람이 다른 이름 키로 적혔으면 몫이 낮아질 수 있다. 등록이 적은 해는 다섯 사람만으로도 몫이 커진다 — 그래서 20건 미만인 해({', '.join(f'{int(r.year)}년 {int(r.entries)}건' for r in out.itertuples())})는 뺐다. 상위 5인은 해마다 다른 사람들일 수 있다. 정의의 다른 값인 HHI는 그리지 않았다(표)." if ko else
                    f"Someone written under two name keys can lower the share. In a year with few entries, five people alone make a large share, which is why years under 20 entries ({', '.join(f'{int(r.year)} with {int(r.entries)}' for r in out.itertuples())}) are left out. The top five can be different people each year. HHI, the other value in the definition, is not drawn (table)."))
        add("terms", ("이름 키 = SRO가 같은 사람의 여러 표기를 한 이름으로 묶으려고 붙인 표기(표의 「최다 등록자」, 예: dayejohn — 성과 이름을 붙여 쓴 꼴이 많지만 모양이 다 같지는 않다). 상위 5인 = 그해 등록 몫이 가장 큰 다섯 사람." if ko else
                      "Name key = the form SRO gives one person written in several ways (the table's 'Top enterer', e.g. dayejohn, mostly surname and first name run together, though not every key has that shape). Top five = the five people with the largest shares that year."))
        return intro, P

    if key == "p3":
        p = D["m_p3_sro_status"]
        r80 = p[p.decade == 1580].iloc[0]
        r20 = p[p.decade == 1620].iloc[0]
        sh = p.loc[p.shared_share.idxmax()]
        first, last_ = p.iloc[0], p.iloc[-1]
        r70 = p[p.decade == 1570].iloc[0]
        intro = ("10년마다 등록 항목 가운데 양도 표시와 공동 등록 표시가 붙은 것의 비율을 그린 그림이다." if ko else
                 "The share of register entries marked as reassigned and as shared, by decade.")
        add("short", (f"양도는 1580년대 {pc(r80.reassigned_share)}에서 1620년대 {pc(r20.reassigned_share)}로 관측된다. 공동 등록은 {dec(sh.decade, lang)} {pc(sh.shared_share)}가 가장 높다." if ko else
                      f"Reassignment is {pc(r80.reassigned_share)} in the 1580s and {pc(r20.reassigned_share)} in the 1620s. Shared entry is highest in the {dec(sh.decade, lang)} ({pc(sh.shared_share)})."))
        add("how", ("선 둘은 「양도」와 「공동 등록」이다. 가로는 10년 구간의 첫 해, 세로는 그 10년 등록 항목 가운데 그 표시가 붙은 항목의 비율이다. 「말소」는 그리지 않았다(표)." if ko else
                    "The two lines are 'Reassigned' and 'Shared'. Across: first year of the decade; up: share of that decade's entries with the mark. 'Cancelled' is not drawn (table)."))
        add("one", (f"1620년대 「양도」 {pc(r20.reassigned_share)}는 등록 {n(r20.entries)}건 가운데 {n(r20.reassigned)}건에 양도 표시가 있다는 뜻이다." if ko else
                    f"'Reassigned' in the 1620s, {pc(r20.reassigned_share)}, means {n(r20.reassigned)} of {n(r20.entries)} entries carry the mark."))
        add("mis", (f"첫 점({dec(first.decade, lang)})은 1557–1559년 {n(first.entries)}건, 마지막 점({dec(last_.decade, lang)})은 1640년 한 해 {n(last_.entries)}건뿐이다. 1570년대는 1571년 7월–1576년 7월의 기록이 없어 남은 기록이 {n(r70.entries)}건뿐이다. 한 항목에 표시가 여럿일 수 있다. SRO 편자가 붙인 표시를 그대로 셌다." if ko else
                    f"The first point ({dec(first.decade, lang)}) is 1557–1559 with {n(first.entries)} entries, the last ({dec(last_.decade, lang)}) 1640 alone with {n(last_.entries)}. The 1570s have only {n(r70.entries)} surviving entries because the record from July 1571 to July 1576 is missing. One entry can carry several marks. The marks are those given by the SRO editors."))
        add("terms", ("양도 = 등록된 권리를 다른 사람에게 넘긴 기재. 공동 등록 = 둘 이상이 함께 등록한 항목. 말소 = 지운 등록." if ko else
                      "Reassigned = an entry recording the transfer of the right to someone else. Shared = an entry made by two or more people. Cancelled = an entry struck out."))
        return intro, P

    if key == "p4":
        p = D["m_p4_sro_fees"]
        out = p[p.with_fee < 10]
        q = p[p.with_fee >= 10]
        before = q[q.year <= 1577]
        band = q[(q.year >= 1582) & (q.year <= 1587)]
        ex = q[q.year == 1590].iloc[0]
        intro = ("해마다 수수료가 적힌 등록 가운데 6펜스로 적힌 항목의 비율을 그린 그림이다." if ko else
                 "The share of entries with a fee of sixpence written, among each year's entries with a fee.")
        add("short", (f"1577년까지 해마다 {pc(before.fee6_share.max(), 0)} 이하이고, 1582–1587년에 {pc(band.fee6_share.min(), 0)}–{pc(band.fee6_share.max(), 0)}를 오간 뒤 1590년 {pc(ex.fee6_share)}다." if ko else
                      f"At most {pc(before.fee6_share.max(), 0)} a year up to 1577, between {pc(band.fee6_share.min(), 0)} and {pc(band.fee6_share.max(), 0)} in 1582–1587, and {pc(ex.fee6_share)} in 1590."))
        add("how", (f"가로는 연도, 세로는 그해 수수료가 적힌 항목 가운데 6펜스로 적힌 항목의 비율이다. 수수료가 적힌 항목이 10건 이상인 해만 그렸다(빠진 해: {yr_list(out.year, lang)}). 기록이 없는 1571–1575년에서는 선을 끊었다(기록은 1571년 7월부터 1576년 7월까지 없다 — 1571년은 통째로 빼고, 1576년은 7월부터의 값이다). 음영 1582–1587년은 SRO가 1582년까지는 수수료를 분량(종이 장수, sheets)으로 매기다 1587년부터 6펜스가 표준이 되었다고 적은 사이다." if ko else
                    f"Across: year; up: share of entries with sixpence written among that year's entries with a fee. Only years with at least 10 such entries are drawn (left out: {yr_list(out.year, lang)}); the line breaks at 1571–1575, which have no record (the record is missing from July 1571 to July 1576; 1571 is left out whole and 1576 has records from July only). The band 1582–1587 is the span between SRO's note that fees were set by the number of sheets up to 1582 and that sixpence was standard from 1587."))
        add("one", (f"1590년 {pc(ex.fee6_share)}는 수수료가 적힌 {n(ex.with_fee)}건 가운데 {n(ex.fee6)}건이 6펜스로 적혔다는 뜻이다." if ko else
                    f"The value for 1590, {pc(ex.fee6_share)}, means {n(ex.fee6)} of {n(ex.with_fee)} entries with a fee have sixpence written."))
        add("mis", ("여러 저작을 한 번에 등록하면 수수료가 6펜스의 배수가 되는데, 그런 항목은 6펜스로 세지 않는다. 그래서 6펜스가 표준이 된 뒤에도 비율이 100%가 되지 않을 수 있다. 분모는 0보다 큰 수수료가 적힌 항목이다. 수수료가 0으로 적혔거나 적히지 않은 항목은 분모에 없다(표의 「수수료 없음」 — 둘을 가르지 않은 수)." if ko else
                    "Entering several works at once makes the fee a multiple of sixpence, and such entries are not counted as sixpence, so the share can stay below 100% even after sixpence became standard. The total is the entries with a fee above zero written; entries with a fee of 0 or none written are not in it (the table's 'No fee stated', which does not tell the two apart)."))
        add("terms", ("펜스(d) = 옛 영국 화폐 단위, 12펜스가 1실링." if ko else "Pence (d) = the old English money unit; 12 pence made a shilling."))
        return intro, P

    if key in ("v1", "eras_v"):
        v = D["m_v1_fulin_annual"]
        oth = int((v.privileges - v.author - v.printer).sum())
        Fc = ctx["Fc"]
        fp = Fc[Fc.kind == "privilege"]
        unst = int(fp.note.fillna("").str.contains("not stated explicitly|outcome not stated|grant not stated|grant implied|not stated in act", case=False, regex=True).sum())
        joint = int((pd.to_numeric(fp.n_beneficiaries, errors="coerce") > 1).sum())
        _check(oth >= 0, "v1 other negative")
        if key == "eras_v":
            mx = v.loc[v.privileges.idxmax()]
            intro = ("Fulin이 모은 베네치아 문서 가운데 이 사이트가 출판 특권으로 분류한 문서가 해마다 몇 건인지, 1469년부터 1526년까지 그린 그림이다." if ko else
                     "How many of the Venetian documents edited by Fulin this site classes as printing privileges, year by year, 1469–1526.")
            add("short", (f"모두 {n(v.privileges.sum())}건이고, 가장 많은 해는 {int(mx.year)}년({int(mx.privileges)}건)이다." if ko else
                          f"{n(v.privileges.sum())} in all; the largest year is {int(mx.year)} ({int(mx.privileges)})."))
            add("how", ("가로는 연도, 세로는 그해 출판 특권 문서 수(건)다. 선이 높을수록 그해 특권 문서가 많다. 좁은 음영은 1474년(베네치아 특허법)과 1517년(원로원이 기존 출판 특권을 거두고 새 책에만 주기로 의결)이다." if ko else
                        "Across: year; up: printing privilege documents that year. The higher the line, the more documents. The narrow bands are 1474 (the Venetian patent act) and 1517 (the Senate revokes existing printing privileges and limits new ones to new books)."))
            add("one", (f"{int(mx.year)}년 값 {J(str(int(mx.privileges)))} 그해 날짜의 문서 가운데 출판 특권으로 분류한 것이 {int(mx.privileges)}건이라는 뜻이다." if ko else
                        f"The value for {int(mx.year)}, {int(mx.privileges)}, means {int(mx.privileges)} documents of that year are classed as printing privileges."))
            add("mis", (f"Fulin은 지금까지 전하는 문서만 모았다 — 내려진 특권 전부가 아니다. 특권으로 분류한 문서에는 허여가 확인된 것 말고도, 청원만 적혀 있어 제재 조항이나 판본을 근거로 특권으로 센 것이 들어 있다(코딩 메모에 허여가 적히지 않았거나 암시만 되었다고 적은 것 {unst}건 — 메모의 낱말로 센 수다). 1474년 음영은 발명 특허법의 해로, 출판 특권의 수를 정한 법이 아니다. 음영은 해를 표시할 뿐이다. 마지막 해 1526년은 11월까지의 문서다." if ko else
                        f"Fulin collected only the documents that survive, not every privilege granted. Documents classed as privileges include, besides confirmed grants, petitions whose grant is not recorded and which were counted on the strength of a penalty clause or an edition ({unst} whose coding note says the grant is not stated or only implied; counted from the wording of the notes). The 1474 band is the year of the act on invention patents, not a law on printing privileges; the bands mark years only. The last year, 1526, has documents up to November."))
            return intro, P
        vb = v.assign(b=v.year // 5 * 5).groupby("b")[["privileges", "author", "printer"]].sum().reset_index()
        later = vb[vb.b <= 1520]     # whole five-year periods only (1525 holds 1525-1526, 1465 holds 1469)
        mx = later.loc[later.privileges.idxmax()]
        b0 = vb.iloc[0]
        same = vb[(vb.author == vb.printer) & (vb.author > 0)].b.tolist()
        more = int((vb.privileges > vb.author + vb.printer).sum())
        yrs0 = v[(v.year // 5 * 5 == b0.b) & (v.privileges > 0)].year.tolist()
        _check(int(b0.b) == 1465 and yrs0 == [1469], "v1 first period is not 1465 holding only 1469")
        intro = ("Fulin이 모은 베네치아 문서 가운데 이 사이트가 출판 특권으로 분류한 문서가 5년마다 몇 건인지, 받은 사람의 유형과 함께 그린 그림이다." if ko else
                 "How many of the Venetian documents edited by Fulin this site classes as printing privileges, per five years, with the kind of person who received them.")
        early = int(v[v.year < 1490].privileges.sum())
        seq = vb[(vb.b >= 1490) & (vb.b <= 1520)]
        add("short", (f"{int(v.year.min())}–1489년에는 모두 {early}건뿐이다. 1490년부터 다섯 해가 다 든 구간은 " + ", ".join(f"{int(r.b)}–{int(r.b) + 4}년 {int(r.privileges)}건" for r in seq.itertuples()) + f"이고, 가장 많은 구간은 {int(mx.b)}–{int(mx.b) + 4}년이다." if ko else
                      f"{int(v.year.min())}–1489 have only {early} in all. The whole five-year periods from 1490 have " + ", ".join(f"{int(r.privileges)} ({int(r.b)}–{int(r.b) + 4})" for r in seq.itertuples()) + f"; the largest is {int(mx.b)}–{int(mx.b) + 4}."))
        add("how", (f"선 셋은 「전체」, 「저자」, 「인쇄업자」다. 가로는 5년 구간의 첫 해(1495는 1495–1499년), 세로는 그 5년의 특권 문서 합이다. 「저자」는 저자·편자·번역자·주석자나 그 상속인(저자이면서 인쇄업자인 사람 포함)이 받은 것, 「인쇄업자」는 인쇄업자·출판업자·서적상·활자 주조업자가 받은 것이다. 「전체」에는 둘 다 아닌 사람(화가·판화가·귀족·성직자 등)이 받은 {oth}건도 들어 있어, 그런 문서가 있는 구간({len(vb)}구간 가운데 {more}구간)에서는 두 선의 합보다 크고 나머지에서는 합과 같다. 좁은 음영 1517은 원로원이 기존 출판 특권을 거두고 새 책에만 특권을 주기로 의결한 해다." if ko else
                    f"Three lines: 'All', 'Author' and 'Printer'. Across: first year of the five-year period (1495 = 1495–1499); up: privilege documents in those five years. 'Author' counts authors, editors, translators, commentators or their heirs (including those who were also printers); 'Printer' counts printers, publishers, booksellers and typefounders. 'All' also holds {oth} documents for others (artists, engravers, noblemen, clerics and the like), so it is more than the two lines added in the periods with such documents ({more} of the {len(vb)}) and equal to it elsewhere. The narrow band, 1517, is the year the Senate revoked existing printing privileges and limited new ones to new books."))
        add("one", (f"{int(mx.b)} 구간의 {J(str(int(mx.privileges)))} {int(mx.b)}–{int(mx.b) + 4}년 다섯 해의 특권 문서 합이고, 그 가운데 저자 {int(mx.author)}건, 인쇄업자 {int(mx.printer)}건이다." if ko else
                    f"The {int(mx.b)} value, {int(mx.privileges)}, is the privilege documents of the five years {int(mx.b)}–{int(mx.b) + 4}: {int(mx.author)} to authors and {int(mx.printer)} to printers."))
        add("mis", (f"첫 점(1465)은 1469년 한 해만 든 구간이다 — Fulin의 문서가 1469년부터다. 마지막 1525 구간은 1525–1526년(11월까지)의 합이라 다섯 해 구간과 바로 견줄 수 없다. 전하는 문서만 모은 것이라 내려진 특권 전부가 아니고, 특권으로 분류한 문서에는 청원만 적혀 있어 제재 조항이나 판본을 근거로 센 것이 들어 있다(코딩 메모에 허여가 적히지 않았거나 암시만 되었다고 적은 것 {unst}건 — 메모의 낱말로 센 수다). 1517년 음영은 원로원 의결의 해를 표시할 뿐이다." + (" " + ", ".join(f"{int(r.b)} 구간" for r in vb[vb.b.isin(same)].itertuples()) + "은 저자와 인쇄업자 값이 같아(" + ", ".join(f"둘 다 {int(r.author)}건" for r in vb[vb.b.isin(same)].itertuples()) + ") 두 선이 겹친다." if same else "") if ko else
                    f"The first point (1465) holds the single year 1469: Fulin's documents start then. The last period, 1525, sums only 1525–1526 (to November), so it cannot be compared directly with the five-year sums. Only surviving documents are counted, not every privilege granted, and the documents classed as privileges include petitions whose grant is not recorded, counted on the strength of a penalty clause or an edition ({unst} whose coding note says the grant is not stated or only implied; counted from the wording of the notes). The 1517 band marks the year of the Senate's decision only." + (" In " + ", ".join(f"the {int(r.b)} period ({int(r.author)} each)" for r in vb[vb.b.isin(same)].itertuples()) + " the author and printer values are equal, so the two lines lie on each other." if same else "")))
        add("terms", (f"출판 특권 = 정해진 기간 동안 어떤 책을 찍거나 팔거나 들여올 권리, 또는 어떤 활자·기법을 쓸 권리를 받은 사람만 누리게 한(배타적) 허가. 한 문서를 여럿이 함께 받기도 했다(특권으로 분류한 문서 가운데 {joint}건)." if ko else
                      f"Printing privilege = an exclusive right, for a set term, to print, sell or import a work, or to use a type or technique. Some documents name several holders together ({joint} of those classed as privileges)."))
        return intro, P

    raise KeyError(f"no notes for chart {key!r}")


def checked(key, D, lang, ctx):
    """notes() with a guard: an unfilled template (a brace) in any sentence stops the build (1.1.4 v1 review found four)."""
    intro, parts = notes(key, D, lang, ctx)
    for t in [intro] + [x for _, x in parts]:
        _check("{" not in t and "}" not in t, f"{key} {lang}: unfilled template text: {t[:120]}")
    return intro, parts
