PREFIXES = {
    "ceo": "https://linkeddata.cultureelerfgoed.nl/def/ceo#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "geo": "http://www.opengis.net/ont/geosparql#",
}

CLASSES = {
    "rijksmonument": "ceo:Rijksmonument",
}

PATHS = {
    "gemeente": [
        "?rm ceo:heeftBasisregistratieRelatie ?rel .",
        "?rel ceo:heeftBRKRelatie ?brk .",
        "?brk ceo:gemeentenaam ?gemeente .",
    ],
    "rijksmonumentnummer": [
        "?rm ceo:rijksmonumentnummer ?nummer .",
    ],
    "naam": [
        "OPTIONAL { ?rm ceo:heeftNaam ?naamNode . ?naamNode ceo:naam ?naam . }",
    ],
}