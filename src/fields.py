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
"""
VERSION = "r5"
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
     r"(?<!calico )(?<!cotton )(?<!linen )\bprint(?!\w*[\s,]+(?:\w+[\s,]+){0,3}(?:woven|fabrics?|cloths?|calicoe?s|cottons?|linens?|silks?|piece.goods))|\bpaper|\bbook|\btype\b|\btypes\b|engrav|\betch|copper.?plate|\bink\b|lithograph|stereotyp|\bcards?\b|writing|\bmaps?\b"),
    ("arms", "arms and ammunition", "무기·화약",
     r"\bguns?\b|cannon|ordnance|musket|\b[fl]ire.?arms?|pistol|gunpowder|\bpowder (?:for|of) (?:guns?|cannon|fire.?arms)|\bshot\b|bullet|bomb.?shells?|\bshells? (?:for|of) (?:guns?|cannon|mortars?|ordnance)|armou?r|weapon|instruments? of war|rifle|cartridge"),
    ("water", "water raising, drainage and hydraulics", "양수·배수·수리",
     r"rais\w* water|water.?rais|drain|\bpumps?\b|hydraul|draw\w* water|water.?works|dredg|scour|sluice|\bwells?\b|aqueduct|water.?closet|convey\w* (?:of )?water|conveyance of water|water.?pipes?|\bpipes? (?:\w+ ){0,4}(?:for|of) (?:the )?(?:convey\w* (?:of )?)?water|\bcisterns?|extinguish\w* (?:of )?fires?"),
    ("steam_power", "steam and motive power", "증기·동력",
     r"\bsteam|motive power|moving power|perpetual|engines? for (?:obtaining|producing|giving) (?:motion|power)|obtaining power|giving motion|fire.?engine"),
    ("mining", "mining and ore", "광업",
     r"\bmines?\b|\bmining\b|colliery|coal.?pits?|calamin|lapis|\b(?:dress|wash|separat|extract|obtain|reduc)\w* (?:\w+ ){0,3}(?:from |of )?(?:the )?ores?\b|\bores? of\b"),
    ("transport", "carriages, railways, ships and navigation", "운송·선박·항해",
     r"carriage|\bwheels?\b|railway|rail.?road|\bcoach|\bwaggon|\bcart\b|\bships?\b|vessels? (?:for|to)|\bboats?\b|navigat|propel|\bsails?\b|\banchors?\b|\bhulls?\b|rigging|\bmasts?\b|\bcables?\b|saddle|harness|horse.?shoe|steer"),
    ("textiles", "textiles, dyeing and leather", "직물·염색·피혁",
     r"\bcloth|weav|\bloom|spin|\bsilk|cotton|\bwool|\bflax|\bhemp|linen|\byarn|\bdye|dyeing|bleach|calico|\blace\b|knit|stocking|hosiery|\bfelt|\bhats?\b|leather|\btann|\bskins?\b|carding|fustian|velvet|ribbon|\bthread|fibrous|fabric|\bsew|\bbraid"),
    ("glass_ceramics", "glass, pottery, brick and tile", "유리·도자·벽돌",
     r"\bglass|pottery|earthen|porcelain|\bchina\b|stoneware|\bbricks?\b|\btiles?\b|\bkilns?\b|crucible"),
    ("metals", "metals and metalworking", "금속·금속가공",
     r"\biron\b|\bsteel|copper|\bbrass|\blead\b|\btin\b|\bzinc|smelt|\bmetals?\b|\bnails?\b|\bwire|forg|cast\w* (?:of )?(?:iron|metal)|plating|\bscrews?\b|\bbolts?\b|cutlery|\bknives|rolling (?:of )?metal|puddl|\bsmith|\blocks?\b|\blatch"),
    ("chemicals", "chemicals, salt, soap, oil and dyestuffs", "화학·소금·비누·기름",
     r"\bsalt\b|saltpetre|nitre|\bsoap|\balum|copperas|sulphur|brimstone|\bacid|alkali|\bsoda\b|\bpotash|\boils?\b|varnish|\bpaint|\bcolou?rs?\b|starch|\bglue|\bresin|\btar\b|turpentine|chemical|bleaching powder|ammonia|\bgases\b|gelatine|impregnat\w* (?:\w+ ){0,3}with (?:\w+ )?gas"),
    ("mills", "mills and grinding", "방아·제분",
     r"\bmills?\b|grind|grinding|\bquerns?\b|pulveri[sz]"),
    ("food_drink", "food, brewing and distilling", "식품·양조·증류",
     r"\bbrew|\bbeer|\bale\b|\bmalt|distil|spirit|\bwine|vinegar|\bsugar|\bbread|\bbak(?:e|ing)|\bflour|\bmeal\b|preserv\w* (?:meat|food|provision|animal|vegetable)|tobacco|\bcoffee|\btea\b|\bfish|chocolate|\bcocoa"),
    ("fuel_light", "fuel, heating and lighting", "연료·난방·조명",
     r"\bgas\b|\bfuel|\bfire\b|\bfires\b|furnace|\bstoves?\b|\bgrates?\b|smok\w* chimneys?|chimneys? (?:\w+ ){0,3}(?:smok|draught|draft)|\bheat|\bcoal\b|\bcoke\b|\bpeat|\bturf\b|\blamps?\b|\bcandle|\blight|illuminat|\bwick"),
    ("instruments", "clocks, instruments and music", "시계·기기·악기",
     r"\bclock|\bwatch|chronometer|(?:mathematical|musical|optical|surgical|nautical|philosophical|astronomical|drawing|surveying) instrument|telescope|spectacle|\blens|compass|quadrant|barometer|thermometer|\bscales?\b|weighing|measur|\bpiano|\borgan\b|\bharp|violin|trumpet|sackbut|telegraph|\bsignals?\b|\balarms?\b"),
    ("agriculture", "agriculture", "농업",
     r"\bplough|\bplow|agricultur|husbandry|\bsow|\bseeds?\b|\bmanure|threshing|thrash|\breap|harrow|\bfarm|tillage|\bland\b|\bsoil|\bhay\b|\bstraw|\bcorn\b|\bgrains?\b|winnow"),
    ("building", "building and construction", "건축·건설",
     r"\bbuild|\broofs?\b|cement|mortar|\bstucco|plaster|\bslate|\bfloor|\bbridges?\b|\bdocks?\b|\bpaving|\broads?\b|\bwindows?\b|\bdoors?\b|\bstairs|\bchimneys?\b|\bgirders?\b|truss\w* (?:\w+ )?(?:beams?|girders?|roofs?)"),
    ("medicine", "medicine and the body", "의약·신체",
     r"medicin|\bcure|\bpills?\b|\bsurg|\btruss(?:es)?\b|\bbath|\bhealth|disease|\bteeth|\bdental|artificial (?:legs?|limbs?)|\bremedy|\bdrugs?\b|\bspectacles"),
]
FIELD_ORDER = [f[0] for f in FIELDS] + ["other"]
LABEL = {f[0]: {"en": f[1], "ko": f[2]} for f in FIELDS}
LABEL["other"] = {"en": "other / no match", "ko": "기타·미분류"}
_COMPILED = [(f[0], re.compile(f[3], re.I)) for f in FIELDS]


def normalise(t: str) -> str:
    t = " " + (t or "").lower() + " "
    for a, b in OLD_SPELLINGS:
        t = t.replace(a, b)
    return t


def classify(title: str) -> str:
    t = normalise(title)
    for key, rx in _COMPILED:
        if rx.search(t):
            return key
    return "other"
