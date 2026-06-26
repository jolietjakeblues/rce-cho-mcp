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
        "description": "Protected town and village view data.",
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
        "description": "Image metadata graph.",
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
        "description": "World heritage related graph.",
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
    },
    {
        "key": "triply-owms",
        "uri": "https://triplydb.com/koop/owms/graphs/default",
        "group": "external",
        "description": "External OWMS graph from TriplyDB/KOOP.",
    },
]


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

    return "\n".join(lines)