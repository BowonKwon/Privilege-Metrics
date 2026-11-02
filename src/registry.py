# -*- coding: utf-8 -*-
"""Metric registry — one entry per published metric, Korean and English. The site builder reads this file only.

reliability.kind
  exact      counted from a structured source (TEI, spreadsheet) or a hand transcription checked against page images
  ocr        counted from OCR'd page text by rule; the card gives the measured OCR / rule error on a checked sample
  sampled    a rule-based classification; the card gives precision measured on an independently coded sample
  secondary  quoted from the literature; not recounted here
Values for the cards are written by src/reliability.py into data/derived/reliability.json.
"""

SITE = {
    "ko": {"title": "특권에서 특허로", "subtitle": "근대 특허 이전, 베네치아·잉글랜드·네덜란드의 발명·출판 특권을 한 건씩 세다"},
    "en": {"title": "From Privilege to Patent", "subtitle": "Invention and printing privileges in Venice, England and the Dutch Republic before modern patents, counted one grant at a time"},
    "version": "1.0.1",
}

SERIES = {
    "A": {"ko": "수량", "en": "How many"},
    "B": {"ko": "분야", "en": "Which trades"},
    "C": {"ko": "사람", "en": "Who received them"},
    "D": {"ko": "조건", "en": "On what terms"},
    "P": {"ko": "출판 등록", "en": "Registering books"},
}

SOURCES = {
    "woodcroft": {
        "ko": "Bennet Woodcroft, *Titles of Patents of Invention, Chronologically Arranged, from March 2, 1617 (14 James I.) to October 1, 1852 (16 Victoriae)*, London: Eyre & Spottiswoode, 1854, 2 parts (Nos. 1–14,359). Internet Archive 스캔(일리노이대 소장본) `chronologicalin1617grea_0`·`chronologicalind1617grea` 의 OCR 단어 좌표로 항목을 갈랐고, OCR이 번호를 잃은 115쪽은 같은 쪽 이미지를 tesseract 5로 다시 읽었다.",
        "en": "Bennet Woodcroft, *Titles of Patents of Invention, Chronologically Arranged, from March 2, 1617 (14 James I.) to October 1, 1852 (16 Victoriae)*, London: Eyre & Spottiswoode, 1854, 2 parts (Nos. 1–14,359). Entries were split from the word coordinates of the Internet Archive OCR of the University of Illinois copy (`chronologicalin1617grea_0`, `chronologicalind1617grea`); 115 pages on which that OCR lost entry numbers were read again from the page images with tesseract 5.",
        "license": "public domain (1854)", "url": "https://archive.org/details/chronologicalin1617grea_0",
    },
    "hulme": {
        "ko": "E. Wyndham Hulme, 「The History of the Patent System under the Prerogative and at Common Law」, *Law Quarterly Review* 12 (1896) 141–154 와 「… A Sequel」, *LQR* 16 (1900) 44–56. 1561–1603년 산업 독점 허여 I–LV(55건) 목록과 52쪽 집계표. 목록을 쪽 이미지와 대조해 손으로 옮겼다.",
        "en": "E. Wyndham Hulme, 'The History of the Patent System under the Prerogative and at Common Law', *Law Quarterly Review* 12 (1896) 141–154, and '… A Sequel', *LQR* 16 (1900) 44–56: the list of industrial monopoly grants 1561–1603, Nos. I–LV (55 grants), and the summary table on p. 52, transcribed by hand and checked against the page images.",
        "license": "public domain (1896, 1900)", "url": "https://archive.org/details/sim_law-quarterly-review_1900-01_16_61",
    },
    "sro": {
        "ko": "Giles Bergel & Ian Gadd (eds.), *Stationers' Register Online*, CREATe, University of Glasgow. GitHub `gbergel/SRO_data` 의 원 등록부 대조판 TEI(`reg_A`–`reg_D-updated.xml`, 커밋 562db00, 2019-08-27). 사이트는 「CC-BY-SA licence」, TEI 머리말은 「Creative Commons Attribution」(CC BY 4.0)이라 적는다. 이 사이트는 더 엄격한 CC BY-SA 4.0 으로 항목 표를 배포한다.",
        "en": "Giles Bergel & Ian Gadd (eds.), *Stationers' Register Online*, CREATe, University of Glasgow. TEI of the register volumes corrected against the manuscripts, GitHub `gbergel/SRO_data` (`reg_A`–`reg_D-updated.xml`, commit 562db00, 2019-08-27). The project website states a 'CC-BY-SA licence'; the TEI header states 'Creative Commons Attribution' (CC BY 4.0). This site distributes its entry table under the stricter CC BY-SA 4.0.",
        "license": "CC BY-SA 4.0 (entry table)", "url": "https://stationersregister.online",
    },
    "fulin": {
        "ko": "Rinaldo Fulin, 「Documenti per servire alla storia della tipografia veneziana」, *Archivio Veneto* 23 (1882), 문서 1–256(1469–1526). Internet Archive `ArchivioVeneto23` OCR. 특권 여부·존속기간·수혜자 유형은 사전 등록한 코드북으로 문서마다 읽어 코딩했다.",
        "en": "Rinaldo Fulin, 'Documenti per servire alla storia della tipografia veneziana', *Archivio Veneto* 23 (1882), documents 1–256 (1469–1526), Internet Archive `ArchivioVeneto23` OCR. Whether a document is a privilege, its term and the beneficiary type were coded document by document under a codebook fixed before coding.",
        "license": "public domain (1882)", "url": "https://archive.org/details/ArchivioVeneto23",
    },
    "buning": {
        "ko": "Marius Buning & Henk Looijesteijn, 「Patents in the Dutch Republic, 1581-1621」, figshare, 2021, doi:10.6084/m9.figshare.16685788.v1 (CC BY 4.0). Buning, *Knowledge, Patents, Power* (Brill, 2021)의 자료. 문서 성격 코드 3(특권 허여)만 셌다.",
        "en": "Marius Buning & Henk Looijesteijn, 'Patents in the Dutch Republic, 1581-1621', figshare, 2021, doi:10.6084/m9.figshare.16685788.v1 (CC BY 4.0), the data behind Buning, *Knowledge, Patents, Power* (Brill, 2021). Only documents with 'Nature of contact' code 3 (privilege issued) are counted.",
        "license": "CC BY 4.0", "url": "https://doi.org/10.6084/m9.figshare.16685788.v1",
    },
    "comino": {
        "ko": "Stefano Comino, Alberto Galasso & Clara Graziano, 「The Diffusion of New Institutions: Evidence from Renaissance Venice's Patent System」, NBER Working Paper 24118 (2017). 베네치아 원로원 특허의 기간별 건수(7쪽)·분야표(표 A1, Berveglieri 1995 자료)·외국인 비율. 2차 인용으로만 싣는다.",
        "en": "Stefano Comino, Alberto Galasso & Clara Graziano, 'The Diffusion of New Institutions: Evidence from Renaissance Venice's Patent System', NBER Working Paper 24118 (2017): period counts of Venetian Senate patents (p. 7), the sector table (Table A1, from Berveglieri 1995) and the share of foreign inventors. Quoted as secondary figures only.",
        "license": "quotation", "url": "https://www.nber.org/papers/w24118",
    },
}

PRIOR = {
    "comino_counts": {"ko": "베네치아 원로원 특허: 1474년 이전 임시 특권 5건(Mandich 1936), 1474–1500년 43건, 1501–1550년 126건, 1551–1600년 471건.",
                      "en": "Venetian Senate patents: 5 ad hoc privileges before 1474 (Mandich 1936), 43 in 1474–1500, 126 in 1501–1550, 471 in 1551–1600.",
                      "cite": "Comino, Galasso & Graziano (2017), NBER WP 24118, p. 7."},
    "kostylo_counts": {"ko": "같은 기간을 Berveglieri 1995(21–22쪽)에 기대어 원로원 단독 33·116·461건으로 적는다. 앞의 세 값과 정확히 10건씩 차이가 나며, 이 사이트는 어느 쪽이 맞는지 판정하지 않았다.",
                       "en": "Citing Berveglieri 1995 (pp. 21–22), gives 33, 116 and 461 grants by the Senate alone for the same periods. Each is exactly 10 below the figures above; this site has not settled which is right.",
                       "cite": "Kostylo, J. (2010), 'From gunpowder to print', in Deazley, Kretschmer & Bently (eds.), Privilege and Property, Open Book Publishers, n. 5."},
    "berveglieri_total": {"ko": "1474–1788년 원로원(Terra) 특허 2,130건.", "en": "2,130 patents granted by the Senate (Terra), 1474–1788.",
                          "cite": "Berveglieri, R. (2020), «Ingegnosi artificij», vol. 1, Cierre, preface."},
    "comino_foreign": {"ko": "1474–1550년 169건 중 외국인(이탈리아인이 아닌 사람)에게 간 것 6.5%.", "en": "6.5% of the 169 patents of 1474–1550 went to foreign (non-Italian) inventors.",
                       "cite": "Comino, Galasso & Graziano (2017), pp. 21–22."},
    "hulme_table": {"ko": "1561–1603년 55건: 외국인 21·내국인 30·거래 규제 4.", "en": "55 grants 1561–1603: 21 to aliens, 30 to natives, 4 for regulating trade.",
                    "cite": "Hulme (1900), LQR 16, p. 52."},
    "macleod": {"ko": "1660–1799년 특허 2,240건(2차 인용).", "en": "2,240 patents in 1660–1799 (secondary citation).",
                "cite": "MacLeod, C. (1988), Inventing the Industrial Revolution, CUP, Table 9.1, p. 160 (as quoted by Nuvolari, Tartari & Tranchero 2021)."},
    "ntt": {"ko": "1700–1850년 잉글랜드 특허 13,070건.", "en": "13,070 English patents granted in 1700–1850.",
            "cite": "Nuvolari, A., Tartari, V. & Tranchero, M. (2021), 'Patterns of innovation during the Industrial Revolution', Explorations in Economic History 82; LEM WP 2020/23, p. 2."},
    "doorman": {"ko": "네덜란드 1515–1797년 특허 관련 신청 952건(카를 5세·펠리페 2세 23, 연방의회 574, 주 의회 355; 2차 인용).",
                "en": "952 Dutch patent applications 1515–1797 (23 under Charles V and Philip II, 574 States General, 355 provincial States; secondary citation).",
                "cite": "Doorman, G. (1940), Octrooien voor uitvindingen in de Nederlanden, as summarised in the review in Maandblad Oud-Utrecht, Sept. 1941."},
    "kostylo_printing": {"ko": "1492–1526년 베네치아 출판 특권 254건, 그중 저자에게 79건(약 30%).", "en": "254 Venetian printing privileges 1492–1526, 79 of them (about 30%) to authors.",
                         "cite": "Kostylo (2010), nn. 17–19, from Fulin (1882)."},
}

M = []


def metric(**kw):
    M.append(kw)


metric(id="a1_annual", series="A", table="m_a1_annual", unit="grants", fmt=",.0f", sources=["hulme", "woodcroft"], prior=["macleod", "ntt"],
       rel="ocr",
       ko=dict(name="잉글랜드 연도별 발명 특권·특허 수", definition="그해 내려진 새 발명 특권·특허의 수. 1561–1603년은 Hulme 목록, 1617–1852년은 Woodcroft 목록의 번호 항목에서 기간 연장(extension)을 뺀 수.",
               formula="허여 수(연) = Hulme 건수 + Woodcroft 항목 수 − 연장 항목 수", reading="1604–1616년은 이 사이트가 쓰는 두 목록(Hulme은 1603년까지, Woodcroft는 1617년부터) 사이라 비워 두었다. 0이 아니라 「모름」이다.",
               caveat="Woodcroft 번호는 허여일 순서이고 날짜는 여백의 날인일이다. OCR이 번호를 잃은 항목은 앞뒤 항목의 연도로 셌다. 1853년 2건은 1852년법 이전 출원의 날인분이다."),
       en=dict(name="Invention grants per year, England", definition="New invention privileges and patents granted in the year: Hulme's list for 1561–1603; for 1617–1852 the numbered entries of Woodcroft's list less those granting an extension.",
               formula="grants(year) = Hulme grants + Woodcroft entries − extension entries", reading="1604–1616 is blank because it falls between the two lists used here (Hulme ends in 1603, Woodcroft begins in 1617). Blank means unknown, not zero.",
               caveat="Woodcroft numbers follow the date of the grant; the date used is the sealing date printed in the margin. Entries whose number the OCR lost are counted in the year of their neighbours. The two grants of 1853 are sealings of applications made under the law before 1852."))
metric(id="a2_periods", series="A", table="m_a2_periods", unit="grants", fmt=",.0f", sources=["hulme", "woodcroft", "fulin", "buning", "comino"], prior=["comino_counts", "kostylo_counts", "berveglieri_total", "doorman"],
       rel="secondary",
       ko=dict(name="관할별 기간 비교", definition="같은 반세기 구간에 잉글랜드(자체 계수)·네덜란드(Buning 자료 재계수)·베네치아(문헌 수치)의 특권 수를 나란히 놓은 표.",
               formula="구간별 합계, 세는 단위를 열로 표시", reading="세는 단위가 다르다. 베네치아 발명은 원로원 허여(2차 인용), 네덜란드는 특권 허여 문서, 잉글랜드는 허여, 베네치아 출판은 Fulin 문서다.",
               caveat="베네치아 발명 수치는 이 사이트가 세지 않았다. 두 계열(43·126·471 과 33·116·461)이 10건씩 어긋난다. 잉글랜드 1551–1600 은 1561년부터이고, Hulme의 55건에는 거래 규제 허여 4건이 들어 있다. 1601–1650 은 1604–1616 공백을 포함한다."),
       en=dict(name="Jurisdictions compared by period", definition="Privileges per half-century for England (our count), the Dutch Republic (our recount of the Buning data) and Venice (figures quoted from the literature), side by side.",
               formula="sum per period, with the counting unit in its own column", reading="The units differ: Venetian inventions are Senate grants (secondary), Dutch figures are documents issuing a privilege, English figures are grants, Venetian printing figures are Fulin documents.",
               caveat="The Venetian invention figures were not counted here, and the two published series (43, 126, 471 and 33, 116, 461) differ by 10 in each period. England 1551–1600 starts in 1561, and Hulme's 55 include four grants for regulating trade; 1601–1650 includes the 1604–1616 gap."))
metric(id="a3_1624", series="A", table="m_a3_1624", unit="grants per year", fmt=".1f", sources=["woodcroft"], prior=[],
       rel="ocr",
       ko=dict(name="1624년 독점법 전후", definition="독점법(Statute of Monopolies, 21 Jac. I c. 3)이 나온 1624년 앞뒤 7년씩의 연평균 허여 수와, 본문에 적힌 존속기간.",
               formula="연평균 = 구간 허여 수 ÷ 7, 95% 구간은 포아송 정확 구간", reading="1617–1623년과 1625–1631년의 연평균이 비슷하게 관측된다. 본문에 적힌 존속기간의 중앙값은 1617–1623년 21년, 1625–1640년 14년이다. 1624년 앞에도 14년 이하가 있고 뒤에도 21년이 남는다.",
               caveat="전후 비교일 뿐이다. 법이 수를 바꾸었다는 뜻이 아니다. 1617년 이전 목록은 1603년에서 끊긴다."),
       en=dict(name="Before and after the Statute of Monopolies (1624)", definition="Mean grants per year in the seven years before and after 1624, the year of the Statute of Monopolies (21 Jac. I c. 3), and the terms written in the entries.",
               formula="mean per year = grants in window ÷ 7; 95% interval = exact Poisson interval", reading="The yearly means of 1617–1623 and 1625–1631 are about the same. The median term written in the entries is 21 years in 1617–1623 and 14 in 1625–1640; some terms of 14 or less come before 1624 and some 21-year terms after it.",
               caveat="A before-and-after comparison only; it does not say the Statute changed the number. The list before 1617 stops in 1603."))
metric(id="a4_extensions", series="A", table="m_a4_extensions", unit="share", fmt=".1%", sources=["woodcroft"], prior=[],
       rel="ocr",
       ko=dict(name="기간 연장 항목 비율", definition="Woodcroft 번호 항목 가운데 기존 특허의 기간 연장·확인을 내준 항목의 비율(10년 단위).",
               formula="연장 항목 수 ÷ 항목 수", reading="연장은 드물다. 전체 항목의 1%가 안 된다.",
               caveat="본문에 extension·prolongation·confirmation 이 들어간 항목을 셌다. OCR로 본문이 사라진 136번호는 분모에서 빠진다."),
       en=dict(name="Share of extension entries", definition="Share of Woodcroft's numbered entries that grant an extension or confirmation of an earlier patent, by decade.",
               formula="extension entries ÷ entries", reading="Extensions are rare: under 1% of all entries.",
               caveat="Counts entries whose text contains 'extension', 'prolongation' or 'confirmation'. The 136 numbers whose text the OCR lost are left out of the denominator."))
metric(id="b1_fields", series="B", table="m_b1_fields", unit="share", fmt=".1%", sources=["woodcroft", "hulme"], prior=[],
       rel="sampled",
       ko=dict(name="분야 구성", definition="허여된 발명의 분야 비율. 분야는 발명 명칭에 사전 등록한 단어 규칙을 차례로 적용해 처음 맞는 것으로 정했다.",
               formula="구간·분야별 건수 ÷ 구간 건수(「기타」 포함)", reading="1617–1649년에는 양수·배수, 금속, 광업이, 1820년 이후에는 직물·운송·증기가 큰 몫을 차지한다.",
               caveat="명칭의 단어로 분류하므로 한 발명이 두 분야에 걸치면 순서가 앞선 분야로 간다. 「기타」는 규칙에 걸리지 않은 것이다. 독립 코더가 본문을 읽고 매긴 분야와는 약 3분의 2가 일치한다(신뢰도 카드). 분야 비율은 대략의 구성으로 읽고, 분야 하나의 작은 증감에 무게를 두지 않는다. Hulme 1561–1603 은 같은 사전을 명칭에 적용했다."),
       en=dict(name="Field composition", definition="Share of granted inventions by field. The field is the first match of a pre-registered list of word rules applied to the title of the invention.",
               formula="count in field and period ÷ count in period (including 'other')", reading="In 1617–1649 water raising and drainage, metals and mining take large shares; after 1820, textiles, transport and steam.",
               caveat="Classification uses the words of the title, so an invention that spans two fields goes to the one earlier in the list. 'Other' is what no rule matched. The rules agree with an independent coder reading the text on about two entries in three (see the reliability card), so read the shares as a rough composition and do not weigh small changes in a single field. For Hulme 1561–1603 the same rules were applied to the subject line."))
metric(id="b2_hhi", series="B", table="m_b2_hhi", unit="HHI", fmt=".3f", sources=["woodcroft"], prior=[],
       rel="sampled",
       ko=dict(name="분야 집중도", definition="10년마다 분류된 허여의 분야 점유율 제곱합(허핀달 지수). 「기타」는 빼고 계산한다.",
               formula="HHI = Σ (분야 점유율)²", reading="값이 클수록 몇 분야에 몰려 있다. 1/17≈0.059 이 17분야 균등의 하한이다.",
               caveat="초기 수십 년은 허여 수가 적어 값이 크게 흔들린다. 분야 분류의 정밀도가 약 3분의 2라는 한계를 그대로 물려받는다."),
       en=dict(name="Field concentration", definition="Herfindahl index of field shares among classified grants in each decade, 'other' excluded.",
               formula="HHI = Σ (field share)²", reading="Higher means grants concentrate in fewer fields. With 17 fields an even spread gives 1/17 ≈ 0.059.",
               caveat="The early decades have few grants, so the index swings widely. The index inherits the field classification's precision of about two in three."))
metric(id="b3_venice_sectors", series="B", table="m_b3_venice_sectors", unit="patents", fmt=",.0f", sources=["comino"], prior=["comino_counts"],
       rel="secondary",
       ko=dict(name="베네치아 1474–1550 분야표(2차 인용)", definition="Comino 등의 표 A1(Berveglieri 1995 분류) 169건을 이 사이트의 분야 사전에 대응시킨 표.",
               formula="문헌의 분야 → 이 사이트 분야(대응은 우리 판단)", reading="방아류가 절반쯤이다. 배수·준설, 양수 펌프가 뒤를 잇는다.",
               caveat="건수는 문헌 그대로다. 대응표만 이 사이트가 만들었다."),
       en=dict(name="Venice 1474–1550 by sector (secondary)", definition="The 169 patents of Table A1 in Comino et al. (sectors of Berveglieri 1995), mapped to this site's field list.",
               formula="published sector → this site's field (the mapping is ours)", reading="Mills make up about half, followed by drainage and dredging and by pumps.",
               caveat="Counts are as published; only the mapping is ours."))
metric(id="c1_foreign", series="C", table="m_c1_foreign_gb", unit="share", fmt=".1%", sources=["woodcroft", "hulme", "buning", "comino"], prior=["hulme_table", "comino_foreign"],
       rel="sampled",
       ko=dict(name="외국 연관 비율", definition="잉글랜드 1617–1852: 본문에 「communication」(해외에서 전해진 발명)이 있거나 수혜자 주소가 브리튼 제도 밖인 허여의 비율. 1561–1603은 Hulme의 외국인 집계와 그의 주석으로 우리가 다시 코딩한 값. 네덜란드는 Buning 자료의 출신국 코드.",
               formula="외국 연관 허여 ÷ 허여(10년 단위), 95% 윌슨 구간", reading="잉글랜드에서는 1810년대부터 「communication」 항목이 늘어 1840–50년대 허여의 약 다섯에 하나가 외국과 이어진다.",
               caveat="관할마다 외국인의 정의가 다르다. 잉글랜드 수치는 주소와 문구로 잡은 하한이다. 국적은 적혀 있지 않다. Hulme 주석으로 잡은 외국인은 Hulme 자신의 21건보다 적다. 네덜란드는 Buning 코드 1–6(출신국이 적힌 외국)을 외국으로, 7(외국 출신 추정)을 따로 셌다. 8·9는 네덜란드인이다."),
       en=dict(name="Foreign links", definition="England 1617–1852: share of grants whose text says 'communication' (an invention communicated from abroad) or whose grantee lives outside the British Isles. 1561–1603: Hulme's alien count and our recoding from his notes. Dutch Republic: origin code in the Buning data.",
               formula="grants with a foreign link ÷ grants, by decade; 95% Wilson interval", reading="In England 'communication' entries grow from the 1810s; by the 1840s–50s about one grant in five has a foreign link.",
               caveat="Each jurisdiction defines 'foreign' differently. The English figure is a lower bound read from addresses and wording; nationality is not recorded. Our recoding from Hulme's notes finds fewer aliens than Hulme's own 21. For the Dutch Republic, Buning's codes 1–6 (a named foreign origin) count as foreign and code 7 (probably of foreign extraction) is shown separately; codes 8 and 9 mark Dutch grantees."))
metric(id="c2_cogrant", series="C", table="m_c2_cogrant", unit="share", fmt=".1%", sources=["woodcroft", "buning"], prior=[],
       rel="ocr",
       ko=dict(name="공동 수혜 비율", definition="수혜자가 둘 이상인 허여의 비율. 잉글랜드는 Woodcroft 여백에 찍힌 성(姓)의 수로 센다.",
               formula="수혜자 ≥ 2 인 허여 ÷ 허여", reading="1617–1649년에는 열에 넷 꼴로 공동 허여다. 18세기 이후는 10년 단위로 5–19% 사이를 오간다.",
               caveat="여백의 성이 OCR에서 빠지거나 둘로 갈리면 값이 흔들린다. 여백 성이 하나도 안 잡힌 항목은 분모에서 뺐다."),
       en=dict(name="Shared grants", definition="Share of grants with two or more grantees. For England the count is the number of surnames printed in Woodcroft's margin.",
               formula="grants with ≥ 2 grantees ÷ grants", reading="In 1617–1649 about four grants in ten are shared; from the 18th century the decade share moves between 5% and 19%.",
               caveat="A margin surname dropped or split by the OCR moves the value. Entries with no margin surname read are left out."))
metric(id="d1_terms", series="D", table="m_d1_terms", unit="years", fmt=".0f", sources=["hulme", "woodcroft", "fulin", "buning"], prior=[],
       rel="sampled",
       ko=dict(name="존속기간 분포", definition="허여 문서에 적힌 존속기간(년). 적혀 있지 않은 것은 채우지 않는다.",
               formula="기간이 적힌 허여의 중앙값·사분위·값별 건수", reading="엘리자베스 시대는 7–21년으로 흩어진다. 1624년 뒤 잉글랜드는 14년으로 모인다. 네덜란드와 베네치아 출판 특권은 10년 안팎이 많다.",
               caveat="Woodcroft 1820년 이후 항목은 기간을 적지 않아 비어 있다. 법정 기간(14년)을 가정해 채우지 않았다."),
       en=dict(name="Terms granted", definition="Term in years written in the grant. Terms not written are left blank, not filled in.",
               formula="median, quartiles and counts by value among grants with a stated term", reading="Elizabethan terms spread from 7 to 21 years; after 1624 English terms gather at 14. Dutch and Venetian printing terms cluster around 10.",
               caveat="Woodcroft's entries from about 1820 do not state the term, so those years are empty. The statutory 14 years was not assumed."))
metric(id="d2_term_shift", series="D", table="m_d2_term_shift", unit="grants", fmt=",.0f", sources=["woodcroft"], prior=[],
       rel="ocr",
       ko=dict(name="21년에서 14년으로", definition="1617–1700년 해마다 본문에 적힌 첫 기간이 21년인 허여와 14년 이하인 허여의 수.",
               formula="연도별 건수", reading="1624년 뒤로 14년 이하가 대부분이 되지만 21년도 드물게 남는다.",
               caveat="독점법 제6조는 새 발명 특허를 14년 이하로 정했다. 이 표는 기록에 적힌 기간을 셀 뿐이다. 한 항목에 광산권·아일랜드·뒤따르는 수익권처럼 다른 기간이 함께 적힌 경우(other_term)는 첫 기간으로 셌다."),
       en=dict(name="From 21 years to 14", definition="Grants per year 1617–1700 whose first written term is 21 years, and whose first written term is 14 years or less.",
               formula="counts per year", reading="After 1624 terms of 14 years or less become the rule, but a few 21-year terms remain.",
               caveat="Section 6 of the Statute of Monopolies limited patents for new inventions to 14 years or less. The table only counts the terms written in the record. Where an entry states further terms (mines, Ireland, a later revenue; column other_term), the first is counted."))
metric(id="d3_clauses", series="D", table="m_d3_clauses", unit="share", fmt=".1%", sources=["woodcroft"], prior=[],
       rel="ocr",
       ko=dict(name="지대·단서 조항", definition="1617–1759년 Woodcroft 항목 요약에 왕실에 바치는 지대(rent)나 단서·무효 조항(proviso, void)이 언급된 비율.",
               formula="조항 언급 항목 ÷ 항목(10년 단위)", reading="1640년대까지는 열에 일곱 꼴로 지대 문구가 있다. 1660–1670년대에는 열에 하나로 줄고 1680년대부터는 거의 보이지 않는다.",
               caveat="Woodcroft의 요약에 적힌 문구로만 센다. 특허장 원문의 조항을 다 담았다는 보장은 없다."),
       en=dict(name="Rent and proviso clauses", definition="Share of Woodcroft entries 1617–1759 whose summary mentions a rent to the Crown or a proviso or voidance clause.",
               formula="entries mentioning the clause ÷ entries, by decade", reading="Up to the 1640s about seven entries in ten mention a rent; in the 1660s and 1670s about one in ten, and from the 1680s almost none.",
               caveat="Counts only what Woodcroft's summary says; the summaries need not carry every clause of the letters patent."))
metric(id="p1_sro_annual", series="P", table="m_p1_sro_annual", unit="entries", fmt=",.0f", sources=["sro"], prior=[],
       rel="exact",
       ko=dict(name="런던 출판업조합 등록 수", definition="해마다 출판업조합 등록부에 기재된 출판 허가(copy entry) 수.",
               formula="연도별 항목 수(SRO 정렬 날짜 기준)", reading="1560년대 1,226건, 1630년대 1,637건으로 10년마다 1천 건 안팎이다.",
               caveat="1571년 7월–1576년 7월 기재는 남아 있지 않다. 1637년 전에는 등록이 의무가 아니었다(SRO). 등록 수는 출판된 책 수가 아니다."),
       en=dict(name="Stationers' Register entries per year", definition="Copy entries (permissions to publish) made in the register of the Stationers' Company each year.",
               formula="entries per year by the SRO sort date", reading="About a thousand or more entries per decade: 1,226 in the 1560s, 1,637 in the 1630s.",
               caveat="No entries survive for July 1571 to July 1576. Before 1637 entrance was not compulsory (SRO). Entries are not a count of books printed."))
metric(id="p2_sro_concentration", series="P", table="m_p2_sro_concentration", unit="HHI", fmt=".3f", sources=["sro"], prior=[],
       rel="exact",
       ko=dict(name="등록자 집중도", definition="해마다 등록자별 점유율의 허핀달 지수와 상위 5인 점유율. 등록자가 여럿이면 한 항목을 나누어 센다.",
               formula="HHI = Σ (등록자 점유율)², 등록자는 SRO 이름 키", reading="상위 5인이 해마다 등록의 몇 할을 차지했는지 본다.",
               caveat="SRO의 이름 키를 그대로 썼다. 같은 사람이 다른 키로 적혔으면 집중도가 낮게 나온다."),
       en=dict(name="Concentration of enterers", definition="Herfindahl index of enterer shares each year, and the share of the top five. An entry with several enterers is split among them.",
               formula="HHI = Σ (enterer share)²; enterers keyed by the SRO name key", reading="Shows how much of each year's entries the top five stationers made.",
               caveat="SRO name keys are used as given; a person recorded under two keys lowers the measured concentration."))
metric(id="p3_sro_status", series="P", table="m_p3_sro_status", unit="share", fmt=".1%", sources=["sro"], prior=[],
       rel="exact",
       ko=dict(name="공동 등록·양도 비율", definition="10년마다 SRO가 「shared」(둘 이상이 등록)·「reassigned」(다른 사람에게 넘김)·「cancelled」(말소)로 표시한 항목의 비율.",
               formula="표시 항목 ÷ 항목", reading="양도 표시는 1580년대 2% 미만에서 1620년대 10%로 늘어난다.",
               caveat="SRO 편자의 상태 판정을 그대로 썼다. 한 항목에 표시가 여럿일 수 있다."),
       en=dict(name="Shared, reassigned and cancelled entries", definition="Share of entries per decade that SRO marks 'shared' (entered by more than one person), 'reassigned' (made over to another) or 'cancelled'.",
               formula="marked entries ÷ entries", reading="Entries marked reassigned grow from under 2% in the 1580s to 10% in the 1620s.",
               caveat="The status is the SRO editors' judgment, used as given; an entry may carry several marks."))
metric(id="p4_sro_fees", series="P", table="m_p4_sro_fees", unit="share", fmt=".1%", sources=["sro"], prior=[],
       rel="exact",
       ko=dict(name="등록 수수료", definition="수수료가 적힌 항목 가운데 6펜스인 항목의 비율과 수수료 중앙값(연도별).",
               formula="6펜스 항목 ÷ 수수료 적힌 항목", reading="SRO는 1582년까지 쪽수로 매기다 1587년부터 6펜스가 표준이 되었다고 적는다. 그 이행이 연도별로 보인다.",
               caveat="여러 저작을 한 번에 등록하면 수수료가 6펜스의 배수가 된다."),
       en=dict(name="Entrance fees", definition="Share of entries with a stated fee whose fee is 6d, and the median fee, by year.",
               formula="entries at 6d ÷ entries with a fee", reading="SRO notes that fees were reckoned by the number of sheets until 1582 and that 6d became standard from 1587; the change shows year by year.",
               caveat="Entering several works at once gives a multiple of 6d."))
metric(id="v1_venice_printing", series="P", table="m_v1_fulin_annual", unit="privileges", fmt=",.0f", sources=["fulin"], prior=["kostylo_printing"],
       rel="sampled",
       ko=dict(name="베네치아 출판 특권", definition="Fulin이 모은 1469–1526년 문서 가운데 출판 특권(배타적 인쇄·판매·활자 사용 허가)을 내준 문서의 연도별 수와 수혜자 유형.",
               formula="연도별 특권 문서 수, 저자·인쇄업자 구분", reading="5년 구간으로 1495–1499년이 가장 많고 1510–1514년이 가장 적다. 1515년 뒤로 다시 늘어난다.",
               caveat="Fulin은 남은 문서만 모았다. 그 스스로 모든 특권의 기록이 남은 것은 아니라고 적었다."),
       en=dict(name="Venetian printing privileges", definition="Documents in Fulin's collection (1469–1526) that grant a printing privilege (an exclusive right to print, sell or use a type), per year and by type of beneficiary.",
               formula="privilege documents per year, split author / printer", reading="By five-year period the most are in 1495–1499 and the fewest in 1510–1514; numbers rise again after 1515.",
               caveat="Fulin collected the documents that survive; he notes that not every privilege granted left a record."))

METRICS = {m["id"]: m for m in M}
