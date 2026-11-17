# Gedeelde kerntekst, zodat deze niet onafhankelijk herhaald wordt in
# ontology/registry.py (CLASS_NOTES/PROPERTY_NOTES) en hieronder in de
# "monument_aard"-topicguidance -- één bron voor dit terugkerende feit.
MONUMENT_AARD_WARNING = (
    "ceo:heeftMonumentAard heeft PRECIES twee waarden (archeologisch / "
    "onroerend gebouwd) en is GEEN fijnmazige type- of categorieclassificatie, "
    "ook al lijkt 'aard' semantisch op 'soort'."
)

# Classes waarvoor ceo:formeelStandpunt GEEN betekenis heeft (bevestigd door
# RCE, 2026-11-17): de boolean staat er in de data wel op (vrijwel altijd
# false), maar zegt bij archeologie niets. Kennis op deze classes wordt dus
# gewoon getoond, zonder filter en zonder "geen formeel standpunt"-vermelding.
# Eén bron: ook gebruikt door validator.py om de formeel-standpuntwaarschuwing
# bij archeologiequery's te onderdrukken.
FORMEEL_STANDPUNT_EXEMPT_CLASSES = (
    "ArcheologischOnderzoeksgebied",
    "Vondstlocatie",
    "Vondsten",
    "Grondsporen",
    "ArcheologischTerrein",
    "ArcheologischComplex",
)

FUNCTION_PATH_NOTE = (
    "Gebruik voor type-/categorievragen (vliegveld, fort, begraafplaats, "
    "landgoed, fabriek, industrieterrein, ...) in plaats daarvan "
    "ceo:heeftOorspronkelijkeFunctie / ceo:heeftHuidigeFunctie (of ceo:heeftType). "
    "Zie semantics_describe_topic('functions')."
)


SEMANTIC_TOPICS = {
    "functions": {
        "title": "Functies",
        "description": (
            "Gebruik functiepaden wanneer een vraag gaat over wat een monument is "
            "of oorspronkelijk was, inclusief fijnmazige type-categorisering zoals "
            "vliegveld, fort, begraafplaats, landgoed, fabriek of industrieterrein. "
            "Filter niet op naam of omschrijving. Gebruik hiervoor NIET "
            "ceo:heeftMonumentAard -- dat kent slechts twee waarden (archeologisch / "
            "onroerend gebouwd), zie semantics_describe_topic('monument_aard').\n"
            "BELANGRIJK, LET OP bij combinatie met legal_status/monument_aard: het "
            "object-naar-functie-/type-object-pad zelf (ceo:heeftOorspronkelijkeFunctie, "
            "ceo:heeftHuidigeFunctie, ceo:heeftType) leeft, net als "
            "heeftJuridischeStatus/heeftMonumentAard, uitsluitend in GRAPH "
            "'instanties-rce'. Maar het skos:prefLabel van de functie-/type-NAAM "
            "erachter (via ceo:heeftFunctieNaam/ceo:heeftTypeNaam) leeft NERGENS in "
            "instanties-rce -- live geverifieerd (2026-11-06): die labels staan "
            "uitsluitend in de aparte thesaurusgraphs "
            "'https://data.cultureelerfgoed.nl/term/id/rn/2/thesaurus' en "
            "'https://linkeddata.cultureelerfgoed.nl/graph/bebouwdeomgeving'. Wrap de "
            "skos:prefLabel-regel van een functie-/typenaam dus NOOIT mee in dezelfde "
            "GRAPH <instanties-rce>-restrictie die legal_status/monument_aard "
            "voorschrijven voor ceo:heeftJuridischeStatus/ceo:heeftMonumentAard -- dat "
            "geeft stil 0 resultaten op het functiedeel, zonder foutmelding. Laat de "
            "skos:prefLabel-regel buiten die GRAPH-restrictie staan (zoals in alle "
            "voorbeelden hieronder), ook wanneer dezelfde query verderop wel "
            "GRAPH <instanties-rce> gebruikt voor heeftJuridischeStatus of "
            "heeftMonumentAard."
        ),
        "patterns": [
            {
                "name": "Oorspronkelijke functie",
                "path": [
                    "ceo:heeftOorspronkelijkeFunctie",
                    "ceo:heeftFunctieNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "Gebruik dit pad vaak als eerste bij vragen als boerderijen, "
                    "kerken, begraafplaatsen, kerkhoven, molens, scholen of fabrieken. "
                    "Gebruik hiervoor niet OWMS. Functies lopen via functiepaden naar "
                    "ceo:heeftFunctieNaam en daarna skos:prefLabel."
                ),
            },
            {
                "name": "Huidige functie",
                "path": [
                    "ceo:heeftHuidigeFunctie",
                    "ceo:heeftFunctieNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "Gebruik dit pad wanneer de vraag expliciet gaat over huidig "
                    "gebruik of actuele functie. Gebruik hiervoor niet OWMS; OWMS is "
                    "voor overheidstermen zoals gemeenten en provincies."
                ),
            },
            {
                "name": "Type (via heeftType)",
                "path": [
                    "ceo:heeftType",
                    "ceo:heeftTypeNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "ceo:heeftType wijst direct van het cultuurhistorisch object naar "
                    "een ceo:Type-node; die node heeft ceo:heeftTypeNaam -> "
                    "skos:prefLabel (FILTER(lang(...)=\"nl\")). Empirisch een van de "
                    "best gevulde paden in de dataset (ceo:heeftTypeNaam: 907.767 "
                    "triples, breed over veel classes, niet alleen Rijksmonument) -- "
                    "gebruik dit als derde kandidaat naast oorspronkelijke en huidige "
                    "functie, bijvoorbeeld bij bouwtype of objecttype dat niet via "
                    "functiepaden te vinden is. Verwar dit niet met "
                    "ceo:heeftKennisregistratie (rdfs:range ceo:Kennisregistratie, "
                    "GEEN ceo:Type): dat leidt naar een heel ander, breder "
                    "verzamelnode-type met meerdere instanties per Rijksmonument "
                    "(live geverifieerd: 2-5+ per monument in een steekproef), die zelf "
                    "weer functienaam, omschrijving, stijlEnCultuurNaam, "
                    "gebeurtenisNaam, bouwkundigeStaat en datering bundelt -- niet "
                    "hetzelfde als, en niet hetzelfde aantal triples als, de "
                    "ceo:Type-node van heeftType. heeftType is en blijft het directe, "
                    "kortere pad specifiek voor type-/objectsoortvragen. LET OP "
                    "formeel standpunt: van de 907.615 ceo:Type-nodes hebben er "
                    "slechts 29.569 ceo:formeelStandpunt true (geverifieerd "
                    "2026-11-17); de rest (878.046, vrijwel alles buiten "
                    "Rijksmonument) is false. Voeg bij rijksmonumenten, "
                    "complexen en gezichten standaard ?typeObj "
                    "ceo:formeelStandpunt true toe; bij de archeologische classes "
                    "heeft de boolean geen betekenis en filter je er NIET op -- "
                    "zie semantics_describe_topic('formeel_standpunt')."
                ),
            },
            {
                "name": "Combinatiezoekpad met betrouwbaarheidsmarkering (UNION)",
                "path": [
                    "ceo:heeftOorspronkelijkeFunctie",
                    "ceo:heeftHuidigeFunctie",
                    "ceo:heeftType",
                    "ceo:heeftOmschrijving",
                ],
                "guidance": (
                    "Voor vrije zoektermen als 'kerk', 'molen', 'kasteel' -- waarbij "
                    "onduidelijk is via welk pad de term voorkomt -- combineer "
                    "oorspronkelijke functie, huidige functie en type in een UNION, "
                    "met omschrijving als laatste vangnet, en label elke tak met een "
                    "?bron-kolom zodat de betrouwbaarheid zichtbaar blijft:\n"
                    "{ ?rm ceo:heeftOorspronkelijkeFunctie ?fObj . "
                    "?fObj ceo:heeftFunctieNaam ?fC . "
                    "?fC skos:prefLabel ?fNaam . FILTER(lang(?fNaam)=\"nl\") "
                    "FILTER(CONTAINS(LCASE(?fNaam), \"kerk\")) "
                    "BIND(\"oorspronkelijke functie\" AS ?bron) } "
                    "UNION { ?rm ceo:heeftHuidigeFunctie ?fObj . ?fObj ceo:heeftFunctieNaam ?fC . "
                    "?fC skos:prefLabel ?fNaam . FILTER(lang(?fNaam)=\"nl\") "
                    "FILTER(CONTAINS(LCASE(?fNaam), \"kerk\")) "
                    "BIND(\"huidige functie\" AS ?bron) } "
                    "UNION { ?rm ceo:heeftType ?typeObj . ?typeObj ceo:formeelStandpunt true ; "
                    "ceo:heeftTypeNaam ?typeC . "
                    "?typeC skos:prefLabel ?fNaam . FILTER(lang(?fNaam)=\"nl\") "
                    "FILTER(CONTAINS(LCASE(?fNaam), \"kerk\")) BIND(\"type\" AS ?bron) } "
                    "UNION { ?rm ceo:heeftOmschrijving ?oObj . ?oObj ceo:formeelStandpunt true ; "
                    "ceo:omschrijving ?fNaam . "
                    "FILTER(REGEX(LCASE(?fNaam), \"(^|\\\\W)kerk(\\\\W|$)\")) "
                    "BIND(\"omschrijving (onzeker)\" AS ?bron) }.\n"
                    "Selecteer ?bron altijd mee in SELECT DISTINCT. Rijen met "
                    "?bron = 'omschrijving (onzeker)' zijn minder betrouwbaar omdat "
                    "ze op vrije tekst berusten -- toon of behandel ze apart. Zoek "
                    "nooit los in ceo:omschrijving zonder deze markering."
                ),
            },
            {
                "name": "Geverifieerd voorbeeld: type-categorisering (fort)",
                "path": [
                    "ceo:heeftOorspronkelijkeFunctie",
                    "ceo:heeftFunctieNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "Live tegen het endpoint bevestigd (2026-09-03): SELECT DISTINCT "
                    "?rm ?naam WHERE { ?rm ceo:heeftOorspronkelijkeFunctie ?fObj . "
                    "?fObj ceo:heeftFunctieNaam ?fC . ?fC skos:prefLabel ?fNaam . "
                    "FILTER(lang(?fNaam)=\"nl\") FILTER(CONTAINS(LCASE(?fNaam), "
                    "\"fort\")) OPTIONAL { ?rm ceo:heeftNaam ?nObj . ?nObj ceo:naam "
                    "?naam . } } LIMIT 10 -- levert echte functienamen op zoals "
                    "'Fort', 'Kustfort', 'Torenfort' en 'Fort, vesting en "
                    "-onderdelen', gekoppeld aan bestaande rijksmonument-URI's "
                    "(o.a. met naam 'Gentse Poort'). Gebruik dit patroon als "
                    "sjabloon voor elke functiecategorie-vraag."
                ),
            },
            {
                "name": "Synoniem-valkuil: het letterlijke zoekwoord is niet de thesaurusterm",
                "path": [
                    "ceo:heeftOorspronkelijkeFunctie",
                    "ceo:heeftFunctieNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "CONTAINS(LCASE(?fNaam), ...) matcht alleen de exacte "
                    "thesaurusterm, geen synoniemen. Live geverifieerd: CONTAINS "
                    "op 'vliegveld' levert 0 resultaten op in ceo:heeftFunctieNaam "
                    "-- niet omdat er geen vliegvelden in de dataset staan, maar "
                    "omdat de functienaam-thesaurus andere termen gebruikt: "
                    "'Luchthavencomplex' en 'Vliegtuighangar' (CONTAINS op "
                    "'luchthaven' levert wel treffers op, o.a. 'Burgerluchthaven "
                    "Welschap' en 'Loods Fliegerhorst'). Concludeer dus nooit uit "
                    "0 resultaten op het letterlijke woord uit de vraag dat een "
                    "categorie niet voorkomt. Gebruik eerst "
                    "zoek_concept_termennetwerk(term) (doorzoekt de CHT/ABR-"
                    "thesauri waaruit deze functienaam-concepten ook daadwerkelijk "
                    "afkomstig zijn, bv. https://data.cultureelerfgoed.nl/term/id/"
                    "cht/... voor 'fort') om broader/narrower-synoniemen te vinden "
                    "-- bv. 'vliegveld' geeft via narrower 'luchthavens' -- en "
                    "filter daarna in de SPARQL-query op die gevonden term(en)."
                ),
            },
        ],
    },
    "legal_status": {
        "title": "Juridische status",
        "description": (
            "Gebruik juridische status om te bepalen of een object rijksmonument, "
            "voorbeschermd of geen rijksmonument is."
        ),
        "patterns": [
            {
                "name": "Juridische status",
                "path": [
                    "ceo:heeftJuridischeStatus",
                    "skos:prefLabel",
                ],
                "known_values": [
                    "rijksmonument",
                    "voorbeschermd",
                    "geen rijksmonument",
                ],
                "known_values_betekenis": {
                    "rijksmonument": "actief, nu beschermd",
                    "voorbeschermd": (
                        "tijdelijke bescherming, nog geen definitief besluit, "
                        "dus nog geen rijksmonument"
                    ),
                    "geen rijksmonument": (
                        "afgevoerd. Ooit rijksmonument (of in behandeling) "
                        "geweest, nu zonder status"
                    ),
                },
                "known_value_uris": {
                    "rijksmonument": "https://data.cultureelerfgoed.nl/term/id/rn/2/b2d9a59a-fe1e-4552-9a05-3c2acddff864",
                    "voorbeschermd": "https://data.cultureelerfgoed.nl/term/id/rn/2/2e93edd1-098f-4f31-ae7e-72cb77f4d2ca",
                    "geen rijksmonument": "https://data.cultureelerfgoed.nl/term/id/rn/2/3e79bb7c-b459-4998-a9ed-78d91d069227",
                },
                "graph": "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
                "guidance": (
                    "Gebruik dit pad voor vragen over actieve rijksmonumenten of "
                    "juridische status. 'Rijksmonument' is hier een juridische "
                    "statuswaarde, geen OWMS-concept. Gebruik dus niet "
                    "resolve_concept_label('rijksmonument', graph_name='owms'). "
                    "Gebruik hiervoor ook niet ceo:registergegeven. Gebruik de "
                    "graph 'instanties-rce' "
                    "(https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce) "
                    "voor rijksmonument-vragen -- dit is de graph met de actuele, "
                    "levende instantiedata. Query's zonder expliciete "
                    "GRAPH-restrictie op deze graph riskeren dubbeltellingen "
                    "(meerdere identieke triples per object). Filter bij voorkeur "
                    "direct op de concept-URI (ceo:heeftJuridischeStatus "
                    "<.../rn/2/b2d9a59a-fe1e-4552-9a05-3c2acddff864> voor "
                    "'rijksmonument', zie known_value_uris voor alle drie) in "
                    "plaats van op skos:prefLabel-tekst -- dat is sneller en "
                    "vermijdt taalstring-issues. LET OP: het padsegment '/2/' "
                    "tussen 'rn/' en de UUID is onderdeel van de URI -- een "
                    "zelf gereconstrueerde URI zonder dat segment matcht niets en "
                    "geeft stil 0 resultaten, zonder foutmelding. Gebruik altijd "
                    "de volledige URI uit known_value_uris, kort hem niet zelf af. "
                    "Deze drie "
                    "concept-URI's zijn geverifieerd tegen de live dataset (bron: "
                    "RCE-query 'Tellen van Verschillende Instanties in de Graph'). "
                    "LET OP bij combinatie met een functie-/typenaamfilter (zie "
                    "semantics_describe_topic('functions')): die GRAPH "
                    "<instanties-rce>-restrictie geldt alleen voor "
                    "ceo:heeftJuridischeStatus zelf, niet voor een skos:prefLabel-"
                    "lookup op een functie-/type-naam elders in dezelfde query -- die "
                    "labels leven in aparte thesaurusgraphs, niet in instanties-rce."
                ),
            },
        ],
    },
    "monument_aard": {
        "title": "Monumentaard",
        "description": (
            "Gebruik monumentaard om onderscheid te maken tussen archeologische "
            "en gebouwde monumenten."
        ),
        "patterns": [
            {
                "name": "Monumentaard",
                "path": [
                    "ceo:heeftMonumentAard",
                    "skos:prefLabel",
                ],
                "known_values": [
                    "archeologisch",
                    "onroerend gebouwd",
                ],
                "known_value_uris": {
                    "archeologisch": "https://data.cultureelerfgoed.nl/term/id/rn/2/b673c8c1-5d93-496d-8f9e-89133d579d77",
                    "onroerend gebouwd": "https://data.cultureelerfgoed.nl/term/id/rn/2/fc966a68-8863-4970-a83e-110f96006c21",
                },
                "graph": "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
                "guidance": (
                    "Gebruik dit pad bij vragen over gebouwde of archeologische "
                    "rijksmonumenten. 'Archeologisch' is monumentaard, geen functie "
                    "en geen OWMS-concept. Gebruik de graph 'instanties-rce' "
                    "(https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce): "
                    "alle heeftMonumentAard-triples leven in deze ene graph. Val "
                    "op: een query zonder GRAPH-restrictie én zonder "
                    "COUNT(DISTINCT ?cho) telt objecten dubbel, omdat elk object "
                    "meerdere identieke rdf:type/kenmerk-triples heeft. Reken "
                    "bijvoorbeeld op 1499 archeologische rijksmonumenten, niet op "
                    "de 2963 die een naieve COUNT(?cho) oplevert. Van die 1499 "
                    "hebben er 1472 POLYGON/MULTIPOLYGON-geometrie en slechts 27 "
                    "POINT (geverifieerd 2026-11-06, zelfde heeftGeometrie/asWKT-pad "
                    "als area.py/grootste_monumenten_oppervlakte() -- dus bij de "
                    "overgrote meerderheid IS automatisch een oppervlakte te "
                    "berekenen met geof:area(), zie semantics_describe_topic('geometry')). "
                    "Filter bij voorkeur direct op de concept-URI "
                    "(ceo:heeftMonumentAard <.../rn/2/b673c8c1-5d93-496d-8f9e-89133d579d77> "
                    "voor 'archeologisch', <.../rn/2/fc966a68-8863-4970-a83e-110f96006c21> "
                    "voor 'onroerend gebouwd' -- zie known_value_uris voor de volledige "
                    "URI's) in plaats van op skos:prefLabel-tekst -- geverifieerd tegen "
                    "de live dataset, geen taalstring nodig (dit concept heeft geen "
                    "lang-tag op zijn prefLabel). LET OP: het padsegment '/2/' tussen "
                    "'rn/' en de UUID is onderdeel van de URI -- zonder dat segment "
                    "matcht de query stil niets, zonder foutmelding.\n"
                    f"BELANGRIJK, veelgemaakte fout: {MONUMENT_AARD_WARNING} "
                    f"{FUNCTION_PATH_NOTE}"
                ),
            },
        ],
    },
    "names": {
        "title": "Namen",
        "description": (
            "Gebruik namen voor presentatie. Gebruik namen meestal niet als eerste "
            "selectiecriterium."
        ),
        "patterns": [
            {
                "name": "Naam",
                "path": [
                    "ceo:heeftNaam",
                    "ceo:naam",
                ],
                "guidance": (
                    "Gebruik dit pad om een naam te tonen nadat objecten zijn "
                    "geselecteerd via type, functie, locatie of status."
                ),
            },
        ],
    },
    "descriptions": {
        "title": "Omschrijvingen",
        "description": (
            "Gebruik omschrijvingen om uit te leggen waarom of hoe een object "
            "in het register beschreven staat."
        ),
        "patterns": [
            {
                "name": "Omschrijving",
                "path": [
                    "ceo:heeftOmschrijving",
                    "ceo:omschrijving",
                ],
                "guidance": (
                    "Gebruik dit pad voor beschrijvende tekst. Filter hier alleen "
                    "op als er geen beter conceptueel pad bestaat. Een "
                    "ceo:Omschrijving is een kennisregistratie met "
                    "ceo:formeelStandpunt true of false (87.061 true, 464.541 "
                    "false, geverifieerd 2026-11-17). Toon bij rijksmonumenten, "
                    "complexen en gezichten standaard alleen het formele "
                    "standpunt (bij de archeologische classes heeft de boolean "
                    "geen betekenis: daar niet filteren): "
                    "?cho ceo:heeftOmschrijving ?oObj . ?oObj "
                    "ceo:formeelStandpunt true ; ceo:omschrijving ?tekst . Bij "
                    "Rijksmonument is dat de officiele registeromschrijving "
                    "(67.415 true naast 4.859 false). Zie "
                    "semantics_describe_topic('formeel_standpunt')."
                ),
            },
        ],
    },
    "identifiers": {
        "title": "Identificerende nummers (registernummers, huisnummer, perceelnummer)",
        "description": (
            "Gebruik dit topic voordat je filtert op een registernummer, huisnummer "
            "of perceelnummer: deze velden zijn stuk voor stuk xsd:string, geen "
            "xsd:integer, ook wanneer de waarde er als getal uitziet. Gebruik "
            "ceo:cultuurhistorischObjectnummer (CHOI) als je tussen domeinspecifieke "
            "nummers (rijksmonumentnummer, complexnummer, werelderfgoednummer, "
            "archis2-nummers) heen en weer wilt vertalen."
        ),
        "patterns": [
            {
                "name": "CHOI (Cultuurhistorisch Object Identificatienummer)",
                "path": ["ceo:cultuurhistorischObjectnummer"],
                "guidance": (
                    "ceo:cultuurhistorischObjectnummer is het CHOI-nummer: RCE's "
                    "domeinonafhankelijke centrale index over alle erfgoeddomeinen "
                    "heen (gebouwd erfgoed, archeologie, landschap, roerend erfgoed). "
                    "Elk CHO heeft precies één CHOI, naast zijn eventuele "
                    "domeinspecifieke nummer (rijksmonumentnummer, complexnummer, "
                    "werelderfgoednummer, archis2*-nummers) op dezelfde node. Gebruik "
                    "dit pad om tussen die domeinspecifieke nummers te vertalen -- bv. "
                    "'welk rijksmonumentnummer hoort bij CHO-nummer X' -- door beide "
                    "properties op hetzelfde subject op te halen: ?cho a ceo:Rijksmonument ; "
                    "ceo:cultuurhistorischObjectnummer ?choi ; ceo:rijksmonumentnummer "
                    "?rmnr . Empirisch veruit de breedst gevulde identifier in de "
                    "dataset (1.210.776 triples tegenover 67.496 voor "
                    "rijksmonumentnummer, dus ruim 17x zo veel -- geverifieerd "
                    "2026-11-06) omdat hij op vrijwel elk CHO-type voorkomt, "
                    "niet alleen op ceo:Rijksmonument. Bron: RCE-story "
                    "'CHO en CHOI als ruggengraat' en de bijbehorende query "
                    "'Het rijksmonumentnummer van een CHO uuid'. xsd:string, altijd "
                    "gequote filteren, net als de andere nummers in dit topic."
                ),
            },
            {
                "name": "Rijksmonumentnummer",
                "path": ["ceo:rijksmonumentnummer"],
                "guidance": (
                    "ceo:rijksmonumentnummer (rdfs:domain ceo:Rijksmonument) is het "
                    "unieke nummer waaronder een rijksmonument bekend staat in het "
                    "monumentenregister (skos:example \"2\"). Het is xsd:string: filter "
                    "altijd met aanhalingstekens (ceo:rijksmonumentnummer \"2\"), nooit "
                    "met een kaal getal. Dit is de meest directe sleutel om een specifiek "
                    "rijksmonument op te zoeken -- gebruik dit pad voor 'zoek monument "
                    "nummer X' in plaats van te filteren op naam of omschrijving. Voor een "
                    "klikbare link naar het officiele register: BIND(URI(CONCAT("
                    "\"https://monumentenregister.cultureelerfgoed.nl/monumenten/\", "
                    "?rijksmonumentnummer)) AS ?link) -- patroon uit RCE's eigen "
                    "voorbeeldquery's, handig bij presentatie van resultaten."
                ),
            },
            {
                "name": "Complexnummer",
                "path": ["ceo:complexnummer"],
                "guidance": (
                    "ceo:complexnummer identificeert het complex waaronder een groep "
                    "rijksmonumenten in het monumentenregister bekend staat. Ook hier: "
                    "xsd:string, altijd gequote filteren."
                ),
            },
            {
                "name": "Gezichtsnummer",
                "path": ["ceo:gezichtsnummer"],
                "guidance": (
                    "ceo:gezichtsnummer identificeert een beschermd stads- of "
                    "dorpsgezicht (ceo:Gezicht). xsd:string, altijd gequote filteren."
                ),
            },
            {
                "name": "Werelderfgoednummer",
                "path": ["ceo:werelderfgoednummer"],
                "guidance": (
                    "ceo:werelderfgoednummer (rdfs:domain ceo:Werelderfgoed) identificeert "
                    "een werelderfgoed (skos:example \"759\"). xsd:string, altijd gequote "
                    "filteren."
                ),
            },
            {
                "name": "Huisnummer",
                "path": ["ceo:huisnummer"],
                "guidance": (
                    "ceo:huisnummer is een ongetypeerd string-literal (bv. \"19\"), "
                    "geen xsd:integer. Filter of match altijd met aanhalingstekens: "
                    "ceo:huisnummer \"19\". Een kaal getal (ceo:huisnummer 19) matcht "
                    "de RDF-term niet en geeft stil 0 resultaten, zonder foutmelding -- "
                    "ook als het monument gegarandeerd bestaat. validate_query_structured() "
                    "waarschuwt hiervoor."
                ),
            },
            {
                "name": "Perceelnummer",
                "path": ["ceo:heeftKadastraleAanduiding", "ceo:perceelnummer"],
                "guidance": (
                    "ceo:perceelnummer is, net als huisnummer, een ongetypeerd "
                    "string-literal. Vergelijk altijd met een gequote waarde "
                    "(ceo:perceelnummer \"123\"), nooit met een kaal getal."
                ),
            },
        ],
    },
    "addresses": {
        "title": "Adressen (BAG)",
        "description": (
            "Gebruik dit topic voor vragen over het adres van een cultuurhistorisch "
            "object (straat, huisnummer, postcode). Adresgegevens staan niet direct "
            "op het object, maar op de gekoppelde BAG-relatie."
        ),
        "patterns": [
            {
                "name": "Volledig adres via BAG",
                "path": [
                    "ceo:heeftBasisregistratieRelatie",
                    "ceo:heeftBAGRelatie",
                    "ceo:volledigAdres",
                ],
                "guidance": (
                    "Kernpatroon: CultuurhistorischObject "
                    "-> ceo:heeftBasisregistratieRelatie -> ceo:BasisregistratieRelatie "
                    "-> ceo:heeftBAGRelatie -> ceo:BAGRelatie -> ceo:volledigAdres "
                    "(skos:example \"Eerste Bloemdwarsstraat 10\"). Postcode "
                    "(ceo:postcode, bv. \"1012BS\") en huisnummer (ceo:huisnummer) staan "
                    "op dezelfde ceo:BAGRelatie-node. Een object kan meerdere "
                    "BAGRelaties hebben (bv. een boerderijcomplex met meerdere "
                    "verblijfsobjecten); gebruik COUNT(DISTINCT ...) en DISTINCT in "
                    "SELECT-resultaten om dubbeltellingen te voorkomen. Combineer deze "
                    "OPTIONAL-tak niet in dezelfde query met een andere multi-valued "
                    "OPTIONAL-tak zoals BRK-percelen (ceo:heeftBRKRelatie) -- dat geeft "
                    "een cartesisch product. Haal BAG- en BRK-gegevens in aparte "
                    "queries op en combineer ze in code."
                ),
            },
            {
                "name": "Meerdere volledigAdres-waarden per verblijfsobject",
                "path": [
                    "ceo:heeftBasisregistratieRelatie",
                    "ceo:heeftBAGRelatie",
                    "ceo:volledigAdres",
                ],
                "guidance": (
                    "ceo:volledigAdres kan meerdere, verschillende waarden hebben "
                    "voor exact hetzelfde ceo:heeftVerblijfsobject (bijvoorbeeld "
                    "ligplaatsen en standplaatsen met meerdere nummeringsvarianten "
                    "op één object, zoals \"Bogaardenstraat 1 M 09\" en "
                    "\"Bogaardenstraat 1 M 08\" voor dezelfde verblijfsobject-URI). "
                    "DISTINCT op de BAGRelatie-node alleen is dus niet voldoende om "
                    "dubbeltellingen te voorkomen. Dedupliceer op "
                    "ceo:heeftVerblijfsobject (de URI, of het laatste padsegment als "
                    "ID), niet op ceo:volledigAdres of op de BAGRelatie-node. "
                    "Bevestigd: rijksmonumentnummer 26722 (CHO 10001) leverde 11 "
                    "verschillende volledigAdres-waarden op voor precies 1 unieke "
                    "heeftVerblijfsobject-URI."
                ),
            },
        ],
    },
    "rest_api_wrappers": {
        "title": "Vaste REST-queries versus zelf geschreven SPARQL",
        "description": (
            "Naast het rechtstreeks bevragen van het SPARQL-endpoint (via "
            "query_sparql) bestaan er ook vaste, opgeslagen queries die als "
            "REST-eindpunt worden aangeboden, bijvoorbeeld "
            "https://api.linkeddata.cultureelerfgoed.nl/queries/rce/"
            "rest-api-rijksmonumenten/run. Deze zijn handig voor snelle lookups "
            "maar hebben een vaste queryvorm die niet met validate_query() te "
            "controleren is, omdat de gebruiker de SPARQL zelf niet ziet of "
            "aanpast."
        ),
        "patterns": [
            {
                "name": "Eén-op-veel wordt onterecht één-op-één",
                "path": [
                    "n.v.t. (vaste REST-query, geen zelf geschreven SPARQL-pad)",
                ],
                "guidance": (
                    "De 'rest-api-rijksmonumenten'-REST-query retourneert altijd "
                    "maximaal 1 BAGRelatie per rijksmonument, ook wanneer een "
                    "monument er meerdere heeft (bijvoorbeeld een pand met meerdere "
                    "huisnummers, zoals rijksmonumentnummer 99 met 5 adressen: "
                    "Oudezijds Achterburgwal 82A t/m E in Amsterdam). Dit wordt niet "
                    "als fout gemeld; de aanroeper krijgt gewoon 1 resultaat en kan "
                    "onterecht aannemen dat dat het enige adres is. Gebruik voor "
                    "volledigheid altijd query_sparql() met een expliciete "
                    "DISTINCT-aanpak (zie semantics_describe_topic('addresses')) in "
                    "plaats van deze REST-wrapper, tenzij zekerheid over "
                    "volledigheid niet relevant is voor de vraag."
                ),
            },
        ],
    },
    "geometry": {
        "title": "Geometrie",
        "description": (
            "Gebruik geometrie om locaties van monumenten op te halen als "
            "coördinaten of WKT-geometrieën. Geometrieën zijn direct bruikbaar "
            "voor kaartvisualisatie; geen coördinaatconversie nodig."
        ),
        "patterns": [
            {
                "name": "Puntgeometrie (WKT)",
                "path": [
                    "ceo:heeftGeometrie",
                    "geo:asWKT",
                ],
                "guidance": (
                    "Gebruik dit pad om de locatie van een monument als WKT op te halen. "
                    "Het resultaat is een POINT-waarde in WGS84 (lon lat), bijvoorbeeld "
                    "POINT(4.9041 52.3676). Geen conversie nodig voor Leaflet of GeoJSON. "
                    "Let op: gebruik ceo:heeftGeometrie, niet geo:hasGeometry -- dat laatste "
                    "is wel de rdfs:subPropertyOf in de ontologie, maar komt in de live data "
                    "0 keer voor en geeft dus stil 0 resultaten zonder foutmelding. "
                    "ceo:heeftGeometrie heeft 241.605 triples. "
                    "Geometrieën staan in de graph 'punten' of 'instanties-rce'. "
                    "Voeg PREFIX geo: <http://www.opengis.net/ont/geosparql#> toe aan de query. "
                    "Gebruik geen geof:sfWithin of andere GeoSPARQL-relaties voor ruimtelijke "
                    "joins — deze veroorzaken structurele timeouts op het Virtuoso-endpoint. "
                    "Haal in plaats daarvan de WKT-geometrieën op via query_sparql() en voer "
                    "de ruimtelijke join daarna lokaal uit met Shapely in Python. "
                    "Let op: de graph 'linies' gebruikt ceo:asWKT-RD met Rijksdriehoekscoordinaten "
                    "(EPSG:28992), niet WGS84. query_sparql_geojson() slaat die rijen automatisch "
                    "over (zichtbaar als '_skipped' in het resultaat). Gebruik voor linies een "
                    "aparte conversie van RD naar WGS84 vóór visualisatie."
                ),
            },
            {
                "name": "Polygoongeometrie (beschermd stadsgezicht)",
                "path": [
                    "ceo:heeftGeometrie",
                    "geo:asWKT",
                ],
                "guidance": (
                    "Polygonen van beschermde stads- en dorpsgezichten (ceo:Gezicht) "
                    "staan in de graph 'instanties-rce' via ceo:heeftGeometrie -> "
                    "geo:asWKT (WGS84; live geverifieerd 2026-11-17: 472 gezichten "
                    "met geo:asWKT, allemaal in instanties-rce). CORRECTIE op een "
                    "eerdere versie van deze tekst: de graph 'gezicht-hvdl' "
                    "(https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl) bevat "
                    "GEEN geo:asWKT -- een GRAPH-restrictie daarop geeft voor de "
                    "polygoon stil 0 resultaten. Die graph bevat wel aanvullende "
                    "gegevens per gezicht (482 stuks): op het Gezicht zelf "
                    "ceo:inProceduredatumGezicht, ceo:intrekkingsdatumGezicht (9x, "
                    "ingetrokken gezichten) en ceo:wordtGetoondOp; op de Geometrie-"
                    "node ceo:oppervlakteInHectare, ceo:oppervlakteInVierkanteKilometers, "
                    "ceo:begrenzingsdatumGezicht, ceo:heeftOndergrondGezicht en een "
                    "ceo:asWKT-RD-PUNT in Rijksdriehoekscoordinaten. Hetzelfde geldt "
                    "voor 'werelderfgoed-hvdl' (18 werelderfgoederen: "
                    "ceo:jaarVanInschrijving, ceo:heeftWerelderfgoedType, "
                    "ceo:wordtGetoondOp naar whc.unesco.org, en oppervlakte op de "
                    "Geometrie-node). Combineer beide dus zo: polygoon uit "
                    "instanties-rce, oppervlakte/datums uit de hvdl-graph, gejoined op "
                    "de gezicht-/werelderfgoed-URI. "
                    "Ruimtelijke joins (welke monumenten liggen binnen een stadsgezicht-polygoon) "
                    "moeten lokaal worden uitgevoerd met Shapely; gebruik geof:sfWithin niet."
                ),
            },
            {
                "name": (
                    "Oppervlakte berekenen (geof:area) -- gebruik liever "
                    "grootste_monumenten_oppervlakte()"
                ),
                "path": [
                    "ceo:heeftGeometrie",
                    "geo:asWKT",
                ],
                "guidance": (
                    "Voor 'grootste monument qua oppervlakte'-vragen: gebruik de "
                    "tool grootste_monumenten_oppervlakte() -- die bevat dit hele "
                    "patroon al, inclusief de 504-workaround. Gebruik dit pad zelf "
                    "alleen als je iets net anders nodig hebt dan die tool biedt "
                    "(bv. een oppervlaktedrempel filteren). "
                    "ceo:oppervlakteInVierkanteMeters bestaat alleen op de ~1.400 "
                    "Geometrie-objecten van historische buitenplaatsen/tuinen "
                    "(via ceo:heeftAanlegGeometrie) -- voor alle andere "
                    "rijksmonumenten bestaat geen gematerialiseerd oppervlakteveld. "
                    "Bereken de oppervlakte in plaats daarvan on-the-fly met de "
                    "GeoSPARQL-functie geof:area(?wkt, uom:metre) op ceo:heeftGeometrie "
                    "-> geo:asWKT (PREFIX geof: <http://www.opengis.net/def/function/"
                    "geosparql/>, PREFIX uom: <http://www.opengis.net/def/uom/OGC/1.0/>). "
                    "Geverifieerd tegen dit endpoint: geof:area verwacht PRECIES twee "
                    "argumenten (wkt-literal + eenheid-URI) -- met één argument geeft "
                    "het endpoint HTTP 400. Met uom:metre levert het een geodetische "
                    "oppervlakte in m2 direct uit WGS84-coordinaten, geen conversie nodig. "
                    "Werkt alleen op POLYGON/MULTIPOLYGON, niet op POINT: van de "
                    "65.786 ceo:heeftGeometrie/geo:asWKT-waarden op Rijksmonument in "
                    "GRAPH instanties-rce (geverifieerd 2026-11-06 -- tel NOOIT de "
                    "losse graph 'punten' hierbovenop op: zoals de eerdere "
                    "\"Puntgeometrie\"-guidance in dit topic al zegt, staat geometrie "
                    "in 'punten' OF instanties-rce, dus als alternatieven, niet als "
                    "optelbare totalen; een "
                    "eerdere versie van dit cijfer deed dat wel en kwam zo op het "
                    "bijna 2x te hoge ~128.896/104.236) is de meerderheid (40.873) "
                    "een POINT zonder oppervlakte, maar 14.284 POLYGON en 10.629 "
                    "MULTIPOLYGON -- samen ~38% van het totaal, dus bij ruim een "
                    "derde van de Rijksmonumenten met geometrie IS een oppervlakte "
                    "te berekenen. Val op: de WKT-literals in "
                    "deze dataset gebruiken gemengde hoofdletters MET spatie voor het "
                    "type-keyword (bv. 'Polygon (...)', 'Point (...)'), niet de striktere "
                    "vorm 'POLYGON(...)' -- FILTER(STRSTARTS(STR(?wkt), \"POLYGON\")) "
                    "geeft hierdoor stil 0 resultaten. Gebruik altijd "
                    "FILTER(REGEX(STR(?wkt), \"^\\\\s*(multi)?polygon\", \"i\")). Combineer "
                    "geof:area()-sortering nooit direct met OPTIONAL-joins (naam, "
                    "rijksmonumentnummer) in dezelfde queryschaal -- dat triggert de "
                    "bekende ORDER BY + OPTIONAL 504. Gebruik de tweetraps-subquery: "
                    "SELECT DISTINCT ?rm (geof:area(?wkt, uom:metre) AS ?opp) sorteren en "
                    "LIMIT-en in een binnenste query zonder OPTIONAL, en pas in de "
                    "buitenste query OPTIONAL-joins toevoegen op de al-beperkte set. "
                    "Live geverifieerd voorbeeld (2026-09-03): het grootste rijksmonument "
                    "qua oppervlakte is 'Deelen/Vliegveld' (rijksmonumentnummer 529782), "
                    "circa 8,67 km2 -- zie grootste_monumenten_oppervlakte() voor de "
                    "kant-en-klare implementatie."
                ),
            },
            {
                "name": "Fallback bij onvolledige adresgegevens: koppelen via PDOK Locatieserver",
                "path": [
                    "ceo:heeftBasisregistratieRelatie",
                    "ceo:heeftBAGRelatie",
                    "ceo:heeftVerblijfsobject",
                ],
                "guidance": (
                    "Adresvelden op een ceo:BAGRelatie zijn niet altijd compleet: "
                    "soms ontbreken ceo:openbareRuimte en/of ceo:postcode, en bevat "
                    "ceo:huisnummer een niet-standaard notatie (bijvoorbeeld "
                    "\"82 C\" of \"1 M 09\"). Zelf een adresstring samenstellen uit "
                    "de losse velden en die vervolgens laten geocoderen is "
                    "onbetrouwbaar. Betrouwbaarder alternatief: gebruik het laatste "
                    "padsegment van ceo:heeftVerblijfsobject (de numerieke "
                    "BAG-verblijfsobject-ID) rechtstreeks bij PDOK Locatieserver via "
                    "een fq-filter op het veld adresseerbaarobject_id (bijv. "
                    "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free?q=*&"
                    "fq=adresseerbaarobject_id:{id}). Dat geeft een exacte match "
                    "met coördinaten (centroide_rd/centroide_ll) en een correct "
                    "opgemaakt weergavenaam-adres, ongeacht hoe onvolledig de "
                    "RCE-zijde is. Dit is een externe bron (PDOK), niet het RCE "
                    "CHO-endpoint zelf, dus vereist een aparte HTTP-aanroep na de "
                    "SPARQL-query."
                ),
            },
        ],
    },
    "kadaster": {
        "title": "Kadastrale percelen (BRK-relatie) -- niet gegarandeerd compleet",
        "description": (
            "Gebruik dit topic bij vragen over welke kadastrale percelen bij "
            "een rijksmonument horen, of over de totale kadastrale oppervlakte "
            "van een monument. BELANGRIJKSTE punt: RCE's eigen BRK-koppeling "
            "is NIET gegarandeerd een volledige perceellijst -- ga daar niet "
            "zonder controle van uit."
        ),
        "patterns": [
            {
                "name": "RCE's eigen BRK-relatie (tekstueel, mogelijk onvolledig)",
                "path": [
                    "ceo:heeftBasisregistratieRelatie",
                    "ceo:heeftBRKRelatie",
                ],
                "guidance": (
                    "Kernpatroon: CultuurhistorischObject -> "
                    "ceo:heeftBasisregistratieRelatie -> ceo:BasisregistratieRelatie "
                    "-> ceo:heeftBRKRelatie -> ceo:BRKRelatie (gemeentenaam/sectie/"
                    "perceelnummer). BELANGRIJKE VALKUIL: het aantal ceo:BRKRelatie-"
                    "triples per rijksmonument varieert enorm en zonder duidelijk "
                    "patroon -- geverifieerd 2026-11-06 over alle rijksmonumenten met "
                    "minstens 1 BRKRelatie: minimum 1, maximum 760, gemiddeld ~2,2. "
                    "Een monument met qua omvang/type een meervoudig-perceel-karakter "
                    "(buitenplaats, landgoed, vliegveld, fort, complex) kan dus zowel "
                    "een lange, kennelijk uitputtende lijst hebben (bv. "
                    "'Circumvallatielinie', rijksmonumentnummer 532275: 751 "
                    "BRKRelatie-triples) als een opvallend korte (bv. Vliegveld Deelen, "
                    "rijksmonumentnummer 529782: 28 BRKRelatie-triples, tegenover 33 "
                    "percelen die een echte spatial join vindt, zie hieronder -- dus "
                    "zelfs een niet-triviaal aantal kan nog altijd onvolledig zijn). "
                    "Je kunt dit vooraf niet aan de query zien: elk monument heeft "
                    "gewoon een of meer ceo:BRKRelatie-triples, zonder markering of "
                    "dat de volledige lijst is of niet. Neem dus NOOIT aan dat het "
                    "gevonden aantal de volledige lijst is. Controleer expliciet of "
                    "het aantal gevonden percelen aannemelijk is voor de omvang van "
                    "het monument (vergelijk desnoods met "
                    "grootste_monumenten_oppervlakte() of geof:area(), zie "
                    "semantics_describe_topic('geometry')) voordat je een "
                    "BRK-uitkomst als compleet presenteert."
                ),
            },
            {
                "name": "Betrouwbaar alternatief: spatial join met Kadaster KKG",
                "path": [
                    "ceo:heeftGeometrie",
                    "geo:asWKT",
                ],
                "guidance": (
                    "Gebruik de tool percelen_via_spatial_join(rijksmonument, limit) "
                    "voor een geometrisch geverifieerd antwoord, onafhankelijk van wat "
                    "RCE's eigen (mogelijk onvolledige) BRK-relatie zegt: deze tool "
                    "haalt RCE's monumentgeometrie op en berekent zelf, via een echte "
                    "spatial join tegen Kadaster's KKG-endpoint (geof:sfIntersects "
                    "tussen ceo:heeftGeometrie/geo:asWKT en imxgeo:Perceel -> "
                    "geosparql:hasGeometry/asWKT), welke percelen het monument "
                    "daadwerkelijk overlapt, met hun totale oppervlakte "
                    "(geosparql:hasMetricArea, al gematerialiseerd in de KKG -- geen "
                    "berekening nodig aan die kant). Geverifieerd live (2026-09-03): "
                    "Vliegveld Deelen (rijksmonumentnummer 529782) -> 33 overlappende "
                    "percelen, 6.801.806 m2 totaal, tegenover 8.674.092 m2 "
                    "monumentoppervlakte (78% -- plausibel: niet elk perceel binnen de "
                    "monumentgrens heeft per se hasGeometry/hasMetricArea in de KKG, en "
                    "een monument kan net over een gemeentegrens heenlopen die RCE's "
                    "eigen heeftGemeente-link niet toont). RCE (WGS84 wktLiteral) en "
                    "KKG (WGS84, maar het Virtuoso-eigen datatype virtrdf:Geometry) "
                    "staan op TWEE APARTE endpoints; een SERVICE-federated query in "
                    "EEN keer bleek in test niet betrouwbaar (een buiten de SERVICE "
                    "gebonden variabele in een geof:sfIntersects-FILTER leverde 0 "
                    "resultaten op), dus doet deze tool de join met twee losse "
                    "HTTP-calls. Virtuoso's eigen bif:st_intersects/bif:st_area op het "
                    "KKG-endpoint gaf consistent HTTP 500 (niet bruikbaar via dit "
                    "gehoste endpoint) -- gebruik geof:sfIntersects (standaard "
                    "GeoSPARQL), en beperk de kandidatenset eerst niet-ruimtelijk tot "
                    "een specifieke imxgeo:Gemeentegebied (via "
                    "imxgeo:ligtInRegistratieveRuimte), anders time-out een scan over "
                    "de ~8,4 miljoen imxgeo:Perceel-instanties net als de bekende "
                    "geof:sfWithin-timeout op het RCE-endpoint zelf."
                ),
            },
        ],
    },
    "maritime": {
        "title": "Maritiem erfgoed (MASS-dataset, los endpoint)",
        "description": (
            "Gebruik dit topic voor vragen over scheepswrakken, maritiem "
            "erfgoed, VOC-schepen of andere historische vaartuigen. Dit zijn "
            "GEEN CEO-objecten -- de data staat in een apart dataset/endpoint "
            "(RCE MASS), met een eigen schema.org-achtige vocabulaire "
            "(sdo:Vehicle/Place/GeoCoordinates), niet in ceo:Rijksmonument of "
            "een andere CEO-class. Gebruik hiervoor query_sparql_mass(), niet "
            "query_sparql() -- die laatste bevraagt het CHO-endpoint, waar "
            "deze data niet in staat."
        ),
        "patterns": [
            {
                "name": "Scheepsrecord (naam, type, omschrijving)",
                "path": [
                    "a sdo:Vehicle",
                    "sdo:name",
                    "schema:additionalType",
                    "sdo:description",
                ],
                "guidance": (
                    "Kernpatroon: ?vehicle a <https://sdo.org/Vehicle> ; "
                    "<https://sdo.org/name> ?naam . Elk vaartuig heeft meestal "
                    "TWEE sdo:name-waarden: een met een jaartal-suffix (bv. "
                    "\"Hendrika (+1850)\", het zinkjaar) en een zonder (\"Hendrika\") "
                    "-- dedupliceer of kies bewust één variant, anders toont een "
                    "lijst elk schip dubbel. Het scheepstype (bv. \"Fregat\", "
                    "\"Vrachtschip\", \"Jacht\") staat niet op sdo: maar op "
                    "<https://schema.org/additionalType> (een ander, "
                    "ongeprefixt namespace dan de rest van deze dataset -- "
                    "let op het verschil tussen sdo.org en schema.org). "
                    "sdo:description is lange HTML-tekst (vergelijkbaar met "
                    "ceo:omschrijving op het CHO-endpoint qua grootte); gebruik "
                    "dit niet als selectiecriterium zonder LIMIT. Anders dan "
                    "skos:prefLabel op het CHO-endpoint zijn deze literals NIET "
                    "taalgetagd -- een kale FILTER(?naam = \"Hendrika\") of "
                    "CONTAINS(LCASE(?naam), ...) werkt hier gewoon, zonder "
                    "STR()-wrap of resolve_concept_label()."
                ),
            },
            {
                "name": "Locatie en coordinaten",
                "path": [
                    "sdo:location",
                    "sdo:geo",
                    "sdo:latitude",
                    "sdo:longitude",
                ],
                "guidance": (
                    "Vervolgpad vanaf het vaartuig: ?vehicle sdo:location ?plaats . "
                    "?plaats sdo:geo ?geo . ?geo sdo:latitude ?lat ; sdo:longitude ?lon . "
                    "Beide zijn xsd:double in decimale graden, WGS84 -- GEEN WKT "
                    "zoals geo:asWKT op het CHO-endpoint, dus niet door "
                    "query_sparql_geojson() (die verwacht een enkele WKT-variabele) "
                    "of wkt_to_geometry() te halen; bouw zelf een "
                    "{\"type\": \"Point\", \"coordinates\": [lon, lat]} als GeoJSON "
                    "nodig is. ?plaats heeft ook sdo:containedInPlace (landnaam als "
                    "platte string, bv. \"Nederland\", \"Verenigd Koninkrijk\" -- "
                    "geen OWMS-concept-URI, dus resolve_concept_label() of "
                    "resolve_gemeente() zijn hier niet van toepassing) en "
                    "sem:hasBeginTimeStamp/sem:hasEndTimeStamp (een jaartal-bereik "
                    "voor de periode van het wrak/object op die locatie, bv. 1800-1850)."
                ),
            },
            {
                "name": "Ontdekkingsjaar",
                "path": ["schema:discovered"],
                "guidance": (
                    "<https://schema.org/discovered> (let op: schema.org-namespace, "
                    "niet sdo.org) geeft het jaar waarin het wrak ontdekt is, als "
                    "kaal geheel getal-literal (bv. 2004). Niet op elk vaartuig "
                    "aanwezig (580 van de 2587 in een steekproef) -- gebruik "
                    "OPTIONAL."
                ),
            },
        ],
    },
    "archaeology": {
        "title": "Archeologische objecten",
        "description": (
            "Gebruik dit topic voor vragen over archeologische terreinen, "
            "onderzoeksgebieden, complexen, vondstlocaties, grondsporen en "
            "vondsten. Dit zijn aparte classes naast ceo:Rijksmonument, "
            "onderling verbonden via ceo:bevatObject / ceo:ligtInObject.\n"
            "LET OP 1 (formeel standpunt): voor ArcheologischOnderzoeksgebied, "
            "Vondstlocatie, Vondsten, Grondsporen, ArcheologischTerrein en "
            "ArcheologischComplex heeft ceo:formeelStandpunt GEEN betekenis "
            "(bevestigd door RCE, 2026-11-17). De boolean staat in de data "
            "vrijwel altijd op false, maar zegt hier niets: filter er NIET op "
            "en toon omschrijving, type, datering, cultuur en materiaal gewoon, "
            "zonder vermelding. De regel 'alleen formeel standpunt' geldt wel "
            "voor rijksmonumenten, ook archeologische; zie "
            "semantics_describe_topic('formeel_standpunt').\n"
            "LET OP 2 (Archis2): Archis2-nummers worden al jaren niet meer "
            "uitgegeven en dekken alleen de periode tot de conversie -- zie het "
            "patroon 'Archis2-identificatienummers' hieronder."
        ),
        "patterns": [
            {
                "name": "Containment-netwerk (bevatObject / ligtInObject)",
                "path": ["ceo:bevatObject"],
                "guidance": (
                    "ceo:bevatObject en zijn inverse ceo:ligtInObject (samen 943.139 "
                    "triples, exact gelijk aantal in beide richtingen, geverifieerd "
                    "2026-11-06) verbinden archeologische classes in een netwerk, geen "
                    "strikte boom -- dezelfde class kan via meerdere bovenliggende "
                    "classes gevuld worden. Empirisch voorkomende combinaties (aantal "
                    "triples, geverifieerd 2026-11-06 -- dit zijn live tellingen die "
                    "met de tijd licht kunnen verschuiven, behandel ze als indicatie "
                    "van orde van grootte, niet als exacte huidige waarde): "
                    "ceo:Rijksmonument bevatObject ceo:ArcheologischTerrein (1.812); "
                    "ceo:ArcheologischTerrein bevatObject ceo:ArcheologischComplex (18.548); "
                    "ceo:ArcheologischOnderzoeksgebied bevatObject "
                    "ceo:ArcheologischComplex (9.528); "
                    "ceo:ArcheologischOnderzoeksgebied bevatObject ceo:Vondstlocatie (40.401); "
                    "ceo:Vondstlocatie bevatObject ceo:ArcheologischComplex (332.352); "
                    "ceo:Vondstlocatie bevatObject ceo:Grondsporen (93.007); "
                    "ceo:Vondstlocatie bevatObject ceo:Vondsten (447.488). "
                    "Gebruik ceo:ligtInObject om vanuit het kleinere object omhoog te "
                    "navigeren (bv. vanaf een Vondsten-object terug naar de "
                    "Vondstlocatie) -- dit is dezelfde relatie in omgekeerde richting, "
                    "geen apart pad met eigen betekenis. Ga niet uit van een vaste "
                    "diepte: een ceo:ArcheologischComplex kan direct onder een "
                    "ArcheologischTerrein, een ArcheologischOnderzoeksgebied of een "
                    "Vondstlocatie hangen, dus verken eerst welke combinatie relevant "
                    "is voordat je een vast pad aanneemt."
                ),
            },
            {
                "name": "Archis2-identificatienummers (historisch, niet meer uitgegeven)",
                "path": ["ceo:archis2Monumentnummer"],
                "guidance": (
                    "BELANGRIJK, PERIODE: Archis2-nummers (waaronder het "
                    "ceo:archis2Vondstmeldingsnummer) worden al jaren niet meer "
                    "uitgegeven (bevestigd door RCE, 2026-11-17). Ze bestaan alleen "
                    "op registraties uit het Archis2-tijdperk, dus op wat bij de "
                    "conversie naar het huidige systeem is overgezet. Live "
                    "geverifieerd (2026-11-17) via ceo:registratiedatum: 41.132 van "
                    "de 41.514 objecten met een archis2Vondstmeldingsnummer hebben "
                    "registratiedatum 2016 (de conversie), en van de ~25.000 "
                    "Vondstlocaties die sinds 2017 zijn geregistreerd hebben er "
                    "slechts 382 nog zo'n nummer (2023 en 2024: 0). "
                    "archis2Monumentnummer en archis2Complexnummer: vrijwel alles "
                    "met registratiedatum 2015 (conversie), een nagekomen partij in "
                    "2019, daarna niets meer. Gevolgen: (1) gebruik een Archis2-"
                    "nummer alleen om een BESTAAND, oud nummer op te zoeken (bv. uit "
                    "een rapport of publicatie van voor de conversie); (2) gebruik "
                    "het NOOIT om 'alle' vondstmeldingen, waarnemingen of terreinen "
                    "te tellen of te selecteren -- alles van na de conversie valt "
                    "dan stil weg; gebruik daarvoor de class (bv. ?x a "
                    "ceo:Vondstlocatie) en ceo:cultuurhistorischObjectnummer; "
                    "(3) meld bij een vraag naar een recente melding dat Archis2-"
                    "nummers daarvoor niet bestaan; (4) ceo:registratiedatum is de "
                    "datum van registratie in het huidige systeem, NIET de datum van "
                    "de oorspronkelijke melding -- voor geconverteerde records is "
                    "dat dus 2015/2016, ongeacht hoe oud de melding werkelijk is. "
                    "Uitzondering: ceo:archis2Waarnemingsnummer wordt nog wel bij "
                    "nieuw geregistreerde records ingevuld (2025: 1.319, 2026: "
                    "3.186) -- het ontbreken ervan zegt dus niets over de ouderdom.\n"
                    "Archis2-nummers zijn xsd:string -- filter altijd met "
                    "aanhalingstekens. Elk nummer hoort bij een specifieke class "
                    "(rdfs:domain): ceo:archis2Monumentnummer -> ceo:ArcheologischTerrein "
                    "(13.025 triples); ceo:archis2Complexnummer -> "
                    "ceo:ArcheologischComplex of ceo:Vondstlocatie (18.588); "
                    "ceo:archis2Vondstmeldingsnummer -> ceo:Vondstlocatie (41.514); "
                    "ceo:archis2Waarnemingsnummer -> ceo:Vondstlocatie (88.649); "
                    "ceo:archis2Vondstnummer -> ceo:Grondsporen of ceo:Vondsten "
                    "(321.634, identificeert de individuele vondst/het grondspoor, "
                    "niet de vondstlocatie). Daarnaast heeft vrijwel elke "
                    "archeologische class ook ceo:cultuurhistorischObjectnummer als "
                    "generieke identifier."
                ),
            },
            {
                "name": "Aantallen op Grondsporen en Vondsten",
                "path": ["ceo:bevatObject", "ceo:aantalVondsten"],
                "guidance": (
                    "ceo:Grondsporen heeft ceo:aantalGrondsporen, ceo:Vondsten heeft "
                    "ceo:aantalVondsten -- beide hangen via ceo:bevatObject onder een "
                    "ceo:Vondstlocatie. Voorbeeld voor 'welke vindplaats heeft de "
                    "meeste vondsten': SELECT DISTINCT ?locatie ?naam ?aantal WHERE { "
                    "?locatie a ceo:Vondstlocatie . ?locatie ceo:bevatObject ?vondstObj . "
                    "?vondstObj a ceo:Vondsten . ?vondstObj ceo:aantalVondsten ?aantal . "
                    "OPTIONAL { ?locatie ceo:heeftLocatieAanduiding ?locObj . "
                    "?locObj ceo:locatienaam ?naam . } } ORDER BY DESC(?aantal) LIMIT 20"
                ),
            },
            {
                "name": "Naam van een vondstlocatie",
                "path": ["ceo:heeftLocatieAanduiding", "ceo:locatienaam"],
                "guidance": (
                    "Vondstlocaties (en andere archeologische classes) hebben geen "
                    "ceo:heeftNaam zoals Rijksmonument, maar "
                    "ceo:heeftLocatieAanduiding -> ceo:locatienaam. Gebruik dit pad "
                    "niet voor ceo:Rijksmonument zelf."
                ),
            },
            {
                "name": "Filteren op gemeente (bv. 'archeologische onderzoeksgebieden in X')",
                "path": [
                    "ceo:heeftBasisregistratieRelatie",
                    "ceo:heeftGemeente",
                ],
                "guidance": (
                    "Dezelfde gemeentekoppeling als bij Rijksmonument: "
                    "CultuurhistorischObject -> ceo:heeftBasisregistratieRelatie -> "
                    "ceo:BasisregistratieRelatie -> ceo:heeftGemeente -> OWMS-"
                    "gemeenteconcept. RDFS-gezien is deze link niet Rijksmonument-"
                    "specifiek, maar in de PRAKTIJK is hij alleen betrouwbaar gevuld "
                    "bij ceo:ArcheologischOnderzoeksgebied (~91%, 103.929 van 113.956) "
                    "en ceo:Vondstlocatie (~91%, 102.226 van 112.009) -- geverifieerd "
                    "2026-11-06. Gebruik hiervoor resolve_gemeente() + de tool "
                    "monumenten_in_gemeente(gemeente, "
                    "class_name='ArcheologischOnderzoeksgebied', "
                    "juridische_status='alle') -- ondanks de naam werkt deze tool voor "
                    "elke class_name, niet alleen monumenten. LET OP, veelgemaakte fout: "
                    "laat juridische_status NIET op zijn standaardwaarde "
                    "('rijksmonument') staan bij een niet-Rijksmonument class_name -- "
                    "ceo:heeftJuridischeStatus (en ceo:heeftMonumentAard) bestaat in de "
                    "ontologie uitsluitend op ceo:Rijksmonument (rdfs:domain), een "
                    "ArcheologischOnderzoeksgebied heeft deze property nooit -- geef "
                    "daarom expliciet juridische_status='alle' mee (de tool geeft sinds "
                    "kort een foutmelding i.p.v. stil 0 resultaten als je dit vergeet).\n"
                    "BELANGRIJKE UITZONDERING: ceo:ArcheologischComplex, "
                    "ceo:ArcheologischTerrein, ceo:Grondsporen en ceo:Vondsten hebben "
                    "deze directe gemeentekoppeling vrijwel NOOIT (elk 1 van tienduizenden "
                    "tot honderdduizenden instanties, geverifieerd 2026-11-06) -- stel "
                    "hier geen query op met ceo:heeftGemeente direct op het object, dat "
                    "geeft stil (bijna) 0 resultaten. Betrouwbaarder alternatief voor "
                    "ArcheologischComplex (~86%), Grondsporen (~93%) en Vondsten (~93%): "
                    "navigeer één stap omhoog via ceo:ligtInObject naar de bovenliggende "
                    "ArcheologischOnderzoeksgebied/Vondstlocatie, en filter die op "
                    "gemeente. Voor ceo:ArcheologischTerrein bestaat GEEN bruikbaar "
                    "alternatief binnen deze dataset: ook via ceo:ligtInObject is maar "
                    "14% bereikbaar (de meeste terreinen hebben geen containment-parent "
                    "geregistreerd) -- overweeg een geometrische aanpak (ceo:heeftGeometrie "
                    "+ spatial join, zie semantics_describe_topic('geometry')) in plaats "
                    "van een gemeentefilter.\n"
                    "Gebruik voor gemeentefiltering NOOIT ceo:gemeentenaam (een los "
                    "tekstveld, rdfs:domain ceo:BRKRelatie, dus zelf ook alleen gevuld "
                    "via de BRK-relatie van een Rijksmonument -- bestaat niet op "
                    "archeologische classes) en navigeer niet via een BAG-woonplaatsnaam "
                    "als vervanging voor een echte gemeentegrens -- BAG-woonplaatsen en "
                    "gemeentegrenzen vallen niet 1-op-1 samen (bv. de kern Cothen ligt "
                    "BAG-woonplaats-gewijs dicht bij Bunnik maar valt gemeentelijk onder "
                    "Wijk bij Duurstede), wat tot een verkeerd (te hoog) aantal leidt."
                ),
            },
        ],
    },
    "formeel_standpunt": {
        "title": "Formeel standpunt (ceo:formeelStandpunt true/false)",
        "description": (
            "Gebruik dit topic bij ELKE vraag die kennis over een object toont "
            "of erop filtert: omschrijving, type, functie, naam, gebeurtenis "
            "(o.a. datering/bouwjaar), stijl en cultuur, materiaal of "
            "bouwkundige kwaliteit. Al deze gegevens zijn ceo:Kennisregistratie-"
            "nodes, en elke kennisregistratie draagt de boolean "
            "ceo:formeelStandpunt (xsd:boolean; rdfs:domain ceo:Kennisregistratie; "
            "live geverifieerd 2026-11-17: aanwezig op ALLE 3.307.776 "
            "kennisregistraties, 289.647 true en 3.018.129 false). true = een "
            "formeel standpunt van de RCE (bv. de officiele registeromschrijving "
            "van een rijksmonument); false = geregistreerde kennis die GEEN "
            "formeel standpunt is.\n"
            "REGEL (afspraak met RCE, 2026-11-17): toon en gebruik standaard "
            "UITSLUITEND kennis met ceo:formeelStandpunt true. Toon kennis met "
            "false alleen als de gebruiker daar uitdrukkelijk om vraagt, en "
            "vermeld er dan bij elke waarde bij dat het geen formeel standpunt "
            "is. Vermeld in je antwoord altijd dat het om het formele standpunt "
            "gaat, en zeg het eerlijk als er voor een object alleen niet-formele "
            "kennis bestaat in plaats van die stilzwijgend te tonen of te doen "
            "alsof er niets is.\n"
            "UITZONDERING ARCHEOLOGIE (bevestigd door RCE, 2026-11-17): voor de "
            "classes ceo:ArcheologischOnderzoeksgebied, ceo:Vondstlocatie, "
            "ceo:Vondsten, ceo:Grondsporen, ceo:ArcheologischTerrein en "
            "ceo:ArcheologischComplex heeft ceo:formeelStandpunt GEEN betekenis. "
            "De boolean staat er in de data wel op (vrijwel altijd false), maar "
            "zegt daar niets. Filter bij deze classes dus NIET op "
            "ceo:formeelStandpunt, toon de kennis (omschrijving, type, "
            "datering, cultuur, materiaal) gewoon, en zet er GEEN vermelding "
            "'geen formeel standpunt' bij. De regel hierboven geldt voor de "
            "overige objecten: rijksmonumenten (ook archeologische "
            "rijksmonumenten, dat zijn ceo:Rijksmonument-objecten), complexen, "
            "gezichten en werelderfgoed."
        ),
        "patterns": [
            {
                "name": "Alleen formeel standpunt (standaard)",
                "path": [
                    "ceo:heeftOmschrijving",
                    "ceo:formeelStandpunt",
                ],
                "guidance": (
                    "Zet de boolean op de kennisnode, niet op het object: "
                    "?cho ceo:heeftOmschrijving ?k . ?k ceo:formeelStandpunt true ; "
                    "ceo:omschrijving ?tekst . Schrijf de waarde als kale boolean "
                    "(true), niet als string (\"true\") -- een string matcht de "
                    "xsd:boolean niet en geeft stil 0 resultaten. Hetzelfde "
                    "patroon geldt voor ceo:heeftType, ceo:heeftGebeurtenis, "
                    "ceo:heeftStijlEnCultuur, ceo:heeftMateriaal, "
                    "ceo:heeftBouwkundigeKwaliteit, ceo:heeftOorspronkelijkeFunctie, "
                    "ceo:heeftHuidigeFunctie, ceo:heeftNaam en het overkoepelende "
                    "ceo:heeftKennisregistratie. validate_query() waarschuwt als "
                    "een query een van de gemengde paden gebruikt zonder "
                    "ceo:formeelStandpunt, behalve wanneer de query een van de "
                    "archeologische classes uit de UITZONDERING noemt."
                ),
            },
            {
                "name": "Verdeling per soort kennis (wat valt weg bij 'alleen true')",
                "path": ["ceo:formeelStandpunt"],
                "guidance": (
                    "Live geteld op 2026-11-17 in graph instanties-rce (true / "
                    "false per class van de kennisnode): ceo:Functie 75.517 / 0; "
                    "ceo:Naam 12.520 / 0; ceo:BouwkundigeKwaliteit 9.178 / 0; "
                    "ceo:StedenbouwkundigeMorfologischeAanduiding 472 / 0; "
                    "ceo:Omschrijving 87.061 / 464.541; ceo:Type 29.569 / 878.046; "
                    "ceo:Gebeurtenis 51.461 / 878.046; ceo:StijlEnCultuur 23.869 / "
                    "352.758; ceo:Materiaal 0 / 444.738. Functie en naam zijn dus "
                    "altijd formeel (het filter verandert daar niets aan). De "
                    "grote aantallen false komen vrijwel geheel van de "
                    "archeologische classes, waar de boolean geen betekenis "
                    "heeft (zie de UITZONDERING in de beschrijving van dit topic): "
                    "materiaal komt bv. alleen bij ceo:Vondsten voor en wordt daar "
                    "gewoon getoond."
                ),
            },
            {
                "name": "Verdeling per objectsoort",
                "path": ["ceo:heeftOmschrijving", "ceo:formeelStandpunt"],
                "guidance": (
                    "Live geteld op 2026-11-17, omschrijvingen per objectclass "
                    "(true / false): Rijksmonument 67.415 / 4.859; Complex 2.513 "
                    "/ 0; ArcheologischComplex 17.108 / 11.692; "
                    "ArcheologischTerrein 25 / 11.212; "
                    "ArcheologischOnderzoeksgebied 0 / 66.477; Vondstlocatie 0 / "
                    "111.988; Vondsten 0 / 216.531; Grondsporen 0 / 41.782. "
                    "De regel 'alleen true' geldt voor Rijksmonument (daar maakt "
                    "hij verschil: 4.859 niet-formele omschrijvingen) en Complex. "
                    "Op Rijksmonument zijn heeftType (10.981), heeftGebeurtenis "
                    "(32.873), heeftStijlEnCultuur (23.869) en "
                    "heeftOorspronkelijkeFunctie (69.887) allemaal true. Voor de "
                    "zes archeologische classes in dit lijstje heeft de boolean "
                    "geen betekenis: negeer hem daar volledig, ook de 17.108 "
                    "true-waarden bij ArcheologischComplex zeggen niets."
                ),
            },
            {
                "name": "Niet-formele kennis tonen (alleen op uitdrukkelijk verzoek)",
                "path": ["ceo:heeftKennisregistratie", "ceo:formeelStandpunt"],
                "guidance": (
                    "Vraagt de gebruiker er uitdrukkelijk om? Selecteer dan de "
                    "boolean mee en toon hem als kolom, in plaats van het filter "
                    "weg te laten: ?cho ceo:heeftOmschrijving ?k . ?k "
                    "ceo:formeelStandpunt ?formeel ; ceo:omschrijving ?tekst . "
                    "Zet in het antwoord bij elke rij 'formeel standpunt' of 'geen "
                    "formeel standpunt'. Laat het filter nooit ongemerkt weg."
                ),
            },
        ],
    },
    "gemeenten": {
        "title": "Gemeenten en gemeentelijke herindelingen (OWMS / TOOI)",
        "description": (
            "Gebruik dit topic bij elke vraag met een gemeentefilter. "
            "ceo:heeftGemeente (via ceo:heeftBasisregistratieRelatie) wijst "
            "ALTIJD naar een OWMS-gemeenteconcept in de graph 'owms' (live "
            "geverifieerd 2026-11-17: 402 verschillende gemeenten, allemaal "
            "http://standaarden.overheid.nl/owms/terms/...). De graph "
            "'tooi-gemeenten' wordt niet als doel van heeftGemeente gebruikt; "
            "het is een naslaggraph (gemeentecode, begin-/einddatum, "
            "wijzigingen).\n"
            "BELANGRIJKSTE VALKUIL: de gemeentekoppeling is bij herindelingen "
            "NIET volledig en niet altijd naar de juiste gemeente omgezet. 61 "
            "van de 402 gebruikte gemeenten zijn opgeheven, samen 5.091 "
            "relaties (1.065 Rijksmonument-objecten over 58 opgeheven "
            "gemeenten, 1.793 archeologische onderzoeksgebieden, 2.233 "
            "vondstlocaties). Drie situaties: (1) ACTIEVE rijksmonumenten "
            "(status 'rijksmonument') zijn overal omgezet naar de huidige "
            "gemeente, met precies een uitzondering: Voorne aan Zee (sinds "
            "2023-01-01) heeft zelf 0 objecten -- alle 448 actieve "
            "rijksmonumenten van dat grondgebied staan op voorganger "
            "Westvoorne, ook de ruim 350 met BAG-woonplaats Brielle. "
            "(2) AFGEVOERDE objecten (status 'geen rijksmonument') zijn niet "
            "omgezet: 617 stuks over 58 opgeheven gemeenten (bv. Weesp 69, "
            "Boxmeer 41, Cuijk 13). (3) ARCHEOLOGIE (onderzoeksgebieden, "
            "vondstlocaties) is niet omgezet voor de herindelingen van "
            "2021-01-01 t/m 2023-01-01. Een filter op alleen de huidige "
            "gemeente mist die objecten stil; een filter op alleen een oude "
            "gemeente geeft een restant (of 0) en zegt niets over wat er "
            "feitelijk in dat voormalige grondgebied ligt. De naam van de "
            "gekoppelde gemeente is dus GEEN betrouwbare aanwijzing voor de "
            "ligging binnen de nieuwe gemeente -- gebruik daarvoor de "
            "BAG-woonplaats (ceo:woonplaatsnaam op de BAGRelatie) of de "
            "geometrie."
        ),
        "patterns": [
            {
                "name": "Gebruik de tools: zij tellen voorgangers mee",
                "path": [
                    "ceo:heeftBasisregistratieRelatie",
                    "ceo:heeftGemeente",
                ],
                "guidance": (
                    "monumenten_in_gemeente() telt standaard "
                    "(inclusief_voorgangers=True) ook de objecten mee die nog aan "
                    "een opgeheven voorganger hangen, en toont de uitsplitsing per "
                    "gemeente. resolve_gemeente() meldt of een gemeente opgeheven "
                    "is (met einddatum en opvolger) en geeft de URI's van de "
                    "voorgangers. percelen_via_spatial_join() vertaalt een "
                    "opgeheven gemeente naar de huidige voordat het Kadaster "
                    "bevraagt (de KKG kent alleen huidige gemeenten). Vraagt de "
                    "gebruiker naar een opgeheven gemeente (bv. 'Brielle'), "
                    "vermeld dan dat die is opgegaan in de opvolger en bied aan "
                    "het huidige grondgebied op te vragen."
                ),
            },
            {
                "name": "Handgeschreven query: voorgangers meenemen via OWMS",
                "path": ["owms:predecessor", "owms:successor", "owms:endDate"],
                "guidance": (
                    "In de graph 'owms' (PREFIX owms: "
                    "<http://standaarden.overheid.nl/owms/terms/>): owms:endDate "
                    "(xsd:date, 269 gemeenten) = opgeheven; owms:successor = "
                    "opvolger(s); owms:predecessor = voorganger(s) (270 elk, "
                    "elkaars inverse); owms:startDate = ontstaan. Neem "
                    "voorgangers mee met een VALUES-lijst uit resolve_gemeente(), "
                    "of met een property path: GRAPH <.../graph/owms> { "
                    "<gemeente-URI> owms:predecessor* ?gem } gevolgd door ?obj "
                    "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente ?gem. "
                    "LET OP gesplitste gemeenten: een voorganger met MEERDERE "
                    "opvolgers (bv. Haaren, 2020-12-31 -> Boxtel, Oisterwijk, "
                    "Tilburg en Vught) is niet eenduidig toe te wijzen; "
                    "owms:predecessor* telt die objecten bij elk van de opvolgers "
                    "mee en overschat dus. De tools slaan zulke voorgangers "
                    "daarom over en melden ze apart; bepaal de juiste gemeente "
                    "dan per object via de geometrie."
                ),
            },
            {
                "name": "TOOI-graph als naslag",
                "path": ["tooi:gemeentecode", "tooi:einddatum", "tooi:owmsId"],
                "guidance": (
                    "Graph 'tooi-gemeenten' "
                    "(https://linkeddata.cultureelerfgoed.nl/rce/tooi/graph/gemeenten; "
                    "PREFIX tooi: <https://identifier.overheid.nl/tooi/def/ont/>): "
                    "605 gemeenten (bestaand en opgeheven) met tooi:gemeentecode "
                    "(CBS-code, bv. '1731'), tooi:officieleNaamExclSoort, "
                    "tooi:begindatum, tooi:einddatum (263x) en tooi:owmsId. "
                    "Herindelingen staan er als aparte nodes in (tooi:Samenvoeging "
                    "54, tooi:Uitbreiding 62, tooi:Herschikking 12) met "
                    "prov:invalidated (opgeheven gemeente), prov:generated (nieuwe "
                    "gemeente), prov:used en tooi:tijdstipWijziging. VALKUIL: "
                    "tooi:owmsId is een xsd:anyURI-LITERAL, geen IRI -- een directe "
                    "join met ceo:heeftGemeente geeft stil 0 resultaten; gebruik "
                    "FILTER(STR(?owmsId) = STR(?gem)). Actualiteit (2026-11-17): "
                    "register met zichtdatum 2026-01-29; de laatste herindeling in "
                    "zowel TOOI als OWMS is die van 2023-01-01 (Voorne aan Zee). "
                    "Latere herindelingen zijn in deze graphs niet te herkennen -- "
                    "controleer bij twijfel de actuele gemeente-indeling."
                ),
            },
        ],
    },
    "images": {
        "title": "Afbeeldingen (Beeldbank RCE, los endpoint)",
        "description": (
            "Gebruik dit topic voor vragen over foto's, bouwtekeningen, prenten "
            "en andere afbeeldingen uit de Beeldbank van de RCE. Dit is een "
            "APARTE dataset (https://linkeddata.cultureelerfgoed.nl/rce/afbeeldingen) "
            "met een eigen endpoint en schema.org-vocabulaire (PREFIX sdo: "
            "<https://schema.org/>), GEEN CEO-objecten. Gebruik "
            "query_sparql_afbeeldingen(), niet query_sparql(). De hoofddata "
            "staat in de named graph "
            "https://linkeddata.cultureelerfgoed.nl/rce/afbeeldingen/graphs/photos "
            "(565.170 sdo:Photograph, ~18,9 miljoen triples, geteld 2026-11-17); "
            "zet daar altijd een GRAPH-restrictie op en een LIMIT -- brede "
            "GROUP BY-scans over deze graph lopen in een timeout."
        ),
        "patterns": [
            {
                "name": "Foto's bij een rijksmonument",
                "path": ["sdo:about", "sdo:image", "sdo:contentUrl"],
                "guidance": (
                    "Een foto verwijst via sdo:about naar de rijksmonument-URI van "
                    "het CHO-endpoint (bv. https://linkeddata.cultureelerfgoed.nl/"
                    "cho-kennis/id/rijksmonument/41069; 329.420 van zulke "
                    "koppelingen). LET OP: het getal in die URI is het "
                    "cultuurhistorischObjectnummer, NIET het rijksmonumentnummer, "
                    "en de fotograph bevat zelf geen ceo:rijksmonumentnummer. "
                    "Werk daarom in twee stappen: (1) zoek met query_sparql() de "
                    "monument-URI bij een rijksmonumentnummer; (2) gebruik die URI "
                    "hier: SELECT ?foto ?titel ?datum ?url ?thumb WHERE { GRAPH "
                    "<.../rce/afbeeldingen/graphs/photos> { ?foto a sdo:Photograph ; "
                    "sdo:about <monument-URI> ; sdo:name ?titel ; sdo:image ?img . "
                    "?img sdo:contentUrl ?url ; sdo:thumbnailUrl ?thumb . OPTIONAL "
                    "{ ?foto sdo:dateCreated ?datum } } } LIMIT 50. Een "
                    "SERVICE-federatie tussen de twee endpoints is niet getest; "
                    "doe het in twee losse aanroepen."
                ),
            },
            {
                "name": "Velden van een foto",
                "path": ["sdo:name", "sdo:creator", "sdo:dateCreated", "sdo:license"],
                "guidance": (
                    "Op de sdo:Photograph: sdo:name (titel/beschrijving), "
                    "sdo:dateCreated (string, wisselende precisie: '2007-07', "
                    "'1965'), sdo:creator -> sdo:Person met sdo:name ('Achternaam, "
                    "Voornaam'), sdo:contentLocation -> sdo:Place met sdo:name (bv. "
                    "'Dorpsstraat 84, Zuid-Beijerland') en sdo:address -> "
                    "sdo:PostalAddress (sdo:streetAddress, sdo:addressLocality, "
                    "sdo:postalCode), sdo:url (detailpagina op "
                    "beeldbank.cultureelerfgoed.nl), sdo:license, sdo:isPartOf -> "
                    "sdo:Collection (bv. 'Fotocollectie', 'RCE - Gebouwd'), en "
                    "sdo:about -> sdo:DefinedTerm met sdo:name voor trefwoorden "
                    "(bv. 'Herbestemming'; 601.899 koppelingen). Het beeld zelf: "
                    "sdo:image -> sdo:ImageObject met sdo:contentUrl (volledig "
                    "formaat), sdo:thumbnailUrl (350x350) en sdo:encodingFormat. "
                    "Literals zijn niet taalgetagd: CONTAINS(LCASE(?titel), ...) "
                    "werkt zonder STR()."
                ),
            },
            {
                "name": "Identificatienummers en licentie",
                "path": ["sdo:identifier", "sdo:propertyID", "sdo:value"],
                "guidance": (
                    "Nummers zitten in sdo:identifier -> sdo:PropertyValue met "
                    "sdo:propertyID en sdo:value. Voorkomende propertyID's: "
                    "'inventarisnummer' (bv. 'OF-01381', '528.367'), "
                    "'beeldbank-uuid' en 'priref'. Filter op een nummer met: "
                    "?foto sdo:identifier ?id . ?id sdo:propertyID "
                    "\"inventarisnummer\" ; sdo:value \"528.367\" . Licenties "
                    "(sdo:license): overwegend CC BY-SA 3.0 "
                    "(http://creativecommons.org/licenses/by-sa/3.0/) en CC BY-SA "
                    "4.0 -- vermeld de licentie en de maker bij het tonen of "
                    "hergebruiken van een afbeelding."
                ),
            },
            {
                "name": "Alternatief op het CHO-endpoint: graph 'image'",
                "path": ["edm:aggregatedCHO", "ceo:rijksmonumentnummer", "edm:isShownBy"],
                "guidance": (
                    "De graph 'image' (ook op het CHO-endpoint, dus met "
                    "query_sparql()) bevat edm:ProvidedCHO-records die WEL direct "
                    "ceo:rijksmonumentnummer dragen (91.834 in de kopie op het "
                    "afbeeldingen-endpoint), plus edm:aggregatedCHO "
                    "(rijksmonument-URI), dc:title, dc:description, dc:rights, "
                    "edm:isShownBy (Wikimedia-thumbnail), edm:isShownAt en "
                    "foaf:depiction. Handig voor een snelle 'eerste foto bij "
                    "rijksmonumentnummer X' in een enkele query; voor de volledige "
                    "collectie met maker, datum en plaats gebruik je de fotograph "
                    "hierboven."
                ),
            },
        ],
    },
    "library": {
        "title": "Bibliotheek (catalogus RCE, los endpoint)",
        "description": (
            "Gebruik dit topic voor vragen over literatuur: boeken en "
            "tijdschriftartikelen uit de bibliotheekcatalogus van de RCE. Dit is "
            "een APARTE dataset (https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek) "
            "met een eigen endpoint en schema.org-vocabulaire (PREFIX sdo: "
            "<https://schema.org/>), GEEN CEO-objecten. Gebruik "
            "query_sparql_bibliotheek(), niet query_sparql(). Twee named graphs "
            "(geteld 2026-11-17): .../rce/bibliotheek/graphs/books (155.422 "
            "sdo:Book) en .../rce/bibliotheek/graphs/article (26.265 "
            "sdo:Article). Zet altijd een GRAPH-restrictie en een LIMIT; de "
            "dataset bevat daarnaast oudere graphs (.../graph/bib e.d.) met "
            "ook boeken -- zonder GRAPH-restrictie riskeer je dubbelen."
        ),
        "patterns": [
            {
                "name": "Boeken",
                "path": ["a sdo:Book", "sdo:name", "sdo:author", "sdo:datePublished"],
                "guidance": (
                    "In graph .../graphs/books: ?boek a sdo:Book ; sdo:name ?titel . "
                    "Verder: sdo:author / sdo:creator -> sdo:Person of "
                    "sdo:Organization met sdo:name ('Achternaam, Voorletters'), "
                    "sdo:datePublished (jaartal als string, bv. '1979'), "
                    "sdo:publisher -> sdo:Organization, sdo:locationCreated -> "
                    "sdo:Place, sdo:numberOfPages, sdo:size, sdo:isPartOf -> reeks "
                    "(sdo:CreativeWorkSeries), en sdo:url (detailpagina op "
                    "catalogus.cultureelerfgoed.nl -- geef die mee in het "
                    "antwoord). Identificatie via sdo:identifier -> "
                    "sdo:PropertyValue met sdo:propertyID 'priref'. Literals zijn "
                    "niet taalgetagd: FILTER(CONTAINS(LCASE(?titel), \"kasteel\")) "
                    "werkt direct."
                ),
            },
            {
                "name": "Tijdschriftartikelen",
                "path": ["a sdo:Article", "sdo:isPartOf", "sdo:pageStart"],
                "guidance": (
                    "In graph .../graphs/article: ?art a sdo:Article ; sdo:name "
                    "?titel . Verder sdo:author, sdo:datePublished, sdo:pageStart / "
                    "sdo:pageEnd, sdo:description, sdo:url. De bron loopt via een "
                    "keten van sdo:isPartOf: Article -> sdo:PublicationIssue "
                    "(sdo:issueNumber) -> sdo:PublicationVolume (sdo:volumeNumber, "
                    "sdo:datePublished) -> sdo:Periodical (sdo:name = "
                    "tijdschrifttitel; 658 tijdschriften). Voorbeeld: ?art "
                    "sdo:isPartOf/sdo:isPartOf/sdo:isPartOf ?tijdschrift . "
                    "?tijdschrift a sdo:Periodical ; sdo:name ?tsNaam ."
                ),
            },
            {
                "name": "Onderwerp: thesaurusterm, plaats of rijksmonument",
                "path": ["sdo:about", "sdo:spatialCoverage"],
                "guidance": (
                    "sdo:about heeft meerdere soorten doelen: (a) CHT- en "
                    "ABR-concepten (https://data.cultureelerfgoed.nl/term/id/cht/... "
                    "resp. .../abr/...; in books 250.377 resp. 18.595 koppelingen) "
                    "-- dezelfde concept-URI's als in de CHO-dataset, dus te vinden "
                    "met zoek_concept_termennetwerk() en daarna hier te gebruiken "
                    "als ?boek sdo:about <concept-URI>; de CHT- en ABR-"
                    "thesaurusgraphs staan ook op dit endpoint, voor labels; "
                    "(b) eigen trefwoorden (sdo:DefinedTerm met sdo:name); "
                    "(c) personen; (d) monumenten: sdo:about -> "
                    "sdo:LandmarksOrHistoricalBuildings -> sdo:identifier -> "
                    "sdo:PropertyValue met sdo:propertyID \"rijksmonumentnummer\" en "
                    "sdo:value \"36769\" (string). Literatuur over een rijksmonument: "
                    "?boek sdo:about ?m . ?m sdo:identifier ?id . ?id sdo:propertyID "
                    "\"rijksmonumentnummer\" ; sdo:value \"36769\" . Deze koppeling is "
                    "dun (3.035 monumentverwijzingen in books, 695 in article) -- "
                    "0 treffers betekent niet dat er geen literatuur is; zoek dan "
                    "ook op plaats (sdo:spatialCoverage -> sdo:Place met sdo:name, "
                    "bv. 'Eede') en op titelwoorden."
                ),
            },
        ],
    },
}


def get_known_value_uris(topic: str) -> dict[str, str]:
    """Return the known_value_uris mapping of a topic's primary pattern.

    Single source of truth for concept URIs such as the legal_status and
    monument_aard values -- gemeente.py and area.py import this instead of
    hardcoding the same URIs again as local module constants.
    """
    return dict(SEMANTIC_TOPICS[topic]["patterns"][0]["known_value_uris"])


def list_topics() -> list[dict]:
    """Return available dataset semantics topics."""
    return [
        {
            "topic": key,
            "title": value["title"],
            "description": value["description"],
        }
        for key, value in sorted(SEMANTIC_TOPICS.items())
    ]


def describe_topic(topic: str) -> dict:
    """Return guidance for a dataset semantics topic."""
    key = topic.lower().strip()

    if key not in SEMANTIC_TOPICS:
        return {
            "found": False,
            "topic": topic,
            "available_topics": sorted(SEMANTIC_TOPICS.keys()),
        }

    return {
        "found": True,
        "topic": key,
        **SEMANTIC_TOPICS[key],
    }


def format_topics() -> str:
    """Return available dataset semantics topics as readable text."""
    lines = ["Beschikbare dataset semantics topics:"]

    for item in list_topics():
        lines.append(
            f"- {item['topic']}: {item['title']} - {item['description']}"
        )

    return "\n".join(lines)


def format_topic(topic: str) -> str:
    """Return dataset semantics guidance as readable text."""
    data = describe_topic(topic)

    if not data["found"]:
        available = ", ".join(data["available_topics"])
        return f"Onbekend semantics topic: {topic}\n\nBeschikbaar: {available}"

    lines = [
        f"Topic: {data['title']}",
        "",
        data["description"],
        "",
        "Patronen:",
    ]

    for pattern in data["patterns"]:
        lines.append(f"- {pattern['name']}")
        lines.append(f"  Pad: {' -> '.join(pattern['path'])}")

        if "known_values" in pattern:
            values = ", ".join(pattern["known_values"])
            lines.append(f"  Bekende waarden: {values}")

        lines.append(f"  Gebruik: {pattern['guidance']}")

    return "\n".join(lines)
