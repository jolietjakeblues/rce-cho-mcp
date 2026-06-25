from rce_cho_mcp.config import DEFAULT_GRAPH
from rce_cho_mcp.planner.models import QueryPlan


def build_sparql(plan: QueryPlan) -> str:
    """Build SPARQL from a QueryPlan."""

    if (
        plan.intent == "count"
        and plan.entity == "Rijksmonument"
        and plan.filters.get("gemeente")
    ):
        gemeente = plan.filters["gemeente"]

        return f"""PREFIX graph: <https://linkeddata.cultureelerfgoed.nl/graph/>
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rn: <https://data.cultureelerfgoed.nl/term/id/rn/2/>

SELECT (COUNT(DISTINCT ?rm) AS ?aantal)
WHERE {
  GRAPH graph:instanties-rce {
    ?rm a ceo:Rijksmonument .
    ?rm ceo:heeftJuridischeStatus rn:b2d9a59a-fe1e-4552-9a05-3c2acddff864 .
    ?rm ceo:heeftBasisregistratieRelatie ?rel .
    ?rel ceo:heeftGemeente ?gemeente .
  }

  GRAPH graph:owms {
    ?gemeente skos:prefLabel "Zeist"@nl .
  }
}

    raise ValueError(f"Unsupported query plan: {plan}")