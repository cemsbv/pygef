from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, List
from warnings import warn

import polars as pl
from lxml import etree

from pygef.common import Location
from pygef.cpt import QualityClass


def lower_text(val: str, **kwargs: dict[Any, Any]) -> str:
    return val.lower()


def parse_float(val: str | None, **kwargs: dict[Any, Any]) -> float | None:
    if isinstance(val, (str, int, float)):
        return float(val)
    return None


def parse_int(val: str | None, **kwargs: dict[Any, Any]) -> int | None:
    if isinstance(val, (str, int, float)):
        return int(val)
    return None


def parse_date(val: str, **kwargs: dict[Any, Any]) -> date:
    return datetime.strptime(val, "%Y-%m-%d").date()


def clean_string(val: str, **kwargs: dict[Any, Any]) -> str:
    if isinstance(val, str):
        return re.sub(r"\W+", "", val)
    return "unknown"


def parse_bool(val: str, **kwargs: dict[Any, Any]) -> bool:
    val = val.lower()
    if val == "ja":
        return True
    if val == "nee" or val == "geen":
        return False
    return bool(val)


def process_bore_result(el: etree.Element, **kwargs: dict[Any, Any]) -> pl.DataFrame:
    namespaces = kwargs["namespaces"]
    upper_boundary = []
    lower_boundary = []
    geotechnical_soil_name_iso: List[str] = []
    geotechnical_soil_name_nen: List[str] = []
    color: List[str] = []
    dispersed_inhomogenity: List[bool | None] = []
    organic_matter_content_class: List[str | None] = []
    sand_median_class: List[str | None] = []
    for layer in el.iterfind("bhrgtcom:layer", namespaces=namespaces):
        upper_boundary.append(
            float(layer.find("bhrgtcom:upperBoundary", namespaces=namespaces).text)
        )
        lower_boundary.append(
            float(layer.find("bhrgtcom:lowerBoundary", namespaces=namespaces).text)
        )
        try:
            geotechnical_soil_name_iso.append(
                clean_string(
                    layer.find(
                        "bhrgtcom:soil/bhrgtcom:geotechnicalSoilName",
                        namespaces=namespaces,
                    ).text
                )
            )
        except AttributeError:
            geotechnical_soil_name_iso.append("niet gedefinieerd")
        try:
            geotechnical_soil_name_nen.append(
                clean_string(
                    layer.find(
                        "bhrgtcom:soil/bhrgtcom:soilNameNEN5104",
                        namespaces=namespaces,
                    ).text
                )
            )
        except AttributeError:
            geotechnical_soil_name_nen.append("niet gedefinieerd")
        try:
            color.append(
                clean_string(
                    layer.find(
                        "bhrgtcom:soil/bhrgtcom:colour", namespaces=namespaces
                    ).text
                )
            )
        except AttributeError:
            color.append("onbekend")

        try:
            dispersed_inhomogenity.append(
                parse_bool(
                    layer.find(
                        "bhrgtcom:soil/bhrgtcom:dispersedInhomogeneity",
                        namespaces=namespaces,
                    ).text
                )
            )
        except AttributeError:
            dispersed_inhomogenity.append(None)
        try:
            organic_matter_content_class.append(
                clean_string(
                    layer.find(
                        "bhrgtcom:soil/bhrgtcom:organicMatterContentClass",
                        namespaces=namespaces,
                    ).text
                )
            )
        except AttributeError:
            organic_matter_content_class.append(None)
        try:
            sand_median_class.append(
                clean_string(
                    layer.find(
                        "bhrgtcom:soil/bhrgtcom:sandMedianClass", namespaces=namespaces
                    ).text
                )
            )
        except AttributeError:
            sand_median_class.append(None)

    # merge NEN and ISO names
    geotechnical_soil_name = [
        word if word != "unknown" else geotechnical_soil_name_nen[i]
        for i, word in enumerate(geotechnical_soil_name_iso)
    ]
    variables = locals()
    return pl.DataFrame(
        {
            name: variables[name]
            for name in [
                "upper_boundary",
                "lower_boundary",
                "geotechnical_soil_name",
                "color",
                "dispersed_inhomogenity",
                "organic_matter_content_class",
                "sand_median_class",
            ]
        }
    )


def process_cpt_result(el: etree.Element, **kwargs: dict[Any, Any]) -> pl.DataFrame:
    """
    Parse the cpt data into a `DataFrame`

    Parameters
    ----------
    el
        conePenetrometerSurvey
    kwargs
        namespaces.
    """
    namespaces = kwargs["namespaces"]

    prefix = "./cptcommon:conePenetrationTest/cptcommon:cptResult"

    text_enc = el.find(f"{prefix}/swe:encoding/swe:TextEncoding", namespaces=namespaces)
    decimal_sep = text_enc.attrib["decimalSeparator"]
    if decimal_sep != ".":
        warn(
            f"Found a '{decimal_sep}' as decimal separator, this may lead to parsing errors."
        )

    delimiter = text_enc.attrib["tokenSeparator"]
    new_line_char = text_enc.attrib["blockSeparator"]

    columns = []
    selection = []

    i = 0
    for param in el.find(
        "./cptcommon:parameters", namespaces=namespaces
    ).iterchildren():
        name = param.tag.split("}")[1]
        if parse_bool(param.text):
            columns.append(name)
            # we select the columns by index
            # this prevents materializing invalid columns
            selection.append(i)
        i += 1

    # we strip the data because there is leading and trailing whitespace.
    data = el.find(f"{prefix}/cptcommon:values", namespaces=namespaces).text.strip()
    return pl.read_csv(
        data.encode(),
        new_columns=columns,
        columns=selection,
        has_header=False,
        sep=delimiter,
        eol_char=new_line_char,
        ignore_errors=True,
    )


def parse_gml_location(el: etree.Element, **kwargs: dict[Any, Any]) -> Location:
    """Resolver for standardizedLocation/brocom:location"""
    srs_name = el.attrib["srsName"]
    pos = next(el.iterfind("./gml:pos", namespaces=kwargs["namespaces"])).text
    (x, y) = parse_position(pos)
    return Location(srs_name=srs_name, x=x, y=y)


def parse_quality_class(val: str, **kwargs: dict[Any, Any]) -> QualityClass:
    val = val.lower().replace(" ", "")
    if val == "klasse1" or val == "class1":
        return QualityClass.Class1
    if val == "klasse2" or val == "class2":
        return QualityClass.Class2
    if val == "klasse3" or val == "class3":
        return QualityClass.Class3
    if val == "klasse4" or val == "class4":
        return QualityClass.Class4
    if val == "onbekend" or val == "unknown":
        return QualityClass.Unknown
    warn(f"quality class '{val}' is unknown")
    return QualityClass.Unknown


def parse_position(pos: str) -> tuple[float, float]:
    """
    Parse a position tuple

    Parameters
    ----------
    pos
        Any of {'x y', 'x,y', 'x;y'}
        where x and y are parsable by float

    Returns
    -------

    """

    if " " in pos:
        splitter = " "
    elif "," in pos:
        splitter = ","
    elif ";" in pos:
        splitter = ";"
    else:
        raise ValueError(f"pygef does not know how to parse '{pos}' position")
    parts = pos.split(splitter)
    return float(parts[0]), float(parts[1])
