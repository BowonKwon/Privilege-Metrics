# -*- coding: utf-8 -*-
"""Method page and reading edition, Korean and English. Numbers come from the derived tables and reliability.json."""
import json
from pathlib import Path

import pandas as pd

from paths import COD, DER, find, need


def _rel():
    return json.loads(need(DER / "reliability.json").read_text(encoding="utf-8"))


def build():
    R = _rel().get("_summary", {})
    W = pd.read_csv(find(DER, "woodcroft_entries.csv"))
    miss = int((~W["parsed"].astype(bool)).sum())     # numbers with no text (the parse log lists the same numbers)
    ds = W["date_source"].value_counts()
    margin = int(ds.get("margin", 0))
    ocr = int(ds.get("margin_ocr", 0) + ds.get("margin_year", 0))
    page = int(ds.get("page_image", 0))
    neigh = int(ds.get("neighbours", 0) + ds.get("margin_rejected+neighbours", 0))
    multi = int(W[W["year"].between(1617, 1700)]["term_other"].notna().sum())
    Fc = pd.read_csv(need(COD / "fulin_coding.csv"), dtype=str)
    unstated = int(((Fc["kind"] == "privilege") & Fc["note"].fillna("").str.contains(
        "not stated explicitly|outcome not stated|grant not stated|grant implied|not stated in act", case=False, regex=True)).sum())
    g = lambda k, d="—": R.get(k, d)
    wy = W[W["year"].notna()]
    c6099 = int(wy["year"].between(1660, 1799).sum())          # all numbered entries, as in the published comparisons
    c0050 = int(wy["year"].between(1700, 1850).sum())
    F = pd.read_csv(need(COD / "fulin_coding.csv"), dtype=str)
    fy = pd.to_numeric(F["date"].str[:4], errors="coerce")
    f9226 = int(((F["kind"] == "privilege") & fy.between(1492, 1526)).sum())
    METHOD = {
        "ko": [
            ("무엇을 세었나", [
                "잉글랜드 발명 특권·특허는 두 목록에서 셌다. 1561–1603년은 Hulme(1896·1900)가 특허 기록부 캘린더에서 뽑은 산업 독점 허여 55건이고, 1617–1852년은 Woodcroft(1854)의 연대순 목록 1–14,359번이다. 1604–1616년은 두 목록 사이라 비어 있다. 1827년 하원이 1623년 이전의 특권·특허 목록을 요구했으나 그 목록은 끝내 제출되지 않았다고 Hulme(1896)가 적었다.",
                f"런던 출판업조합 등록부는 Stationers' Register Online의 TEI 원자료(1557–1640, 10,453항목)를 그대로 읽었다. 베네치아 출판 특권은 Fulin(1882)이 모은 문서 256건을 문서마다 읽어 코딩했다. 특권으로 코딩한 것 가운데 {unstated}건은 Fulin의 요약에 청원만 있고 허여가 적혀 있지 않다. 제재 조항이나 Fulin 주석의 「con privilegio」 판본을 근거로 특권으로 셌으며, 코딩 표의 note 열에 그렇게 적었다. 네덜란드는 Buning·Looijesteijn이 공개한 자료를 다시 셌다.",
                "베네치아 발명 특허는 이 사이트가 세지 않았다. 이 사이트가 확인한 건별 원천은 Berveglieri(2020)의 레게스토(종이책)이고, 그보다 앞서 Mandich(1936·1948)가 1474–1550년 109건을 옮기고 분류했다(Comino 등 2017). 문헌 수치는 「2차 인용」으로 표시해 따로 둔다."]),
            ("Woodcroft 목록을 읽은 방법", [
                f"Internet Archive의 OCR 단어 좌표에서 여백 단(수혜자 성·날인일)과 본문 단(번호·요약)을 갈랐다. 번호는 1부터 14,359까지 늘어나야 하므로, 번호처럼 보이는 줄 가운데 가장 긴 증가 사슬을 고르고 그 틈에 낀 후보는 차례로 다시 번호를 매겼다. OCR이 번호를 잃은 115쪽은 같은 쪽 이미지를 tesseract 5로 다시 읽었다. 그래도 본문을 찾지 못한 번호는 {miss}개다. 이 번호들은 연도별 수에는 넣고(앞뒤 항목의 연도), 본문이 필요한 지표에서는 뺐다. 연장 항목 비율만은 이 번호들을 연장이 아닌 항목으로 분모에 남기므로 하한이다.",
                f"날짜는 여백의 날인일이다. {margin:,}항목은 여백 날짜를 그대로 썼다. OCR이 망가뜨린 여백 날짜({ocr}항목)는 연도가 앞뒤의 깨끗한 날짜 사이에 들 때만 썼고, 일(日)은 숫자가 깨끗할 때만 남겼다. OCR이 여백 날짜를 아예 잃은 {page}항목은 쪽 이미지에서 읽어 data/coding/woodcroft_date_overrides.csv에 적었다. 나머지는 앞뒤 항목의 연도가 같을 때 그 연도를 썼다({neigh:,}항목).",
                "앞뒤 항목의 연도가 서로 같은데 혼자 다른 해는 OCR 오독으로 보고 버렸다. 7046·7049번은 Woodcroft 지면에도 1836년 3월 항목들 사이에 「29th March 1835」로 인쇄되어 있어 인쇄 오식으로 보고 1836년으로 셌다.",
                "여백에서 숫자가 든 줄은 날짜이지 수혜자 성이 아니다. 수혜자 수(공동 수혜)는 숫자 없는 여백 줄만 센다. 해외 주소는 수혜자 설명에 브리튼 제도 밖 지명이 있을 때로 보되, 「Hanover Square」 같은 런던 거리 이름과 외국 학회 회원 자격은 주소로 보지 않는다.",
                f"존속기간은 요약에 적힌 첫 기간이다. 옛 철자(fourteene, one and twentie)와 로마 숫자(xiiij, xxjtie), OCR이 망가뜨린 꼴(xilij)을 읽는다. 한 항목에 광산권·아일랜드·뒤따르는 수익권처럼 다른 기간이 함께 적히면 term_other 열에 따로 둔다(1617–1700년 {multi}건). 1617–1640년 1–126번의 첫 기간은 독립 검증자가 쪽 이미지에서 읽은 값과 모두 같다. 1820년 무렵부터 요약이 기간을 적지 않으므로 그 뒤의 기간은 비워 두었다. 법정 14년을 가정해 채우지 않았다.",
                "지대·단서 조항·외국 연관은 요약문의 단어로 판정했다. 지대 지표는 지대 문구가 있는 비율이지 지대 의무를 법적으로 판정한 비율이 아니다."]),
            ("분야 분류", [
                "분야는 17개다. 발명 명칭에 정해진 순서대로 단어 규칙을 적용해 처음 맞는 분야를 택한다. 1700년 이전 항목은 명칭이 따옴표로 갈라져 있지 않아 요약 전체에 적용했고, 옛 철자는 현대 철자로 바꾼 뒤 맞췄다.",
                "규칙은 결과를 보기 전에 정했으나 공개 전에 세 번 고쳤다. r2에서는 17세기의 「instrument」(장치 일반)를 기기 분야에서 뺐다. r3에서는 옛 철자 표를 넣고 1700년 이전 항목의 분류 대상을 요약 전체로 넓혔다. 이 두 번은 첫 결과가 이상해서 고친 것이다.",
                f"r3 규칙을 독립 코더의 본문 재코딩 212항목(R2)과 맞춰 보니 분야 일치가 {g('r2_dictr3_field')}였고 광업은 11건 중 2건만 맞았다. 「tan pits」·「pit coal」·「smelting copper ore」가 광업으로 가고 가스 조명이 화학으로 간 탓이었다. r4에서 이를 고친 뒤, 고친 근거가 된 표본이 아니라 다른 시드로 새로 뽑은 212항목(R2b)으로 다시 쟀다. 아래 신뢰도 카드의 분야 수치는 R2b다. 고친 내용은 src/fields.py 머리에 그대로 남겼다."]),
            ("신뢰도 카드", [
                f"쪽 이미지 대조(R1): 시기별 30항목씩 120항목을 쪽 이미지에서 독립 코더가 직접 읽어 번호·날짜·수혜자 수·「communication」·기간을 우리 추출값과 비교했다. 연도 일치 {g('r1_year')}, 날짜(일) 일치 {g('r1_date')}, 기간 일치 {g('r1_term')}, 수혜자 수 일치 {g('r1_ngrantees')}, communication 일치 {g('r1_comm')}.",
                f"본문 재코딩(R2b): 분야마다 11항목(「기타」 25항목), 212항목을 다른 코더가 본문만 보고 분야·해외 주소·communication·기간을 코딩했다. 분야 일치 {g('r2_field')}(κ {g('r2_kappa')}; 분야마다 같은 수를 뽑은 층화 표본이므로, 분야별 정밀도를 실제 분야 비중으로 가중하면 {g('r2_weighted')}), 해외 주소 일치 {g('r2_foreign')}, communication 일치 {g('r2_comm')}, 기간 일치 {g('r2_term')}.",
                f"Fulin 재코딩(R3): 무작위 40건을 두 번째 코더가 같은 코드북으로 다시 코딩했다. 특권 여부 일치 {g('r3_kind')}, 기간 일치 {g('r3_term')}, 수혜자 유형 일치 {g('r3_btype')}.",
                f"Hulme 55건: 손으로 옮긴 표를 다른 코더가 쪽 이미지에서 따로 읽어 날짜 {g('hulme_date')}, 기간 {g('hulme_term')}가 일치했다. 10년 단위 건수는 Hulme 52쪽 표와 모두 같다(23·12·14·6·0)."]),
            ("선행 수치와의 대조", [
                f"Woodcroft 번호 항목은 1660–1799년 {c6099:,}건으로 MacLeod(1988)의 2,240건과 {abs(c6099 - 2240)}건, 1700–1850년 {c0050:,}건으로 Nuvolari 등(2021)의 13,070건과 {abs(c0050 - 13070)}건 차이가 난다. 두 연구의 세는 규칙(연장 포함 여부 등)을 확인하지 못해 차이의 원인은 가리지 않았다.",
                f"출판업조합 등록의 10년 합은 SRO 사이트의 검색 API로 잰 값(2026-11-03, data/sro/sro_site_decade_counts.csv)과 모든 10년에서 같다. Fulin 계수는 1492–1526년 {f9226}건으로 Kostylo(2010)의 254건보다 {254 - f9226}건 적다. 무엇을 특권으로 세었는지가 달라서일 수 있다."]),
            ("하지 않은 것", [
                "인과 추정은 하지 않는다. 1474·1624·1710년 같은 연도는 전후 비교의 기준일 뿐이다. 「법이 특허를 늘렸다」 같은 문장을 쓰지 않는다.",
                "베네치아 발명 특허의 건별 계수, 프랑스 왕실 특권, 1640년 이후의 출판업조합 등록, 미국 연방 특허(1790–)는 다음 판 후보다."]),
            ("판", ["1.0 (2026-11-03) 첫 공개.",
                   "1.0.1 (2026-11-03) 독립 검증 반영. 네덜란드 외국 출신 코드(8·9는 네덜란드인)를 바로잡았다. Woodcroft 17세기 기간 읽기(옛 철자·로마 숫자)와 여백 날짜 읽기를 고쳐 연도 공란을 없앴다. 여백 날짜 줄을 수혜자로 세던 오류와 런던 거리 이름을 해외 주소로 보던 오류를 고쳤다. 「마지막 21년 기간」 서술을 1617–1700년 표로 바꾸었다. 신뢰도 카드는 고친 값으로 다시 쟀다.",
                   "1.0.2 (2026-11-04) 본문의 서술 네 곳을 자료에 맞게 고쳤다. 연장 항목 비율의 분모(본문을 잃은 번호는 36개이고 분모에 남는다), 엘리자베스 시대 존속기간의 범위(6–30년), 18세기 이후 공동 허여 비율의 범위(3.6–17.1%), 기간 열 이름이다. 언어 전환 링크가 같은 면으로 가고, 표 머리글과 그래프 이름을 두 언어로 적었다. 비율은 백분율로 보이고 긴 값은 좁은 화면에서 줄을 바꾼다. 공개 저장소만으로 다시 만드는 절차를 고쳤다. 지표 값은 바뀌지 않았다."]),
        ],
        "en": [
            ("What was counted", [
                "English invention privileges and patents come from two lists: Hulme (1896, 1900), who drew 55 industrial monopoly grants of 1561–1603 from the calendars of the Patent Rolls, and Woodcroft (1854), whose chronological list numbers 1 to 14,359 for 1617–1852. 1604–1616 falls between the two lists. Hulme (1896) notes that a return of grants made before 1623, ordered by the Commons in 1827, was never presented.",
                f"The Stationers' Register is read straight from the Stationers' Register Online TEI (1557–1640, 10,453 entries). Venetian printing privileges are Fulin's 256 documents (1882), read and coded one by one. For {unstated} of those coded as privileges, Fulin's summary records the petition but not the grant; they were counted on the strength of the penalty clause or of editions 'con privilegio' cited in Fulin's notes, and the note column says so. The Dutch figures are a recount of the data published by Buning and Looijesteijn.",
                "Venetian invention patents were not counted here. The record-level source checked here is Berveglieri's printed calendar (2020); earlier, Mandich (1936, 1948) transcribed and classified 109 grants of 1474–1550 (Comino et al. 2017). Figures from the literature are marked 'secondary' and kept apart."]),
            ("Reading Woodcroft's list", [
                f"The word coordinates of the Internet Archive OCR were used to separate the margin column (surnames, sealing dates) from the text column (numbers and abstracts). Because numbers must run from 1 to 14,359, the longest rising chain of number-like lines was kept and candidates caught in its gaps were renumbered in order. 115 pages on which the OCR lost entry numbers were read again from the page images with tesseract 5. {miss} numbers still have no text: they are counted in the yearly totals (with their neighbors' year) and left out of metrics that need the text, except the share of extension entries, which keeps them in the denominator as entries that are not extensions and is therefore a lower bound.",
                f"Dates are the sealing dates printed in the margin. For {margin:,} entries the margin date is used as read. Margin dates damaged by the OCR ({ocr} entries) are used only when their year falls between the clean dates before and after, and the day is kept only when its digits are clean. For {page} entries whose margin date the OCR lost altogether, the date was read on the page image (data/coding/woodcroft_date_overrides.csv). Otherwise the neighbors' year was used when both neighbors agreed ({neigh:,} entries).",
                "A year that differs from both neighbors while they agree with each other is treated as an OCR misreading. Nos. 7046 and 7049 are printed '29th March 1835' in Woodcroft itself among entries of March 1836; they are taken as misprints and counted in 1836.",
                "A margin line containing digits is a date, not a grantee's surname: the number of grantees (shared grants) counts only margin lines without digits. An address abroad is a place outside the British Isles in the grantee's description; London street names such as 'Hanover Square' and memberships of foreign societies do not count.",
                f"The term is the first term stated in the abstract, read in early-modern spellings (fourteene, one and twentie), Roman numerals (xiiij, xxjtie) and OCR-damaged forms (xilij). Where an entry states further terms (mines, Ireland, a later revenue), they are kept in the column term_other ({multi} entries in 1617–1700). For nos. 1–126 (1617–1640) the first term agrees in every case with an independent reading of the page images. From about 1820 the abstracts stop stating the term, so later terms are left blank; the statutory 14 years was not assumed.",
                "Rents, provisos and foreign links are judged from the words of the abstract. The rent metric is the share of entries with rent wording, not a legal finding that rent was owed."]),
            ("Field classification", [
                "There are 17 fields. Word rules are applied to the title of the invention in a fixed order and the first match is taken. Entries before 1700 do not set the title off in quotation marks, so the whole abstract is used, after early-modern spellings are normalized.",
                "The rules were fixed before any results were seen but were revised three times before publication. r2 removed the bare word 'instrument' (any device, in 17th-century usage) from the instruments field; r3 added the spelling table and widened the text used for entries before 1700. These two followed an implausible first result.",
                f"Checked against an independent coder's recoding of 212 entries from the text (R2), the r3 rules agreed on {g('r2_dictr3_field')} and on only 2 of 11 mining entries: 'tan pits', 'pit coal' and 'smelting copper ore' had gone to mining and gas lighting to chemicals. After the r4 fix, precision was measured again on a fresh sample of 212 entries drawn with another seed (R2b), not on the sample that prompted the fix. The field figures on the reliability cards are from R2b. The revisions are recorded at the head of src/fields.py."]),
            ("Reliability cards", [
                f"Image check (R1): an independent coder read 120 entries, 30 per period, from the page images (number, date, number of grantees, 'communication', term) for comparison with the extracted values. Year agreement {g('r1_year')}, full date {g('r1_date')}, term {g('r1_term')}, number of grantees {g('r1_ngrantees')}, communication {g('r1_comm')}.",
                f"Text recoding (R2b): another coder coded 212 entries (11 per field, 25 'other') from the text alone: field, address abroad, communication, term. Field agreement {g('r2_field')} (κ {g('r2_kappa')}; the sample takes equal numbers per field, so per-field precision weighted by actual field shares gives {g('r2_weighted')}), address abroad {g('r2_foreign')}, communication {g('r2_comm')}, term {g('r2_term')}.",
                f"Fulin recoding (R3): a second coder recoded 40 random documents under the same codebook. Agreement on privilege or not {g('r3_kind')}, term {g('r3_term')}, beneficiary type {g('r3_btype')}.",
                f"Hulme's 55 grants: another coder read the page images independently; dates agree {g('hulme_date')} and terms {g('hulme_term')}. The decade counts match Hulme's own table on p. 52 (23, 12, 14, 6, 0)."]),
            ("Checks against prior figures", [
                f"Woodcroft's numbered entries come to {c6099:,} for 1660–1799 against MacLeod's (1988) 2,240 (a difference of {abs(c6099 - 2240)}), and {c0050:,} for 1700–1850 against the 13,070 of Nuvolari et al. (2021) (a difference of {abs(c0050 - 13070)}). The counting rules of those studies (whether extensions are included, for instance) were not checked, so the source of the differences is not settled.",
                f"The decade totals of the Stationers' Register match the counts returned by the SRO website's search API (2026-11-03; data/sro/sro_site_decade_counts.csv) in every decade. The Fulin count of {f9226} privileges for 1492–1526 is {254 - f9226} below Kostylo's (2010) 254, possibly because of what each counts as a privilege."]),
            ("What this site does not do", [
                "It makes no causal estimates. Years such as 1474, 1624 and 1710 are reference points for before-and-after comparison only; the site does not say that a law increased patenting.",
                "Record-level counts of Venetian invention patents, French royal privileges, the Stationers' Register after 1640 and United States federal patents (from 1790) are candidates for later versions."]),
            ("Versions", ["1.0 (2026-11-03) first release.",
                        "1.0.1 (2026-11-03) corrections after independent verification. The Dutch foreign-origin codes are read correctly (8 and 9 mark Dutch grantees). Woodcroft's 17th-century terms (old spellings, Roman numerals) and damaged margin dates are read better, leaving no entry without a year. Margin date lines are no longer counted as grantees, and London street names are no longer read as addresses abroad. The 'last 21-year term' statement is replaced by a table for 1617–1700. The reliability cards were measured again on the corrected values.",
                        "1.0.2 (2026-11-04) Four statements in the text now match the data: the denominator of the extension share (36 numbers lost their text, and they stay in the denominator), the range of Elizabethan terms (6–30 years), the range of the shared-grant share from the 18th century (3.6–17.1%) and the name of the term column. The language switch leads to the same page, and table headers and chart labels are given in each language. Shares are shown as percentages, and long values wrap on narrow screens. The steps to rebuild from the public repository were corrected. No metric values changed."]),
        ],
    }
    READING = {
        "ko": [
            ("특권은 어떻게 셀 수 있나", [
                "근대 특허법과 저작권법이 생기기 전, 새 기술이나 책에 대한 배타적 권리는 법률이 정한 권리가 아니라 군주·원로원·의회가 사람마다 내주는 특권이었다. 특권은 문서로 남았고, 19세기의 문서 정리자들이 그것을 목록으로 엮었다. 이 사이트는 그 목록을 건별로 세었다.",
                "목록마다 세는 단위가 다르다. Woodcroft는 특허 번호를, Hulme은 허여를, 출판업조합 등록부는 기재를, Fulin은 문서를 단위로 삼았다. 그래서 관할을 나란히 놓는 표에는 단위를 함께 적었다."]),
            ("1624년 전후", [
                "잉글랜드 독점법은 새 발명에 대한 특허를 14년 이하로 정했다. Woodcroft 목록에서 1617–1623년 허여는 대개 21년을 적고, 1625년 뒤 허여는 거의 모두 14년 이하를 적는다. 연평균 허여 수는 독점법 전후 7년씩을 비교하면 비슷하게 관측된다. 1630년대 들어 늘어난다."]),
            ("누가 받았나", [
                "엘리자베스 시대 허여의 상당수는 외국 장인에게 갔다. Hulme은 55건 가운데 21건을 외국인 허여로 셌다. 19세기에는 해외에서 전해진 발명을 대리인이 받는 「communication」 항목이 늘어난다. 네덜란드 1581–1621년 특권 문서에서는 출신이 외국으로 확인되는 수혜자가 있는 문서가 다섯에 하나 꼴이다."]),
            ("출판 쪽", [
                "런던 출판업조합 등록부에는 1557–1640년 1만여 건의 출판 허가가 기재되었다. 등록은 1637년에야 의무가 되었으므로 등록 수가 곧 출판 수는 아니다. 양도·공동 등록 표시가 1590년대 이후 늘어나는 것이 관측된다. 베네치아에서는 1490년대에 출판 특권이 몰리고, 그 가운데 열에 셋쯤이 저자에게 갔다."]),
            ("이 수치를 쓸 때", [
                "모든 수치는 지금까지 전하는 목록에서 센 것이다. 목록 바깥에서 내려진 특권, 기록이 사라진 특권은 들어 있지 않다. 지표마다 붙은 신뢰도 카드와 한계를 함께 읽기를 권한다."]),
        ],
        "en": [
            ("How privileges can be counted", [
                "Before modern patent and copyright law, an exclusive right in a new technique or a book was not a right set by statute but a privilege granted case by case by a ruler, a senate or a parliament. The grants left documents, and nineteenth-century archivists bound them into lists. This site counts those lists grant by grant.",
                "Each list counts in its own unit: Woodcroft numbers patents, Hulme counts grants, the Stationers' Register records entries and Fulin collects documents. Tables that set jurisdictions side by side therefore carry the unit with every figure."]),
            ("Before and after 1624", [
                "The Statute of Monopolies limited patents for new inventions to 14 years or less. In Woodcroft's list the grants of 1617–1623 mostly state 21 years, and almost all grants after 1625 state 14 years or less. Comparing seven years on either side, the yearly number of grants is about the same; it rises in the 1630s."]),
            ("Who received them", [
                "Many Elizabethan grants went to foreign craftsmen: Hulme counts 21 of 55 as grants to aliens. In the nineteenth century 'communication' entries, inventions communicated from abroad and taken out by an agent, become more frequent. About one Dutch privilege document of 1581–1621 in five names a grantee of known foreign origin."]),
            ("Printing", [
                "The register of the London Stationers' Company records some ten thousand permissions to publish in 1557–1640. Entrance became compulsory only in 1637, so entries are not a count of books printed. Entries marked as shared or reassigned grow from the 1590s. In Venice printing privileges bunch in the 1490s, and roughly three in ten of them went to authors."]),
            ("Using these numbers", [
                "Every figure is counted from a surviving list. Privileges granted outside these lists, or whose record is lost, are not in them. Please read the reliability card and the caveats that come with each metric."]),
        ],
    }
    return METHOD, READING
