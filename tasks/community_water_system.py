import os
from pathlib import Path

import requests
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD, OWL, TIME


SAB = Namespace("https://www.epa.gov/ontology/pwssab#")
CGSR = Namespace("http://data.cgsearth.org/pwsa/")

_PREFIX = {
    "pwsa": CGSR,
    "sab": SAB,
    "geo": Namespace("http://www.opengis.net/ont/geosparql#"),
    "sf": Namespace("http://www.opengis.net/ont/sf#"),
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "owl": OWL,
    "time": TIME,
}

def community_water_system_feature(task_instance):
    """Fetch and triplify community water system features."""

    query_url = (
        "https://services.arcgis.com/cJ9YHowT8TU7DUyn/"
        "arcgis/rest/services/Water_System_Boundaries/"
        "FeatureServer/0/query"
    )

    params = {
        "where": "1=1",
        "outFields": (
            "PWSID,PWS_Name,Population_Served_Count,"
            "Area_SqKM,Service_Area_Type"
        ),
        "returnGeometry": "true",
        "outSR": 4326,
        "f": "geojson",
    }

    response = requests.get(query_url, params=params, timeout=60)
    response.raise_for_status()
    feature_collection = response.json()

    graph = Graph()
    graph.bind("sab", SAB)
    graph.bind("pwsa", CGSR)

    for feature in feature_collection.get("features", []):
        properties = feature.get("properties", {})

        pwsid = properties.get("PWSID")
        if not pwsid:
            continue

        feature_iri = CGSR[str(pwsid)]

        graph.add(
            (
                feature_iri,
                RDF.type,
                SAB.CommunityWaterSystemBoundary,
            )
        )

        graph.add(
            (
                feature_iri,
                SAB.pwsIdentifier,
                Literal(pwsid),
            )
        )

        pws_name = properties.get("PWS_Name")
        if pws_name:
            graph.add(
                (
                    feature_iri,
                    SAB.pwsName,
                    Literal(pws_name),
                )
            )

        population = properties.get("Population_Served_Count")
        if population is not None:
            graph.add(
                (
                    feature_iri,
                    SAB.populationServedCount,
                    Literal(
                        population,
                        datatype=XSD.nonNegativeInteger,
                    ),
                )
            )

        service_area_type = properties.get("Service_Area_Type")
        if service_area_type:
            graph.add(
                (
                    feature_iri,
                    SAB.serviceAreaType,
                    Literal(service_area_type),
                )
            )
    for prefix in _PREFIX:
        graph.bind(prefix, _PREFIX[prefix])

    output_directory = Path(os.environ.get("OUTPUT_DIR", "/output"))
    output_directory.mkdir(parents=True, exist_ok=True)

    destination = output_directory / "pwsa.ttl"
    graph.serialize(destination=destination, format="turtle")

    return destination