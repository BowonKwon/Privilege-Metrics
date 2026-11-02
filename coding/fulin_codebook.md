# Fulin 1882 coding — codebook v1.0 (fixed 2026-11-03 before coding)

Source: R. Fulin, "Documenti per servire alla storia della tipografia veneziana", *Archivio Veneto* 23 (1882), documents 1–256 (1469–1526). Fulin prints a number, the date (modern year first; Venetian-style year "m. v." in brackets), the archive series — N. C. (Collegio, Notatorio), S. T. (Senato, Terra), N. C. X. (Capi del Consiglio dei Dieci, Notatorio) — and either the text of the act or his Italian summary, followed by notes.

One row per Fulin number, 1..256. Columns:

| column | values | rule |
|---|---|---|
| number | 1–256 | Fulin's number |
| date | YYYY-MM-DD | modern year (the first year Fulin gives). If the OCR year is garbled, use the "m. v." year (+1 for Jan–Feb dates) or the chronological order; write the reason in `note` |
| series | NC / ST / NCX / other | as printed |
| kind | privilege / refusal / other | privilege = an exclusive right (to print, sell or import a work or works, or to use a type, technique or process for books, music or prints) granted or confirmed by a Venetian body. refusal = a request for such a right that the act denies or does not grant. other = everything else (contracts, wills, general laws, revocations, censorship licences without exclusivity, letters) |
| general_law | yes / no | yes when the act is a general rule for the trade rather than a grant to a person (e.g. 1517 revocation, 1526 licence rule) |
| term_years | number or blank | term stated in the act or summary ("per anni dieci", "annos decem", "per anni X"). Blank when not stated. For "per la vita" write `life` |
| beneficiary | short name as in the text | first named beneficiary; add "et al." if several |
| n_beneficiaries | integer | persons named as beneficiaries |
| beneficiary_type | author / printer / both / other | author = author, editor, translator, commentator or heirs of one; printer = printer, publisher, bookseller, typefounder; both = the text says the person is both; other = artist, engraver, nobleman, cleric etc. when not one of the above |
| object | book / type_technique / print_image / music / other | what the right covers |
| penalty | yes / no | a penalty for infringers (fine, confiscation) is stated |
| place_origin | as stated (e.g. "da Brescia", "ferrarese", "tedesco") or blank | origin of the first beneficiary when the text gives it |
| quote | ≤ 20 words copied from the OCR text | the words that support `kind` and `term_years` |
| note | free | OCR problems, dating reasoning, uncertainty |
| confidence | high / medium / low | |

Do not use any knowledge outside the text. When the text does not say, leave the cell blank.
