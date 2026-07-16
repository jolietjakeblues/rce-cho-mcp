"""
Test: bereken pand-footprint-oppervlakte (m2) uit BAG-geometrie, gegeven een adres.

Workflow:
1. Adres -> RD-coördinaat via PDOK Locatieserver (api.pdok.nl)
2. Coördinaat -> pandgeometrie via BAG WFS bbox-query (service.pdok.nl)
3. Footprint-oppervlakte = shapely .area op de polygon (RD, dus al in m2)
4. Vergelijk met BAG-attributen oppervlakte_min/oppervlakte_max
   (dit zijn de NEN2580-gebruiksoppervlaktes van de verblijfsobjecten
   in het pand, GEEN footprint - twee verschillende dingen)

Gebruik: python3 pand_oppervlakte.py "Smallepad 5 Amersfoort"
"""

import sys
import json
import urllib.request
import urllib.parse
from shapely.geometry import shape


def adres_naar_rd(adres: str) -> tuple[float, float, dict]:
    """Resolve adres naar RD-coördinaat via PDOK Locatieserver."""
    q = urllib.parse.quote(adres)
    url = f"https://api.pdok.nl/bzk/locatieserver/search/v3_1/free?q={q}&fq=type:adres&rows=1"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.load(resp)

    docs = data["response"]["docs"]
    if not docs:
        raise ValueError(f"Geen adres gevonden voor: {adres}")

    doc = docs[0]
    # centroide_rd = "POINT(x y)"
    coords = doc["centroide_rd"].replace("POINT(", "").replace(")", "").split()
    x, y = float(coords[0]), float(coords[1])
    return x, y, doc


def rd_naar_pand(x: float, y: float, marge: float = 25.0) -> dict:
    """Haal pandgeometrie op via BAG WFS bbox-query rond een RD-punt."""
    bbox = f"{x-marge},{y-marge},{x+marge},{y+marge},EPSG:28992"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": "bag:pand",
        "outputFormat": "application/json",
        "srsName": "EPSG:28992",
        "bbox": bbox,
    }
    url = "https://service.pdok.nl/lv/bag/wfs/v2_0?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.load(resp)

    features = data.get("features", [])
    if not features:
        raise ValueError("Geen pand gevonden binnen de bbox. Vergroot de marge.")

    # Bij meerdere panden in de bbox: pak het pand waarvan het punt binnen de geometrie valt
    from shapely.geometry import Point
    punt = Point(x, y)
    for f in features:
        geom = shape(f["geometry"])
        if geom.contains(punt) or geom.distance(punt) < 1.0:
            return f
    return features[0]  # fallback: eerste resultaat


def main():
    adres = sys.argv[1] if len(sys.argv) > 1 else "Smallepad 5 Amersfoort"

    print(f"Adres: {adres}")
    x, y, adres_doc = adres_naar_rd(adres)
    print(f"RD-coördinaat: {x}, {y}")

    pand = rd_naar_pand(x, y)
    props = pand["properties"]
    geom = shape(pand["geometry"])

    footprint_m2 = geom.area

    print()
    print(f"Pand-ID (BAG identificatie): {props.get('identificatie')}")
    print(f"Bouwjaar: {props.get('bouwjaar')}")
    print(f"Status: {props.get('status')}")
    print(f"Gebruiksdoel: {props.get('gebruiksdoel')}")
    print(f"Aantal verblijfsobjecten: {props.get('aantal_verblijfsobjecten')}")
    print()
    print(f"Footprint-oppervlakte (berekend uit geometrie): {footprint_m2:.1f} m2")
    print(f"BAG oppervlakte_min (NEN2580, kleinste vbo): {props.get('oppervlakte_min')} m2")
    print(f"BAG oppervlakte_max (NEN2580, som/grootste vbo): {props.get('oppervlakte_max')} m2")
    print()
    print("Let op: footprint (voetprint van het gebouw) en oppervlakte_min/max")
    print("(gebruiksoppervlakte per verblijfsobject, NEN2580) zijn geen zelfde metriek.")
    print("Een pand met meerdere verdiepingen heeft een kleinere footprint dan de")
    print("opgetelde gebruiksoppervlakte van alle vbo's erin.")


if __name__ == "__main__":
    main()