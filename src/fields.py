# -*- coding: utf-8 -*-
"""Field (sector) dictionary for invention privileges — fixed 2026-11-03 BEFORE any field counts were looked at.

A record is assigned the FIRST field in FIELDS whose pattern matches its title text (lower case).
Order encodes priority: specific trades before generic words ('steam engine for draining mines' -> mining,
'mill for grinding corn' -> food? no: mills come before food, so -> mills). Changing the order or the patterns
after counts have been seen requires a new site version and a note on the method page.
Records with no match are 'other'. The share of 'other' is published with every field chart.

Revision log
  r1 2026-11-03  first version.
  r2 2026-11-03  (before publication, after the first field counts were seen) the bare word 'instrument' was removed
                 from the clocks/instruments rule: in 17th-century grants 'engine or instrument' means any device, and
                 r1 made 'clocks, instruments and music' the largest field of 1617-1649. Only qualified instruments
                 (mathematical, musical, optical, surgical, nautical, philosophical, astronomical, drawing, surveying)
                 now count. No other rule was changed.
  r3 2026-11-03  (before publication) early-modern spellings are normalised before matching (OLD_SPELLINGS), and
                 entries dated before 1700 are classified on their whole text (they rarely carry addresses), because
                 their titles are not set off by quotation marks and the r2 title cut often dropped the object.
                 After r2, 45% of 1617-1649 grants were 'other'. No rule pattern was changed.
  r4 2026-11-03  (before publication) after the first independent text recoding of 212 entries (R2: field agreement
                 144/212 = 68%; mining 2/11): mining no longer matches bare 'pit(s)', 'mineral' or 'ore(s)' ('tan pits',
                 'pit coal', 'smelting copper ore' had gone to mining); ore counts as mining only after dressing/washing/
                 separating/extracting/obtaining/reducing or in 'ore of'; 'gas' moved from chemicals to fuel and
                 lighting. Precision is re-measured on a fresh sample drawn with another seed (R2b), not on R2.
  r5 2026-11-07  (site 1.0.3, after publication) from the disagreements in R2b (r4: 145/212) and two misclassifications
                 found in independent verification (no. 5999 chimneys for houses -> metals through the grantee's name
                 'Seth Smith'; no. 2999 pipes for conveying water under ground -> other):
                 - entries from 1700 whose title is not quoted are classified on the text after the first 'for/of his|
                   their|her' (enrich_woodcroft.object_text), so the grantee's name, address and trade ('engraver',
                   'surgeon', 'chocolate maker', 'Bath') no longer decide the field;
                 - order: water raising and steam/motive power now come before mining (a pump or engine 'for mines'
                   is classified by what it is, not where it is used); 'fire engine' moved from water to steam;
                 - water adds conveying water, water pipes, cisterns and extinguishing fires;
                 - printing excludes calico/cloth printing; arms no longer match bare 'powder' or 'shell(s)'
                   ('powder sugar', 'button shells'), and read OCR 'lire-arms';
                 - corn and grain moved from food to agriculture; chocolate and cocoa added to food;
                 - locks moved from building to metals; chimneys go to building unless smoke or draught is the object
                   (then fuel and lighting); trussing beams and girders go to building, 'truss' in medicine is the noun;
                 - mills add pulverising; chemicals add 'gases' (plural), gelatine and impregnating with gas;
                   instruments add telegraphs, signals and alarms.
                 Precision is re-measured on a fresh sample (R2c: new seed, stratified by the r5 fields, entries in R2
                 and R2b excluded), not on R2b.
  r6 2026-11-13  (site 1.0.6, after publication) from the disagreements in R2c (r5: 157/212) and the three error types
                 named on the method page in 1.0.4 (no. 692 woollen goods printed -> printing; no. 8664 looms worked by
                 steam -> steam; no. 1020 wire strings of a harpsichord -> metals). The rule is the coders' rule: the
                 field is the object of the invention, not its driving power, its material or the place it is used.
                 - driving means are removed before matching: 'by' followed only by power words ('worked by hand, steam,
                   water, or any other motive power', 'by steam', 'by horses') (strip_means). Only when nothing is left
                   to match is the full text matched ('an engine to be worked by the power of steam' stays steam);
                 - a few object nouns are matched before every word rule (OBJECTS): musical instruments (harpsichord,
                   pianoforte, violin, flute, guitar ...), clocks, watches, time pieces and chronometers, looms, lamps and
                   lanterns (not 'lamp black'). A material word in front of them ('wire strings of an harpsichord',
                   'glass and tin lamps') no longer decides the field;
                 - printing excludes printing, staining or embossing of woollen and worsted goods, stuffs, callimancoes,
                   muslins, chintz and handkerchiefs, up to five words after 'print' (textile finishing, not printing);
                   textiles read 'dying' (the period spelling of dyeing; the 51 occurrences in the raw text all mean dyeing);
                 - water: raising or forcing water/liquids/fluids with up to four words between, filtering water,
                   fountains; steam: locomotive engines, communicating motion/power; transport: axletrees, axles;
                   metals: hinges, chains; printing: pens; fuel and light: smoke or draught before 'chimneys' as well as
                   after;
                 - entries from 1700 whose title gives no match are classified again on the object text (from the first
                   'for/of his|their|her' to 'to hold'; enrich_woodcroft), because the title cut sometimes keeps only the
                   term clause ('for ye term of 14 years': no. 1694, cannon, was 'other').
                 R2c was used to write r6 and is not used to measure it. Precision is re-measured on a fresh sample (R2d:
                 seed 20261113, stratified by the r6 fields, entries in R2, R2b and R2c excluded).
  r7 2026-11-13  (site 1.0.7 and 1.0.8, after publication) owner decisions on the r6 boundary cases (R2d-chg regressions 2301,
                 12421, 5393, 7749, 7870, 11800; independent verification E05) and one codebook line: the object comes
                 first; the 'first field in the list' rule is used only when the object itself belongs to two fields. A
                 machine that improves the engine is steam; one for a ship, a carriage or propulsion is transport.
                 - object nouns (OBJECTS) count only as the head of the title: a noun that follows a use phrase ('for
                   ornamenting carriages ... musical instruments', 'for the purpose of', 'applicable to',
                   'such as', 'used in', 'adapted to') is ignored, unless a naming phrase ('called', 'which he
                   denominates', 'named') comes between (no. 3966 'which he denominates a musical time keeper');
                 - application clauses are removed before matching, like driving means: 'applicable to/for ...' and
                   'applied to ...' and 'may also be used ...' up to the next semicolon, and 'and (to) other (like) purposes'. Only when nothing is
                   left to match is the full text matched (strip_use);
                 - mining no longer matches 'iron mine', the period word for ironstone (no. 502, making iron from
                   'iron stone, iron mine, or iron ore', was mining);
                 - unchanged and now confirmed: 'locomotive engines' -> steam; 'propelling vessels by steam' -> transport
                   (the driving-means cut of r6).
                 The rules are word rules and do not parse the title: 'paddle wheels for steam boats' still goes to steam
                 (the word 'steam' comes before transport in the list), 'a nautical instrument for measuring the way of a
                 ship' to transport, and 'a machine for making wheels for clocks' to transport (the clock follows 'for
                 making'). These follow from the fixed order of the fields and are left for a later revision.
                 R2d and R2d-chg are not used to measure r7. Precision is re-measured on a fresh sample (R2f, seed 20261114).
                 The order rule for two object heads (1.0.8) changes no item of R2f or R2f-chg.
"""
VERSION = "r7"
OLD_SPELLINGS = [("drayn", "drain"), ("yron", "iron"), ("glasse", "glass"), ("sope", "soap"), ("salte", "salt"), ("engyn", "engin"),
                 ("myne", "mine"), ("mynes", "mines"), ("colepitt", "coal pit"), ("cole pitt", "coal pit"), ("seacole", "sea coal"),
                 ("sea cole", "sea coal"), ("cole", "coal"), ("oyle", "oil"), ("clothe", "cloth"), ("printinge", "printing"), ("ffire", "fire"),
                 ("watter", "water"), ("leade", "lead"), ("brasse", "brass"), ("silke", "silk"), ("lynnen", "linen"), ("woolle", "wool"),
                 ("shipp", "ship"), ("boate", "boat"), ("milne", "mill"), ("milles", "mills"), ("furnis", "furnace"), ("fornace", "furnace"),
                 ("coales", "coals"), ("pitt", "pit"), ("smelte", "smelt"), ("melte", "melt"), ("powlder", "powder"), ("gunne", "gun"),
                 ("ordinance", "ordnance"), ("brewe", "brew"), ("maulte", "malt"), ("malte", "malt"), ("bricke", "brick"), ("tyle", "tile"),
                 ("lether", "leather"), ("dye ", "dye "), ("dyinge", "dyeing"), ("plowe", "plough"), ("ploughe", "plough"), ("seede", "seed"),
                 ("fewell", "fuel"), ("fuell", "fuel"), ("heate", "heat"), ("lampe", "lamp"), ("candell", "candle"), ("paper", "paper"),
                 ("booke", "book"), ("printe", "print"), ("steele", "steel"), ("copperas", "copperas"), ("allom", "alum"), ("allum", "alum"),
                 ("salt peter", "saltpetre"), ("saltpeeter", "saltpetre"), ("saltpeter", "saltpetre"), ("vessell", "vessel"), ("shippes", "ships"),
                 ("carte", "cart"), ("coache", "coach"), ("waggone", "waggon"), ("pumpe", "pump"), ("draweinge", "drawing"), ("drawinge", "drawing")]
import re

FIELDS = [
    ("printing_paper", "printing, paper, books and prints", "인쇄·종이·도서",
     r"(?<!calico )(?<!cotton )(?<!linen )\bprint(?!\w*[\s,]+(?:\w+[\s,]+){0,5}(?:woven|fabrics?|cloths?|calicoe?s|cottons?|linens?|silks?|piece.goods|woolw*|worsteds?|stuffs|callimancoe?s|muslins?|chintz|handkerchiefs?))|\bpaper|\bbook|\btype\b|\btypes\b|engrav|\betch|copper.?plate|\bink\b|lithograph|stereotyp|\bcards?\b|writing|\bmaps?\b|\bpens?\b"),
    ("arms", "arms and ammunition", "무기·화약",
     r"\bguns?\b|cannon|ordnance|musket|\b[fl]ire.?arms?|pistol|gunpowder|\bpowder (?:for|of) (?:guns?|cannon|fire.?arms)|\bshot\b|bullet|bomb.?shells?|\bshells? (?:for|of) (?:guns?|cannon|mortars?|ordnance)|armou?r|weapon|instruments? of war|rifle|cartridge"),
    ("water", "water raising, drainage and hydraulics", "양수·배수·수리",
     r"rais\w* (?:\w+ ){0,4}(?:water|liquids?|fluids?)|forc\w* (?:\w+ ){0,3}(?:water|liquids?|fluids?)|water.?rais|filt\w* (?:\w+ ){0,2}water|\bfountains?\b|drain|\bpumps?\b|hydraul|draw\w* water|water.?works|dredg|scour|sluice|\bwells?\b|aqueduct|water.?closet|convey\w* (?:of )?water|conveyance of water|water.?pipes?|\bpipes? (?:\w+ ){0,4}(?:for|of) (?:the )?(?:convey\w* (?:of )?)?water|\bcisterns?|extinguish\w* (?:of )?fires?"),
    ("steam_power", "steam and motive power", "증기·동력",
     r"\bsteam|motive power|moving power|perpetual|engines? for (?:obtaining|producing|giving) (?:motion|power)|obtaining power|giving motion|fire.?engine|locomotive engines?|communicat\w* (?:motion|power)"),
    ("mining", "mining and ore", "광업",
     r"(?<!iron )(?<!iron-)\bmines?\b|\bmining\b|colliery|coal.?pits?|calamin|lapis|\b(?:dress|wash|separat|extract|obtain|reduc)\w* (?:\w+ ){0,3}(?:from |of )?(?:the )?ores?\b|\bores? of\b"),
    ("transport", "carriages, railways, ships and navigation", "운송·선박·항해",
     r"carriage|\bwheels?\b|axle.?trees?|\baxles?\b|railway|rail.?road|\bcoach|\bwaggon|\bcart\b|\bships?\b|vessels? (?:for|to)|\bboats?\b|navigat|propel|\bsails?\b|\banchors?\b|\bhulls?\b|rigging|\bmasts?\b|\bcables?\b|saddle|harness|horse.?shoe|steer"),
    ("textiles", "textiles, dyeing and leather", "직물·염색·피혁",
     r"\bcloth|weav|\bloom|spin|\bsilk|cotton|\bwool|\bflax|\bhemp|linen|\byarn|\bdye|dyeing|\bdying\b|bleach|calico|\blace\b|knit|stocking|hosiery|\bfelt|\bhats?\b|leather|\btann|\bskins?\b|carding|fustian|velvet|ribbon|\bthread|fibrous|fabric|\bsew|\bbraid"),
    ("glass_ceramics", "glass, pottery, brick and tile", "유리·도자·벽돌",
     r"\bglass|pottery|earthen|porcelain|\bchina\b|stoneware|\bbricks?\b|\btiles?\b|\bkilns?\b|crucible"),
    ("metals", "metals and metalworking", "금속·금속가공",
     r"\biron\b|\bsteel|copper|\bbrass|\blead\b|\btin\b|\bzinc|smelt|\bmetals?\b|\bnails?\b|\bwire|forg|cast\w* (?:of )?(?:iron|metal)|plating|\bscrews?\b|\bbolts?\b|cutlery|\bknives|rolling (?:of )?metal|puddl|\bsmith|\blocks?\b|\blatch|\bhinges?\b|\bchains?\b"),
    ("chemicals", "chemicals, salt, soap, oil and dyestuffs", "화학·소금·비누·기름",
     r"\bsalt\b|saltpetre|nitre|\bsoap|\balum|copperas|sulphur|brimstone|\bacid|alkali|\bsoda\b|\bpotash|\boils?\b|varnish|\bpaint|\bcolou?rs?\b|starch|\bglue|\bresin|\btar\b|turpentine|chemical|bleaching powder|ammonia|\bgases\b|gelatine|impregnat\w* (?:\w+ ){0,3}with (?:\w+ )?gas"),
    ("mills", "mills and grinding", "방아·제분",
     r"\bmills?\b|grind|grinding|\bquerns?\b|pulveri[sz]"),
    ("food_drink", "food, brewing and distilling", "식품·양조·증류",
     r"\bbrew|\bbeer|\bale\b|\bmalt|distil|spirit|\bwine|vinegar|\bsugar|\bbread|\bbak(?:e|ing)|\bflour|\bmeal\b|preserv\w* (?:meat|food|provision|animal|vegetable)|tobacco|\bcoffee|\btea\b|\bfish|chocolate|\bcocoa"),
    ("fuel_light", "fuel, heating and lighting", "연료·난방·조명",
     r"\bgas\b|\bfuel|\bfire\b|\bfires\b|furnace|\bstoves?\b|\bgrates?\b|smok\w* chimneys?|(?:smok|draught|draft)\w* (?:\w+ ){0,5}chimneys?|chimneys? (?:\w+ ){0,3}(?:smok|draught|draft)|\bheat|\bcoal\b|\bcoke\b|\bpeat|\bturf\b|\blamps?\b|\bcandle|\blight|illuminat|\bwick"),
    ("instruments", "clocks, instruments and music", "시계·기기·악기",
     r"\bclock|\bwatch|chronometer|(?:mathematical|musical|optical|surgical|nautical|philosophical|astronomical|drawing|surveying) instrument|telescope|spectacle|\blens|compass|quadrant|barometer|thermometer|\bscales?\b|weighing|measur|\bpiano|\borgan\b|\bharp|violin|trumpet|sackbut|telegraph|\bsignals?\b|\balarms?\b"),
    ("agriculture", "agriculture", "농업",
     r"\bplough|\bplow|agricultur|husbandry|\bsow|\bseeds?\b|\bmanure|threshing|thrash|\breap|harrow|\bfarm|tillage|\bland\b|\bsoil|\bhay\b|\bstraw|\bcorn\b|\bgrains?\b|winnow"),
    ("building", "building and construction", "건축·건설",
     r"\bbuild|\broofs?\b|cement|mortar|\bstucco|plaster|\bslate|\bfloor|\bbridges?\b|\bdocks?\b|\bpaving|\broads?\b|\bwindows?\b|\bdoors?\b|\bstairs|\bchimneys?\b|\bgirders?\b|truss\w* (?:\w+ )?(?:beams?|girders?|roofs?)"),
    ("medicine", "medicine and the body", "의약·신체",
     r"medicin|\bcure|\bpills?\b|\bsurg|\btruss(?:es)?\b|\bbath|\bhealth|disease|\bteeth|\bdental|artificial (?:legs?|limbs?)|\bremedy|\bdrugs?\b|\bspectacles"),
]
# r6: object nouns matched before every word rule. Each names the thing invented; material, power or use words beside
# them ('wire strings of an harpsichord', 'glass and tin lamps', 'looms ... worked by steam') must not decide the field.
OBJECTS = [
    ("instruments", r"harpsichord|piano.?forte|\bpianos?\b|\bviolins?\b|violoncello|\bflutes?\b|\bguitars?\b|musical instruments?"
                    r"|\bclocks?\b|\bwatches\b|time.?pieces?|time.?keepers?|chronometers?"),
    ("textiles", r"\blooms?\b"),
    ("fuel_light", r"\blamps?\b(?!.?black)|\blanterns?\b"),
]
# r6: driving means. 'by' followed only by these words is removed before matching ('to be worked by hand, steam, water,
# or any other motive power'): the power that drives a machine is not its field.
POWER_WORDS = {"hand", "hands", "manual", "labour", "labor", "horse", "horses", "animal", "animals", "cattle", "men", "water", "wind",
               "steam", "air", "atmospheric", "gas", "electricity", "magnetism", "galvanism", "motive", "mechanical", "power", "powers",
               "force", "means", "agency", "action", "of", "the", "any", "other", "or", "and", "either", "both", "similar", "suitable"}
POWER_CORE = {"hand", "hands", "manual", "horse", "horses", "animal", "animals", "cattle", "water", "wind", "steam", "air", "gas",
              "electricity", "magnetism", "galvanism", "motive", "mechanical", "power"}
_BY = re.compile(r"\bby\b")
_TOK = re.compile(r"[\s,;]*([a-z-]+)")


def strip_means(t: str) -> str:
    """Remove 'by <power words>' (r6). t is already lower case (normalise)."""
    out, i = [], 0
    for m in _BY.finditer(t):
        if m.start() < i:
            continue
        j, words, last = m.end(), [], m.end()
        while True:
            k = _TOK.match(t, j)
            if not k or k.group(1) not in POWER_WORDS:
                break
            words.append(k.group(1))
            j = k.end()
            if k.group(1) in POWER_CORE:
                last = j
        if any(w in POWER_CORE for w in words):
            out.append(t[i:m.start()])
            i = last
    out.append(t[i:])
    return " ".join(out)


FIELD_ORDER = [f[0] for f in FIELDS] + ["other"]
LABEL = {f[0]: {"en": f[1], "ko": f[2]} for f in FIELDS}
LABEL["other"] = {"en": "other / no match", "ko": "기타·미분류"}
_COMPILED = [(f[0], re.compile(f[3], re.I)) for f in FIELDS]
_OBJECTS = [(k, re.compile(rx, re.I)) for k, rx in OBJECTS]


def normalise(t: str) -> str:
    t = " " + (t or "").lower() + " "
    for a, b in OLD_SPELLINGS:
        t = t.replace(a, b)
    return t


# r7: a use phrase before an object noun means the noun is where the invention is used, not what it is.
# 'for' counts only before a gerund or 'the purpose/use' ('for ornamenting ...'); 'dials for clocks' keeps the clock.
USE_BEFORE = re.compile(r"\bfor (?:the )?(?:purposes?|use)\b|\bfor \w+ing\b"
                        r"|\bapplicable\b|\bapplied to\b|\bsuch as\b|\bused (?:in|for|by)\b|\badapted (?:to|for)\b|\bsuitable (?:to|for)\b")
NAMING = re.compile(r"\bcalled\b|denominat|\bnamed\b|\btermed\b|\bknown (?:as|by)\b")
# r7: application clauses removed before matching (the field is the object, not where it can also be applied).
USE_CLAUSE = re.compile(r"\b(?:applicable (?:to|for)|(?:which (?:may|are|is|can) be )?applied to)\b[^;]*"
                        r"|\b(?:may|can) (?:also )?be used\b[^;]*"
                        r"|\band (?:also )?(?:to )?(?:other|similar) (?:like |similar )?purposes\b")


def strip_use(t: str) -> str:
    return USE_CLAUSE.sub(" ", t)


def _object_head(t: str):
    """The first field in OBJECTS that has an object noun standing as the head of the text (r7), or None.
    When two object nouns of different fields are both heads, the order of OBJECTS decides, not their position in
    the text (1.0.8; the unpublished build of 1.0.7 took the earlier position, which moved one grant, no. 1287)."""
    for key, rx in _OBJECTS:
        for m in rx.finditer(t):
            before = t[: m.start()]
            u = [x.end() for x in USE_BEFORE.finditer(before)]
            if u and not NAMING.search(before, u[-1]):
                continue
            return key
    return None


def _match(t: str) -> str:
    k = _object_head(t)
    if k:
        return k
    for key, rx in _COMPILED:
        if rx.search(t):
            return key
    return "other"


def classify(title: str) -> str:
    t = normalise(title)
    f = _match(strip_use(strip_means(t)))
    # r6/r7: the driving power or an application clause decides only when nothing else names the object
    # ('an engine to be worked by the power of steam')
    return f if f != "other" else _match(t)
