SEMANTIC_TOPICS = {
    "functions": {
        "title": "Functions",
        "description": (
            "Use function relations and function concepts when a question is about "
            "what an object is or was used for. Do not filter on object names."
        ),
        "properties": [
            {
                "property": "ceo:heeftFunctie",
                "role": "Links an object or knowledge node to a function concept.",
                "guidance": (
                    "Use this route for questions about churches, houses, mills, "
                    "farms, schools and other object functions."
                ),
            },
            {
                "property": "ceo:hoofdfunctie",
                "role": "Marks whether a function is the primary function.",
                "guidance": (
                    "When an object has multiple functions, prefer records where "
                    "ceo:hoofdfunctie is true if the user asks for the main function."
                ),
            },
        ],
    },
    "names": {
        "title": "Names",
        "description": (
            "Names are useful for presentation, but usually not for selecting objects."
        ),
        "properties": [
            {
                "property": "ceo:heeftNaam",
                "role": "Links an object to a name node.",
                "guidance": "Use this to retrieve names, not as the first filter.",
            },
            {
                "property": "ceo:naam",
                "role": "Literal value of a name node.",
                "guidance": "Use for display after selecting objects through type, function or location.",
            },
            {
                "property": "ceo:huidigeNaam",
                "role": "Marks whether a name is current.",
                "guidance": "Prefer current names when multiple names exist.",
            },
            {
                "property": "ceo:formeelStandpunt",
                "role": "Marks whether a name reflects the formal RCE position.",
                "guidance": "Prefer formal RCE names when available.",
            },
        ],
    },
    "status": {
        "title": "Status",
        "description": (
            "Use status properties to distinguish active register objects from other records."
        ),
        "properties": [
            {
                "property": "ceo:heeftJuridischeStatus",
                "role": "Links an object to its legal status concept.",
                "guidance": (
                    "Use this when the user asks for active rijksmonumenten or formally "
                    "protected objects."
                ),
            },
            {
                "property": "ceo:registergegeven",
                "role": "Marks whether a statement is a register fact.",
                "guidance": "Use when formal register information matters.",
            },
        ],
    },
    "location": {
        "title": "Location",
        "description": (
            "Location data can be spread across multiple nodes and graphs. "
            "Use concept URIs for municipalities and provinces."
        ),
        "properties": [
            {
                "property": "ceo:heeftLocatieAanduiding",
                "role": "Links an object to a location indication node.",
                "guidance": "Inspect this route for addresses, places and administrative locations.",
            },
            {
                "property": "ceo:heeftBasisregistratieRelatie",
                "role": "Links location data to basic registration relations.",
                "guidance": "Use this route when looking for municipality or BAG-related information.",
            },
            {
                "property": "ceo:heeftGemeente",
                "role": "Links a registration relation to a municipality concept.",
                "guidance": "Resolve the municipality label first, then filter by the URI.",
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
        "Belangrijke properties:",
    ]

    for prop in data["properties"]:
        lines.extend(
            [
                f"- {prop['property']}",
                f"  Rol: {prop['role']}",
                f"  Gebruik: {prop['guidance']}",
            ]
        )

    return "\n".join(lines)