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

```
pip install -r requirements.txt
python src/build_woodcroft.py      # needs the Internet Archive OCR files (djvu.xml) in data/raw/woodcroft/
python src/reocr_pages.py          # page images + tesseract 5 for pages where the OCR lost entry numbers
python src/enrich_woodcroft.py
python src/build_sro.py            # needs reg_A..reg_D-updated.xml from gbergel/SRO_data in data/raw/sro/current/
python src/build_fulin.py          # needs the Archivio Veneto 23 OCR text in data/raw/fulin/
python src/metrics.py
python src/reliability.py
python src/build_site.py
```

원자료 파일은 이 저장소에 넣지 않았다. 각 스크립트 머리에 원자료의 위치와 식별자를 적었다. The raw files are not in this repository; the head of each script names the source files and identifiers.

## 인용 · Citation

From Privilege to Patent, version 1.0.1 (2026), https://bowonkwon.github.io/Privilege-Metrics/

## 라이선스 · License

코드 MIT, 데이터·문서 CC BY 4.0, `data/sro/` 는 CC BY-SA 4.0. 자세한 것은 LICENSE.md. Code MIT; data and text CC BY 4.0; `data/sro/` CC BY-SA 4.0. See LICENSE.md.

[모든 공개 자료 · All public materials](https://bowonkwon.github.io/)
