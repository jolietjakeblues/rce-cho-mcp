KNOWN_GRAPH_ROWS = [
    {
        "key": "abr-thesaurus",
        "uri": "https://data.cultureelerfgoed.nl/term/id/abr/thesaurus",
        "group": "thesauri",
        "description": "ABR thesaurus.",
    },
    {
        "key": "cht-thesaurus",
        "uri": "https://data.cultureelerfgoed.nl/term/id/cht/thesaurus",
        "group": "thesauri",
        "description": "CHT thesaurus.",
    },
    {
        "key": "cho-kennis-meta",
        "uri": "https://linkeddata.cultureelerfgoed.nl/cho-kennis/graph/meta",
        "group": "metadata",
        "description": "CHO-KENNIS metadata graph.",
    },
    {
        "key": "aanwijzingenmonumenten",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/aanwijzingenmonumenten",
        "group": "register",
        "description": "Monument designation data.",
    },
    {
        "key": "actorenrol",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/actorenrol",
        "group": "domain",
        "description": "Actor role data.",
    },
    {
        "key": "archiefdagen",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/archiefdagen",
        "group": "domain",
        "description": "Archive day data.",
    },
    {
        "key": "bebouwdeomgeving",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/bebouwdeomgeving",
        "group": "domain",
        "description": "Built environment graph.",
    },
    {
        "key": "buitenplaatsen",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/buitenplaatsen",
        "group": "domain",
        "description": "Historic country estates graph.",
    },
    {
        "key": "gezicht-hvdl",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl",
        "group": "domain",
        "description": (
            "HVDL-aanvulling op beschermde stads- en dorpsgezichten (482 "
            "ceo:Gezicht): oppervlakte (ceo:oppervlakteInHectare / "
            "InVierkanteKilometers), ceo:inProceduredatumGezicht, "
            "ceo:begrenzingsdatumGezicht, ceo:intrekkingsdatumGezicht, "
            "ceo:heeftOndergrondGezicht, ceo:wordtGetoondOp en een "
            "ceo:asWKT-RD-punt (RD). LET OP: de WGS84-polygoon (geo:asWKT) "
            "staat NIET hier maar in instanties-rce."
        ),
    },
    {
        "key": "groenaanleg",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/groenaanleg",
        "group": "domain",
        "description": "Historic green design and landscape architecture graph.",
    },
    {
        "key": "image",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/image",
        "group": "media",
        "description": (
            "Beeldbank-afbeeldingen bij rijksmonumenten (edm:ProvidedCHO met "
            "edm:aggregatedCHO -> rijksmonument, ceo:rijksmonumentnummer, "
            "edm:isShownBy, foaf:depiction). Voor de volledige Beeldbank "
            "(565.170 foto's): zie de aparte dataset 'afbeeldingen' "
            "(query_sparql_afbeeldingen, semantics_describe_topic('images'))."
        ),
    },
    {
        "key": "image-1",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/image-1",
        "group": "media",
        "description": "Additional image metadata graph.",
    },
    {
        "key": "information-model",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/information-model",
        "group": "model",
        "description": "Information model graph.",
    },
    {
        "key": "instanties-rce",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
        "group": "core",
        "description": "RCE instances and object-related data.",
    },
    {
        "key": "linies",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/linies",
        "group": "domain",
        "description": "Defence line data.",
    },
    {
        "key": "msp-indicatie",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/msp_indicatie",
        "group": "register",
        "description": "MSP indication data.",
    },
    {
        "key": "natura2000",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/natura2000",
        "group": "external",
        "description": "Natura 2000 related graph.",
    },
    {
        "key": "oudeomschrijving",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/oudeomschrijving",
        "group": "register",
        "description": "Older object descriptions.",
    },
    {
        "key": "owms",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/owms",
        "group": "thesauri",
        "description": "OWMS concepts, including municipalities and provinces.",
    },
    {
        "key": "print",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/print",
        "group": "output",
        "description": "Print/output graph.",
    },
    {
        "key": "punten",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/punten",
        "group": "geometry",
        "description": "Point geometry graph.",
    },
    {
        "key": "werelderfgoed-hvdl",
        "uri": "https://linkeddata.cultureelerfgoed.nl/graph/werelderfgoed_hvdl",
        "group": "domain",
        "description": (
            "HVDL-aanvulling op werelderfgoed (18 ceo:Werelderfgoed): "
            "ceo:jaarVanInschrijving, ceo:heeftWerelderfgoedType "
            "(cultuur/natuur/gemengd), oppervlakte (ceo:oppervlakteInHectare / "
            "InVierkanteKilometers / InVierkanteMeters op de Geometrie-node) "
            "en ceo:wordtGetoondOp (link naar whc.unesco.org)."
        ),
    },
    {
        "key": "ceox-vuurtorens",
        "uri": "https://linkeddata.cultureelerfgoed.nl/id/ceox/vuurtorens",
        "group": "ceox",
        "description": "CEOX lighthouse graph.",
    },
    {
        "key": "ceox-default",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/ceox/graphs/default",
        "group": "ceox",
        "description": "Default CEOX graph.",
    },
    {
        "key": "cbs-woonplaatsen",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/cho/graphs/cbs_woonplaatsen",
        "group": "external",
        "description": "CBS residential places graph.",
    },
    {
        "key": "cho-default",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/cho/graphs/default",
        "group": "core",
        "description": "Default CHO graph.",
    },
    {
        "key": "tooi-gemeenten",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/tooi/graph/gemeenten",
        "group": "thesauri",
        "description": "TOOI municipalities graph.",
    },
    {
        "key": "ceo-ontology",
        "uri": "https://raw.githubusercontent.com/cultureelerfgoed/CEO/master/CEO_RCE.ttl",
        "group": "model",
        "description": "CEO ontology graph.",
        "queryable": False,
    },
    {
        "key": "triply-owms",
        "uri": "https://triplydb.com/koop/owms/graphs/default",
        "group": "external",
        "description": "External OWMS graph from TriplyDB/KOOP.",
        "queryable": False,
    },
]

# Graphs in ANDERE RCE-datasets dan CHO: elk met een eigen SPARQL-endpoint en
# een eigen query-tool. Bewust een aparte lijst en NIET in KNOWN_GRAPH_ROWS:
# die voedt de allowlist van resolve_concept_label() (config.KNOWN_GRAPHS),
# en dat is een CHO-endpoint-tool -- een GRAPH-clause met een van deze URI's
# op het CHO-endpoint geeft stil 0 resultaten. Aantallen live geteld op
# 2026-11-17.
OTHER_DATASET_GRAPH_ROWS = [
    {
        "dataset": "afbeeldingen",
        "tool": "query_sparql_afbeeldingen",
        "topic": "images",
        "browse": "https://linkeddata.cultureelerfgoed.nl/rce/afbeeldingen",
        "key": "afbeeldingen-photos",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/afbeeldingen/graphs/photos",
        "description": (
            "Beeldbank RCE: 565.170 foto's/tekeningen (sdo:Photograph) met "
            "beeld-URL's, maker, datum, plaats, licentie en koppeling naar "
            "rijksmonumenten (sdo:about)."
        ),
    },
    {
        "dataset": "bibliotheek",
        "tool": "query_sparql_bibliotheek",
        "topic": "library",
        "browse": "https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek",
        "key": "bibliotheek-books",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek/graphs/books",
        "description": (
            "Bibliotheekcatalogus RCE, boeken: 155.422 sdo:Book met titel, "
            "auteur, jaar, uitgever, onderwerpen (CHT/ABR) en plaatsen."
        ),
    },
    {
        "dataset": "bibliotheek",
        "tool": "query_sparql_bibliotheek",
        "topic": "library",
        "browse": "https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek",
        "key": "bibliotheek-article",
        "uri": "https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek/graphs/article",
        "description": (
            "Bibliotheekcatalogus RCE, tijdschriftartikelen: 26.265 "
            "sdo:Article, via sdo:isPartOf gekoppeld aan aflevering, jaargang "
            "en tijdschrift."
        ),
    },
]

# Rijen zonder "queryable"-key zijn standaard query-baar; dit is alleen
# expliciet False voor de twee rijen hierboven. Eén bron voor zowel de
# allowlist in config.py (KNOWN_GRAPHS) als de duidelijke notitie die
# format_graphs() hieronder toont, zodat een graph die hier als "bekend"
# wordt getoond niet alsnog als onbekend wordt afgewezen door
# resolve_concept_label(graph_name=...).
NON_QUERYABLE_GRAPH_KEYS = {
    row["key"] for row in KNOWN_GRAPH_ROWS if not row.get("queryable", True)
}


def list_graphs() -> list[dict]:
    """Return known CHO-KENNIS graphs."""
    return sorted(
        KNOWN_GRAPH_ROWS,
        key=lambda row: (row["group"], row["key"]),
    )


def format_graphs() -> str:
    """Return known CHO-KENNIS graphs as readable text."""
    rows = list_graphs()

    lines = ["Bekende CHO-KENNIS graphs:"]

    current_group = None

    for row in rows:
        if row["group"] != current_group:
            current_group = row["group"]
            lines.append("")
            lines.append(f"{current_group}:")

        lines.append(f"- {row['key']}: {row['uri']}")

        if row["description"]:
            lines.append(f"  {row['description']}")

        if not row.get("queryable", True):
            lines.append(
                "  LET OP: alleen informatief -- niet query-baar via GRAPH <...> "
                "op het RCE CHO SPARQL-endpoint (en dus ook niet geldig als "
                "graph_name in resolve_concept_label()); een GRAPH-clause hiertegen "
                "geeft stil 0 resultaten, zonder foutmelding."
            )

    lines.append("")
    lines.append(
        "Andere RCE-datasets (eigen endpoint en eigen tool -- deze graphs "
        "bestaan NIET op het CHO-endpoint van query_sparql() en zijn geen "
        "geldige graph_name voor resolve_concept_label()):"
    )
    for row in OTHER_DATASET_GRAPH_ROWS:
        lines.append(f"- {row['key']}: {row['uri']}")
        lines.append(f"  {row['description']}")
        lines.append(
            f"  Bevraag met {row['tool']}() -- zie "
            f"semantics_describe_topic('{row['topic']}'). Dataset: {row['browse']}"
        )

    return "\n".join(lines)