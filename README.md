# 특권에서 특허로 · From Privilege to Patent

**사이트 · Site:** https://bowonkwon.github.io/Privilege-Metrics/ ([한국어](https://bowonkwon.github.io/Privilege-Metrics/ko/) · [English](https://bowonkwon.github.io/Privilege-Metrics/en/))

근대 특허·저작권 이전의 발명·출판 특권을 건별로 센 공개 데이터 사이트다. 잉글랜드 발명 특권·특허(1561–1603, 1617–1852), 런던 출판업조합 등록부(1557–1640), 베네치아 출판 특권(1469–1526), 네덜란드 발명 특권(1581–1621)을 같은 틀로 세고, 지표마다 정의·공식·한계·신뢰도 카드를 붙였다. 인과 추정은 하지 않는다.

A public data site that counts invention and printing privileges before modern patent and copyright law, grant by grant: English invention privileges and patents (1561–1603, 1617–1852), the London Stationers' Register (1557–1640), Venetian printing privileges (1469–1526) and Dutch invention privileges (1581–1621). Every metric comes with its definition, formula, caveats and a reliability card. No causal estimates are made.

## 자료원 · Sources

| 자료 · Source | 범위 · Coverage | 권리 · Rights |
|---|---|---|
| Bennet Woodcroft, *Titles of Patents of Invention, Chronologically Arranged* (1854) | 1617–1852, Nos. 1–14,359 | public domain |
| E. Wyndham Hulme, *Law Quarterly Review* 12 (1896), 16 (1900) | 1561–1603, 55 grants | public domain |
| R. Fulin, "Documenti per servire alla storia della tipografia veneziana", *Archivio Veneto* 23 (1882) | 1469–1526, 256 documents | public domain |
| G. Bergel & I. Gadd (eds.), *Stationers' Register Online* (TEI, GitHub gbergel/SRO_data) | 1557–1640, 10,453 entries | CC BY-SA (website) / CC BY 4.0 (TEI header) |
| M. Buning & H. Looijesteijn, "Patents in the Dutch Republic, 1581-1621", figshare, doi:10.6084/m9.figshare.16685788 | 1581–1621 | CC BY 4.0 (not redistributed here) |
| S. Comino, A. Galasso & C. Graziano, NBER WP 24118 (2017) | Venice 1474–1600 | quoted figures only |

## 폴더 · Layout

- `docs/` 사이트(GitHub Pages) · the site
- `data/` 지표 표와 레코드 표 · metric and record tables (`data/sro/` is CC BY-SA 4.0; everything else in `data/` is CC BY 4.0)
- `coding/` Hulme 전사, Fulin 코드북·코딩, 신뢰도 표본 · Hulme transcription, Fulin codebook and coding, reliability samples
- `src/` 파서·지표·사이트 생성 코드 · parsers, metric code, site builder

## 재현 · Reproducing

스크립트는 이 저장소의 구조(`data/`, `coding/`, `docs/`)를 알아보고 그대로 읽고 쓴다(`src/paths.py`). 필요한 입력이 없으면 건너뛰지 않고 오류로 멈춘다.
The scripts detect this repository's layout (`data/`, `coding/`, `docs/`; see `src/paths.py`) and read and write there. A missing required input stops the run with an error; nothing is skipped silently.

**지표·신뢰도 카드·사이트 다시 만들기 · Rebuilding the metrics, reliability cards and site** (from the record tables shipped here)

```
pip install -r requirements.txt
# Dutch data (CC BY 4.0, not redistributed here): Buning & Looijesteijn, figshare doi:10.6084/m9.figshare.16685788.v1,
# file 31787171 — save it as data/raw/buning/patents-dutch-republic-1581-1621.xlsx
python src/metrics.py        # data/woodcroft_entries.csv.gz, data/sro/sro_entries.csv.gz, coding/*.csv, the Buning xlsx -> data/m_*.csv
python src/reliability.py    # coding/reliability/*.csv -> data/reliability.json
python src/build_site.py     # -> docs/
```

**원자료부터 레코드 표 만들기 · Rebuilding the record tables from the raw sources** (raw files are not in this repository; the head of each script names the files and identifiers)

```
python src/build_woodcroft.py      # Internet Archive OCR (djvu.xml) in data/raw/woodcroft/ -> data/woodcroft_raw.csv, data/woodcroft_parse_log.json
python src/reocr_pages.py          # page images + tesseract 5 (--tesseract PATH or TESSERACT) for pages where the OCR lost entry numbers
python src/build_woodcroft.py      # again, now reading the re-OCR'd pages
python src/enrich_woodcroft.py     # -> data/woodcroft_entries.csv
python src/build_sro.py            # reg_A..reg_D-updated.xml from gbergel/SRO_data in data/raw/sro/current/ -> data/sro_entries.csv
python src/build_fulin.py          # Archivio Veneto 23 OCR text in data/raw/fulin/
```

then the three steps above. Uncompressed record tables written by these steps are read in preference to the shipped `.gz` copies.

## 인용 · Citation

From Privilege to Patent, version 1.0.4 (2026), https://bowonkwon.github.io/Privilege-Metrics/

## 라이선스 · License

코드 MIT, 데이터·문서 CC BY 4.0, `data/sro/` 는 CC BY-SA 4.0. 자세한 것은 LICENSE.md. Code MIT; data and text CC BY 4.0; `data/sro/` CC BY-SA 4.0. See LICENSE.md.

[모든 공개 자료 · All public materials](https://bowonkwon.github.io/)
