SEMANTIC_TOPICS = {
    "functions": {
        "title": "Functies",
        "description": (
            "Gebruik functiepaden wanneer een vraag gaat over wat een monument is "
            "of oorspronkelijk was. Filter niet op naam of omschrijving."
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
                    "functiepaden te vinden is. ceo:heeftKennisregistratie leidt naar "
                    "dezelfde ceo:Type-node (identiek aantal triples in een steekproef "
                    "op ceo:Rijksmonument); heeftType is het directe, kortere pad."
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
                    "{ ?rm ceo:heeftOorspronkelijkeFunctie ?fObj . ?fObj ceo:heeftFunctieNaam ?fC . "
                    "?fC skos:prefLabel ?fNaam . FILTER(lang(?fNaam)=\"nl\") "
                    "FILTER(CONTAINS(LCASE(?fNaam), \"kerk\")) BIND(\"oorspronkelijke functie\" AS ?bron) } "
                    "UNION { ?rm ceo:heeftHuidigeFunctie ?fObj . ?fObj ceo:heeftFunctieNaam ?fC . "
                    "?fC skos:prefLabel ?fNaam . FILTER(lang(?fNaam)=\"nl\") "
                    "FILTER(CONTAINS(LCASE(?fNaam), \"kerk\")) BIND(\"huidige functie\" AS ?bron) } "
                    "UNION { ?rm ceo:heeftType ?typeObj . ?typeObj ceo:heeftTypeNaam ?typeC . "
                    "?typeC skos:prefLabel ?fNaam . FILTER(lang(?fNaam)=\"nl\") "
                    "FILTER(CONTAINS(LCASE(?fNaam), \"kerk\")) BIND(\"type\" AS ?bron) } "
                    "UNION { ?rm ceo:heeftOmschrijving ?oObj . ?oObj ceo:omschrijving ?fNaam . "
                    "FILTER(REGEX(LCASE(?fNaam), \"(^|\\\\W)kerk(\\\\W|$)\")) "
                    "BIND(\"omschrijving (onzeker)\" AS ?bron) }.\n"
                    "Selecteer ?bron altijd mee in SELECT DISTINCT. Rijen met "
                    "?bron = 'omschrijving (onzeker)' zijn minder betrouwbaar omdat "
                    "ze op vrije tekst berusten -- toon of behandel ze apart. Zoek "
                    "nooit los in ceo:omschrijving zonder deze markering."
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
                    "<...b2d9a59a-fe1e-4552-9a05-3c2acddff864> voor 'rijksmonument', "
                    "zie known_value_uris) in plaats van op skos:prefLabel-tekst -- "
                    "dat is sneller en vermijdt taalstring-issues. Deze drie "
                    "concept-URI's zijn geverifieerd tegen de live dataset (bron: "
                    "RCE-query 'Tellen van Verschillende Instanties in de Graph')."
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
                    "bijvoorbeeld op 1499 archeologische rijksmonumenten (1492 met "
                    "puntcoordinaten), niet op de 2963 die een naieve COUNT(?cho) "
                    "oplevert. Filter bij voorkeur direct op de concept-URI "
                    "(ceo:heeftMonumentAard <...b673c8c1-5d93-496d-8f9e-89133d579d77> "
                    "voor 'archeologisch') in plaats van op skos:prefLabel-tekst -- "
                    "geverifieerd tegen de live dataset, geen taalstring nodig "
                    "(dit concept heeft geen lang-tag op zijn prefLabel)."
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
                    "op als er geen beter conceptueel pad bestaat."
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
                    "dataset (1.204.320 triples, ruim vier keer zo veel als "
                    "rijksmonumentnummer) omdat hij op vrijwel elk CHO-type voorkomt, "
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
                    "Polygonen van beschermde stads- en dorpsgezichten staan in de graph "
                    "'gezicht-hvdl' (URI: https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl). "
                    "Gebruik GRAPH <https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl> "
                    "om polygonen op te halen. Het WKT-formaat is een POLYGON in WGS84. "
                    "Ruimtelijke joins (welke monumenten liggen binnen een stadsgezicht-polygoon) "
                    "moeten lokaal worden uitgevoerd met Shapely; gebruik geof:sfWithin niet."
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
    "archaeology": {
        "title": "Archeologische objecten",
        "description": (
            "Gebruik dit topic voor vragen over archeologische terreinen, "
            "onderzoeksgebieden, complexen, vondstlocaties, grondsporen en "
            "vondsten. Dit zijn aparte classes naast ceo:Rijksmonument, "
            "onderling verbonden via ceo:bevatObject / ceo:ligtInObject."
        ),
        "patterns": [
            {
                "name": "Containment-netwerk (bevatObject / ligtInObject)",
                "path": ["ceo:bevatObject"],
                "guidance": (
                    "ceo:bevatObject en zijn inverse ceo:ligtInObject (samen 938.756 "
                    "triples, exact gelijk aantal in beide richtingen) verbinden "
                    "archeologische classes in een netwerk, geen strikte boom -- "
                    "dezelfde class kan via meerdere bovenliggende classes gevuld "
                    "worden. Empirisch voorkomende combinaties (aantal triples): "
                    "ceo:Rijksmonument bevatObject ceo:ArcheologischTerrein (3.665); "
                    "ceo:ArcheologischTerrein bevatObject ceo:ArcheologischComplex (18.548); "
                    "ceo:ArcheologischOnderzoeksgebied bevatObject ceo:ArcheologischComplex (9.362); "
                    "ceo:ArcheologischOnderzoeksgebied bevatObject ceo:Vondstlocatie (40.005); "
                    "ceo:Vondstlocatie bevatObject ceo:ArcheologischComplex (332.327); "
                    "ceo:Vondstlocatie bevatObject ceo:Grondsporen (91.832); "
                    "ceo:Vondstlocatie bevatObject ceo:Vondsten (444.867). "
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
                "name": "Archis2-identificatienummers",
                "path": ["ceo:archis2Monumentnummer"],
                "guidance": (
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
        ],
    },
}


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
