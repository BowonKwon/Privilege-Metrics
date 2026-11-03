# -*- coding: utf-8 -*-
"""Shared page shell, CSS and SVG chart helpers (adapted from the Sillok Metrics builder; palette changed)."""
import html
import math
import pandas as pd

CSS = """
:root{color-scheme:light;
  --bg:#f7f6f2;--bg2:#edebe4;--card:#ffffff;--line:#dcd9d0;--line2:#e9e6de;
  --fg:#1e2024;--fg2:#5b5f67;--fg3:#8a8e96;
  --accent:#8a3b2e;--accent2:#2f6372;
  --s1:#8a3b2e;--s2:#2f6372;--s3:#9a7a2f;--s4:#5e5a8a;--grid:#e4e1d9;
  --shadow:0 1px 2px rgba(30,32,40,.05),0 6px 18px rgba(30,32,40,.05);
  --display:"Noto Serif KR","Source Serif 4",Georgia,"Times New Roman",serif;
  --body:"Noto Sans KR",-apple-system,"Segoe UI","Apple SD Gothic Neo",Roboto,sans-serif}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;
  --bg:#1a1c1f;--bg2:#222326;--card:#232428;--line:#34363c;--line2:#2b2d32;
  --fg:#ebe9e4;--fg2:#b3b1aa;--fg3:#80827f;
  --accent:#d98a76;--accent2:#7fb3c2;
  --s1:#d98a76;--s2:#7fb3c2;--s3:#cfae63;--s4:#a9a3d6;--grid:#2e3035;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 20px rgba(0,0,0,.25)}}
:root[data-theme="dark"]{color-scheme:dark;
  --bg:#1a1c1f;--bg2:#222326;--card:#232428;--line:#34363c;--line2:#2b2d32;
  --fg:#ebe9e4;--fg2:#b3b1aa;--fg3:#80827f;
  --accent:#d98a76;--accent2:#7fb3c2;
  --s1:#d98a76;--s2:#7fb3c2;--s3:#cfae63;--s4:#a9a3d6;--grid:#2e3035;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 20px rgba(0,0,0,.25)}
*{box-sizing:border-box}html,body{max-width:100%;overflow-x:hidden}
body{margin:0;font:16px/1.7 var(--body);background:var(--bg);color:var(--fg);overflow-wrap:anywhere;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline;text-underline-offset:3px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
header{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:.55rem 1.1rem;display:flex;gap:1.4rem;align-items:center;flex-wrap:wrap}
header .brand{font-family:var(--display);font-weight:600;font-size:1.05rem;color:var(--fg);letter-spacing:-.01em}
header nav{display:flex;gap:1rem;flex-wrap:wrap}header nav a{color:var(--fg2);font-size:.92rem;padding:.2rem 0;border-bottom:2px solid transparent}
header nav a:hover{text-decoration:none;color:var(--fg)}header nav a.on{color:var(--fg);border-bottom-color:var(--accent2)}
header .right{margin-left:auto;display:flex;gap:.6rem;align-items:center}
header .lang{font-size:.88rem;color:var(--fg2);border:1px solid var(--line);border-radius:999px;padding:.15rem .7rem}header .lang:hover{text-decoration:none;color:var(--fg);border-color:var(--fg3)}
.theme{border:1px solid var(--line);background:transparent;color:var(--fg2);border-radius:999px;width:30px;height:30px;cursor:pointer;font-size:.9rem;line-height:1;padding:0}.theme:hover{color:var(--fg);border-color:var(--fg3)}
main{max-width:1060px;margin:0 auto;padding:1.6rem 1.1rem 4rem;min-width:0}
h1{font-family:var(--display);font-weight:600;font-size:clamp(1.6rem,3.2vw,2.2rem);line-height:1.25;letter-spacing:-.015em;margin:.3rem 0 .5rem;text-wrap:balance}
h2{font-family:var(--display);font-weight:600;font-size:1.3rem;line-height:1.3;margin:2.4rem 0 .8rem;padding-bottom:.35rem;border-bottom:1px solid var(--line);text-wrap:balance}
h3{font-size:1.02rem;margin:1.4rem 0 .4rem}
.eyebrow{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:.4rem}
.tag{display:inline-block;font-size:.74rem;letter-spacing:.04em;padding:.1rem .55rem;border-radius:999px;color:var(--fg2);background:var(--bg2);border:1px solid var(--line2)}
.tag.layer{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 35%,transparent);background:color-mix(in srgb,var(--accent) 9%,transparent)}
.lead{color:var(--fg2);font-size:1.05rem;max-width:70ch;margin:0 0 1.2rem}
.hero{padding:.6rem 0 1.4rem;border-bottom:1px solid var(--line);margin-bottom:1.4rem}
.hero h1{font-size:clamp(1.9rem,4vw,2.7rem)}.hero .lead{font-size:1.12rem}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:.8rem;margin:.9rem 0 1.4rem}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.85rem 1rem .9rem;box-shadow:var(--shadow);color:var(--fg);transition:transform .15s,border-color .15s}
a.card:hover{text-decoration:none;transform:translateY(-2px);border-color:var(--fg3)}
.card b{display:block;margin-bottom:.25rem;font-size:.98rem;color:var(--accent)}.card small{color:var(--fg2);font-size:.86rem;line-height:1.5;display:block}
.card.s-A{border-top:3px solid var(--s1)}.card.s-B{border-top:3px solid var(--s3)}.card.s-C{border-top:3px solid var(--s2)}.card.s-D{border-top:3px solid var(--s4)}.card.s-E{border-top:3px solid var(--fg3)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:.8rem;margin:1.2rem 0 1.6rem}
.stat{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.1rem;box-shadow:var(--shadow);color:var(--fg)}
.stat .n{font-family:var(--display);font-size:2rem;font-weight:600;line-height:1.1;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stat small{display:block;color:var(--fg2);margin-top:.35rem;font-size:.86rem;line-height:1.45}
a.stat:hover{text-decoration:none;border-color:var(--fg3)}
.spec{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem;margin:1rem 0 1.4rem;box-shadow:var(--shadow)}
.rel{border-left:4px solid var(--accent2)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.55rem 1.4rem;margin:0}dt{color:var(--fg3);font-size:.86rem;letter-spacing:.01em;padding-top:.15rem}dd{margin:0;min-width:0}
dd.formula{font-family:ui-monospace,"SF Mono",Consolas,"Noto Sans KR",monospace;font-size:.9rem;background:var(--bg2);border-radius:6px;padding:.45rem .65rem;line-height:1.6}
@media(max-width:640px){dl{grid-template-columns:1fr}dt{margin-top:.5rem}}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin:.6rem 0}
th,td{border-bottom:1px solid var(--line2);padding:.42rem .6rem;text-align:left;vertical-align:top}
thead th{color:var(--fg2);font-weight:600;font-size:.82rem;letter-spacing:.02em;cursor:pointer;white-space:nowrap;border-bottom:1px solid var(--line)}
thead th:hover{color:var(--fg)}tbody tr:nth-child(even){background:color-mix(in srgb,var(--bg2) 55%,transparent)}tbody tr:hover{background:var(--bg2)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}td:first-child{white-space:nowrap}
table.fixed{table-layout:fixed;min-width:900px}table.fixed th{white-space:normal}table.fixed td{white-space:normal;overflow-wrap:normal;word-break:break-all}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);padding:0 .3rem;margin:.6rem 0 1rem}.wrap table{margin:0}
figure{margin:1.2rem 0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1rem .8rem;box-shadow:var(--shadow)}
figcaption{font-size:.86rem;color:var(--fg2);margin-top:.5rem;line-height:1.5}
svg{max-width:100%;height:auto;display:block}svg text{font-family:var(--body);fill:var(--fg2);font-size:11px}svg .ax{stroke:var(--line)}svg .grid{stroke:var(--grid)}
.legend{display:flex;gap:1.1rem;font-size:.86rem;color:var(--fg2);flex-wrap:wrap;margin:.2rem 0 .4rem}.legend span::before{content:"";display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:.4rem;vertical-align:-1px;background:var(--c)}
.note{background:color-mix(in srgb,var(--accent) 7%,var(--card));border:1px solid color-mix(in srgb,var(--accent) 25%,var(--line));border-left:4px solid var(--accent);border-radius:8px;padding:.7rem 1rem;margin:1.2rem 0;font-size:.95rem}
.prose p,.prose ul,.prose ol,.prose .note,.prose .lead{max-width:72ch}.prose p{margin:.8rem 0}.prose ul,.prose ol{padding-left:1.2rem}.prose li{margin:.3rem 0}
.src{color:var(--fg2);font-size:.92rem}.files a{display:inline-block;font-size:.85rem;background:var(--bg2);border:1px solid var(--line2);border-radius:6px;padding:.15rem .55rem;margin:.2rem .3rem .2rem 0;color:var(--fg2)}.files a:hover{color:var(--fg);text-decoration:none;border-color:var(--fg3)}
footer{border-top:1px solid var(--line);color:var(--fg3);font-size:.82rem;padding:1.2rem;text-align:center;line-height:1.6}
.filter{margin:.5rem 0}.filter input{padding:.4rem .7rem;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);width:min(100%,340px);font:inherit;font-size:.9rem}
.filter input:focus{border-color:var(--accent);outline:none;box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 20%,transparent)}
.links{display:flex;gap:1.2rem;flex-wrap:wrap;margin-top:2rem;font-size:.95rem}
@media(prefers-reduced-motion:reduce){.card,a.card:hover{transition:none;transform:none}}
/* --- visual layer: hero band, glyph watermark, key values, takeaways, ribbons --- */
.hero{position:relative;padding:1.4rem 0 1.2rem;margin:-.4rem 0 1.4rem;border-bottom:1px solid var(--line);overflow:hidden}
.hero::before{content:"";position:absolute;inset:0 -1.1rem auto -1.1rem;height:6px;background:linear-gradient(90deg,var(--s1),var(--s2) 50%,var(--s3))}
.hero .glyph{position:absolute;right:-.2rem;top:.6rem;font-family:var(--display);font-size:clamp(5rem,14vw,9rem);line-height:1;color:var(--accent);opacity:.07;pointer-events:none;user-select:none;letter-spacing:-.04em}
.hero .lead{max-width:62ch}
.strip{margin:1.2rem 0 .2rem}.strip svg text{font-size:10.5px}
.take{position:relative;background:color-mix(in srgb,var(--accent2) 9%,var(--card));border:1px solid color-mix(in srgb,var(--accent2) 30%,var(--line));border-left:5px solid var(--accent2);border-radius:10px;padding:.9rem 1.2rem 1rem;margin:1.2rem 0 1.4rem;box-shadow:var(--shadow)}
.take .l{font-family:var(--display);font-weight:600;font-size:.98rem;color:var(--accent2);letter-spacing:-.005em}
.take p{margin:.3rem 0 0;font-size:1.02rem;line-height:1.65;max-width:76ch}
.take.small p{font-size:.95rem}
.card{position:relative}.card .kv{display:block;font-family:var(--display);font-weight:600;font-size:1.55rem;line-height:1.1;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:var(--fg);margin:.1rem 0 .35rem}
.card .kv small{display:inline;font:inherit;font-family:var(--body);font-weight:400;font-size:.8rem;color:var(--fg3);margin-left:.4rem;letter-spacing:0}
h2.num{counter-increment:sec}h2.num::before{content:attr(data-n);font-family:var(--display);font-weight:600;color:var(--accent2);margin-right:.6rem;font-size:.95rem;vertical-align:.12em;font-variant-numeric:tabular-nums}
.mhero{display:grid;grid-template-columns:1fr auto;gap:1rem 2rem;align-items:end;margin-bottom:.4rem}
.mhero .big{font-family:var(--display);font-weight:600;font-size:clamp(2rem,4.5vw,3.2rem);line-height:1;letter-spacing:-.025em;font-variant-numeric:tabular-nums;color:var(--accent);text-align:right;white-space:nowrap;min-width:0}
.mhero .big.long{font-size:clamp(1.5rem,3vw,2.1rem);line-height:1.15;white-space:normal;overflow-wrap:break-word;max-width:18ch;margin-left:auto}
.mhero .big small{display:block;font:inherit;font-family:var(--body);font-weight:400;font-size:.82rem;color:var(--fg2);letter-spacing:0;margin-top:.35rem;white-space:normal;max-width:22ch;margin-left:auto}
@media(max-width:720px){.mhero{grid-template-columns:1fr}.mhero .big{text-align:left;white-space:normal;overflow-wrap:anywhere}.mhero .big.long{max-width:none;margin-left:0}.mhero .big small{margin-left:0}}
.ribbon{margin:.8rem 0 1.2rem}.ribbon svg text{font-size:10px}
.rel .badge{display:inline-block;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;padding:.1rem .5rem;border-radius:999px;background:var(--accent2);color:#fff;margin-right:.5rem;vertical-align:.1em}
.stat .n{color:var(--accent)}

"""

JS = """
(function(){var k="ppm-theme",r=document.documentElement,b=document.getElementById("theme");function ap(v){if(v)r.setAttribute("data-theme",v);else r.removeAttribute("data-theme");if(b)b.textContent=v==="dark"?"\\u263E":v==="light"?"\\u2600":"\\u25D1"}var cur=localStorage.getItem(k)||"";ap(cur);if(b)b.addEventListener("click",function(){cur=cur===""?"light":cur==="light"?"dark":"";if(cur)localStorage.setItem(k,cur);else localStorage.removeItem(k);ap(cur)})})();
document.querySelectorAll('table.sort').forEach(function(t){
  var ths=t.querySelectorAll('th');ths.forEach(function(th,i){th.addEventListener('click',function(){
    var rows=Array.from(t.tBodies[0].rows),asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
    rows.sort(function(a,b){var x=a.cells[i].dataset.v||a.cells[i].textContent,y=b.cells[i].dataset.v||b.cells[i].textContent;
      var nx=parseFloat(x),ny=parseFloat(y);if(!isNaN(nx)&&!isNaN(ny))return asc?nx-ny:ny-nx;return asc?x.localeCompare(y):y.localeCompare(x)});
    rows.forEach(function(r){t.tBodies[0].appendChild(r)})})})});
document.querySelectorAll('.filter input').forEach(function(inp){inp.addEventListener('input',function(){
  var q=inp.value.toLowerCase(),t=document.getElementById(inp.dataset.target);
  Array.from(t.tBodies[0].rows).forEach(function(r){r.style.display=r.textContent.toLowerCase().indexOf(q)>=0?'':'none'})})});
"""


def esc(s) -> str:
    return html.escape("" if s is None or (isinstance(s, float) and math.isnan(s)) else str(s))


def fmt(v, spec) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)) or (isinstance(v, str) and v == ""):
        return ""
    if hasattr(v, "item"):          # numpy scalar -> Python scalar (repr(np.float64) is not a decimal literal)
        v = v.item()
    try:
        if isinstance(v, float) and spec and spec[-1] == "d" and v.is_integer():
            v = int(v)                  # integer columns read as float because of blank cells
        if isinstance(v, float) and spec and spec[-1] in "%f":
            # 1.2.1: round half-up on the decimal value (format() rounds the binary float: 0.0295 → '2.9%', 0.575 → '0.57')
            from decimal import Decimal, ROUND_HALF_UP
            digits = int(spec.rstrip("%f").split(".")[-1] or 0) if "." in spec else 0
            scaled = Decimal(repr(v)) * (100 if spec.endswith("%") else 1)
            q = scaled.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
            s = f"{q:,.{digits}f}" if "," in spec else f"{q:.{digits}f}"
            return s + ("%" if spec.endswith("%") else "")
        return format(v, spec)
    except Exception:
        return str(v)


# ----------------------------------------------------------------- SVG charts
def nice_ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10)), key=lambda st: abs(st - raw))
    start = math.floor(lo / step) * step
    ticks, v = [], start
    while v <= hi + step * 1e-9:
        if v >= lo - step * 1e-9:
            ticks.append(round(v, 10))
        v += step
    return ticks


def svg_lines(series, spec, width=900, height=320, ylabel="", xstep=None, bands=None, lang="en") -> str:
    xs = [p[0] for _, pts, _ in series for p in pts]
    ys = [p[1] for _, pts, _ in series for p in pts if not math.isnan(p[1])]
    if not xs or not ys:
        return ""
    x0, x1, y0, y1 = min(xs), max(xs), 0.0, max(ys) * 1.05 or 1
    L, R, Tp, B = 62, (110 if len(series) > 1 else 20), 16, 36
    pw, ph = width - L - R, height - Tp - B
    X = lambda v: L + (v - x0) / (x1 - x0 or 1) * pw
    Y = lambda v: Tp + ph - (v - y0) / (y1 - y0) * ph
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{"선 그래프" if lang == "ko" else "Line chart"}">']
    if bands:
        for (a, b, label) in bands:
            out.append(f'<rect x="{X(a):.1f}" y="{Tp}" width="{max(X(b)-X(a),1):.1f}" height="{ph}" fill="var(--accent2)" fill-opacity=".10"><title>{esc(label)}</title></rect>')
    for v in nice_ticks(y0, y1):
        out.append(f'<line class="grid" x1="{L}" y1="{Y(v):.1f}" x2="{width-R}" y2="{Y(v):.1f}"/><text x="{L-6}" y="{Y(v)+4:.1f}" text-anchor="end">{fmt(v, spec)}</text>')
    step = xstep or max(1, int((x1 - x0) / 8 / 10) * 10)
    xv = int(math.ceil(x0 / step) * step)
    while xv <= x1:
        out.append(f'<text x="{X(xv):.1f}" y="{height-12}" text-anchor="middle">{xv}</text>')
        xv += step
    if ylabel:
        out.append(f'<text x="{L}" y="10">{esc(ylabel)}</text>')
    for name, pts, ci in series:
        pts = [p for p in pts if not math.isnan(p[1])]
        if not pts:
            continue
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for i, (x, y) in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="var(--s{ci+1})" stroke-width="1.8" stroke-linejoin="round"/>')
        for x, y in pts:
            out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="transparent"><title>{esc(name)} · {x}: {fmt(y, spec)}</title></circle>')
        if len(series) > 1:
            lx, ly = pts[-1]
            out.append(f'<text x="{X(lx)+4:.1f}" y="{Y(ly)+4:.1f}">{esc(name)}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_bars(items, spec, width=900, row_h=22, label_w=240, xlabel="", errors=None, lang="en") -> str:
    vals = [v for _, v, _ in items if not (isinstance(v, float) and math.isnan(v))]
    if not vals:
        return ""
    hi_err = max([e[1] for e in errors.values()] if errors else [0])
    lo, hi = 0.0, max(max(vals), hi_err, 0.0)
    pad = hi * 0.05 or 1
    hi = hi + pad
    pw = width - label_w - 30
    h = row_h * len(items) + 40
    x = lambda v: label_w + (v - lo) / (hi - lo) * pw
    out = [f'<svg viewBox="0 0 {width} {h}" role="img" aria-label="{"막대 그래프" if lang == "ko" else "Bar chart"}">']
    for v in nice_ticks(lo, hi):
        out.append(f'<line class="grid" x1="{x(v):.1f}" y1="6" x2="{x(v):.1f}" y2="{h-30}"/><text x="{x(v):.1f}" y="{h-14}" text-anchor="middle">{fmt(v, spec)}</text>')
    if xlabel:
        out.append(f'<text x="{label_w+pw/2:.0f}" y="{h-2}" text-anchor="middle">{esc(xlabel)}</text>')
    for i, (name, v, ci) in enumerate(items):
        y = 8 + i * row_h
        out.append(f'<text x="{label_w-8}" y="{y+row_h*0.68:.1f}" text-anchor="end">{esc(name)}</text>')
        if isinstance(v, float) and math.isnan(v):
            continue
        out.append(f'<rect x="{x(0):.1f}" y="{y+2}" width="{max(x(v)-x(0),1):.1f}" height="{row_h-6}" fill="var(--s{ci+1})" rx="3"><title>{esc(name)}: {fmt(v, spec)}</title></rect>')
        if errors and name in errors:
            lo_e, hi_e = errors[name]
            out.append(f'<line x1="{x(lo_e):.1f}" y1="{y+row_h/2-1:.1f}" x2="{x(hi_e):.1f}" y2="{y+row_h/2-1:.1f}" stroke="var(--fg)" stroke-width="1.5"/>')
    out.append("</svg>")
    return "".join(out)


def legend(entries) -> str:
    return '<div class="legend">' + "".join(f'<span style="--c:var(--s{ci+1})">{esc(n)}</span>' for n, ci in entries) + "</div>"


MAX_ROWS = 60
T = {"ko": {"search": "필터"}, "en": {"search": "Filter"}}

# Column labels for every metric table, Korean and English. The CSV files keep the keys; only the page headers change.
COLS = {
    "year": ("연도", "Year"), "decade": ("10년", "Decade"), "period": ("구간", "Period"), "window": ("구간", "Window"), "years": ("햇수", "Years"),
    "n": ("전체", "Total"), "count": ("건수", "Count"), "share": ("비율", "Share"), "entries": ("항목", "Entries"),
    "hulme": ("Hulme", "Hulme"), "woodcroft_grants": ("Woodcroft 허여", "Woodcroft grants"), "woodcroft_extensions": ("Woodcroft 연장", "Woodcroft extensions"),
    "woodcroft_no_text": ("본문 없는 번호", "Numbers without text"), "grants": ("허여", "Grants"), "list": ("목록", "List"),
    "jurisdiction": ("관할", "Jurisdiction"), "kind": ("종류", "Kind"), "unit": ("단위", "Unit"), "basis": ("근거", "Basis"), "source": ("자료원", "Source"),
    "coverage": ("범위", "Coverage"), "alt_count": ("다른 계수", "Other count"), "alt_source": ("다른 계수의 자료원", "Source of other count"),
    "per_year": ("연평균", "Per year"), "ci_low": ("95% 구간 하한", "95% CI low"), "ci_high": ("95% 구간 상한", "95% CI high"),
    "term_stated": ("기간 적힘", "Terms stated"), "term_median": ("기간 중앙값", "Median term"), "term_21": ("21년", "21 years"), "term_14_or_less": ("14년 이하", "≤14 years"),
    "extensions": ("연장 항목", "Extensions"), "field": ("분야", "Field"), "field_name": ("분야", "Field"),
    "classified": ("분류된 허여", "Classified"), "hhi": ("HHI", "HHI"), "top_field": ("가장 큰 분야", "Largest field"), "top_share": ("가장 큰 분야의 몫", "Largest field's share"),
    "other_share": ("「기타」 비율", "'Other' share"), "sector_berveglieri": ("분야(Berveglieri)", "Sector (Berveglieri)"), "our_field": ("이 사이트 분야", "Field here"),
    "communication": ("communication", "Communication"), "foreign_address": ("해외 주소", "Address abroad"), "either": ("둘 중 하나", "Either"),
    "communication_share": ("communication 비율", "Communication share"), "foreign_address_share": ("해외 주소 비율", "Address-abroad share"),
    "either_share": ("둘 중 하나 비율", "Either share"), "either_ci_low": ("95% 구간 하한", "95% CI low"), "either_ci_high": ("95% 구간 상한", "95% CI high"),
    "foreign": ("외국", "Foreign"), "foreign_incl_probable": ("외국(추정 포함)", "Foreign incl. probable"), "co": ("공동 허여", "Shared grants"),
    "foreign_share": ("외국 비율", "Foreign share"), "foreign_incl_probable_share": ("외국(추정 포함) 비율", "Foreign share incl. probable"), "co_share": ("공동 허여 비율", "Shared-grant share"),
    "hulme_alien": ("Hulme 외국인", "Hulme aliens"), "hulme_native": ("Hulme 내국인", "Hulme natives"), "hulme_trade": ("Hulme 거래 규제", "Hulme trade"),
    "hulme_total": ("Hulme 합계", "Hulme total"), "explicit": ("명시", "Explicit"), "indirect": ("간접", "Indirect"),
    "n_stated": ("기간 적힘", "Terms stated"), "median": ("중앙값", "Median"), "p25": ("1사분위", "Lower quartile"), "p75": ("3사분위", "Upper quartile"),
    "min": ("최소", "Min"), "max": ("최대", "Max"), "values": ("값별 건수", "Counts by value"),
    "stated": ("기간 적힘", "Terms stated"), "le14": ("14년 이하", "≤14 years"), "eq21": ("21년", "21 years"), "other_term": ("다른 기간 병기", "Further terms"),
    "rent": ("지대", "Rent"), "proviso": ("단서", "Proviso"), "rent_share": ("지대 비율", "Rent share"), "proviso_share": ("단서 비율", "Proviso share"),
    "works": ("저작", "Works"), "gap": ("기록 공백", "Gap"), "enterers": ("등록자", "Enterers"), "top5_share": ("상위 5인 몫", "Top-five share"), "top1": ("최다 등록자", "Top enterer"),
    "shared": ("공동 등록", "Shared"), "reassigned": ("양도", "Reassigned"), "cancelled": ("말소", "Cancelled"), "stock": ("stock 표시", "Stock"),
    "shared_share": ("공동 등록 비율", "Shared share"), "reassigned_share": ("양도 비율", "Reassigned share"), "cancelled_share": ("말소 비율", "Cancelled share"),
    "with_fee": ("수수료 적힘", "With fee"), "fee6": ("6펜스 항목", "6d entries"), "median_fee": ("수수료 중앙값(펜스)", "Median fee (d)"),
    "fee6_share": ("6펜스 비율", "6d share"), "no_fee_stated": ("수수료 없음", "No fee stated"),
    "privileges": ("특권", "Privileges"), "author": ("저자", "Author"), "printer": ("인쇄업자", "Printer"), "documents": ("문서", "Documents"),
}


def col_label(c: str, lang: str) -> str:
    """Header for a table column. Unknown keys fail loudly so that no raw key reaches a page."""
    if c not in COLS:
        raise KeyError(f"no column label for {c!r}; add it to site_kit.COLS")
    return COLS[c][0 if lang == "ko" else 1]


def table_html(df: pd.DataFrame, cols, tid: str, lang: str, filt=True) -> str:
    t = T[lang]
    out = []
    if filt:
        out.append(f'<div class="filter"><input placeholder="{t["search"]}…" data-target="{tid}"></div>')
    # Chrome's automatic table layout stalls on a few hundred rows of long CJK cells; large tables use a
    # fixed layout with explicit column widths (the context column gets the room, the rest share equally)
    big = len(df) > 100
    if big:   # the full table is in the CSV; the page shows the first rows only
        note = (f"표의 처음 {MAX_ROWS}행만 보인다(전체 {len(df):,}행은 CSV)." if lang == "ko" else f"First {MAX_ROWS} of {len(df):,} rows shown; the CSV has them all.")
        out.append(f'<p class="src">{note}</p>')
        df = df.head(MAX_ROWS)
    out.append(f'<div class="wrap"><table class="sort{" fixed" if big else ""}" id="{tid}"><thead><tr>')
    wide = [c for c, _, _ in cols if c in ("context", "title", "top5")]
    for c, hname, spec in cols:
        style = ""
        if big:
            if c in wide:
                style = f' style="width:{int(50/len(wide))}%"'
        out.append(f'<th class="{"num" if spec else ""}"{style}>{esc(hname)}</th>')
    out.append("</tr></thead><tbody>")
    for _, r in df.iterrows():
        out.append("<tr>")
        for c, hname, spec in cols:
            v = r.get(c)
            if spec:
                out.append(f'<td class="num" data-v="{"" if pd.isna(v) else v}">{fmt(v, spec)}</td>')
            else:
                out.append(f"<td>{esc(v)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


KEEP_LOWER = {"n", "p10", "p25", "p50", "p75", "p90", "p99", "max"}   # unit / statistic abbreviations stay as they are


def cap(s, lang: str) -> str:
    """Sentence case for English headers, legends and labels: first letter up, the rest untouched."""
    s = "" if s is None else str(s)
    if lang != "en" or not s or s in KEEP_LOWER or not s[0].islower():
        return s
    return s[0].upper() + s[1:]


def fig(svg: str, caption: str) -> str:
    return f"<figure>{svg}<figcaption>{caption}</figcaption></figure>" if svg else ""

