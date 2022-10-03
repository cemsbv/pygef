from __future__ import annotations

from warnings import warn
from typing import Any
from lxml import etree

from pygef.broxml import QualityClass, Location
import polars as pl


def lower_text(val: str, **kwargs: dict[Any, Any]) -> str:
    return val.lower()


def parse_float(val: str, **kwargs: dict[Any, Any]) -> float:
    return float(val)


def parse_int(val: str, **kwargs: dict[Any, Any]) -> int:
    return int(val)


def parse_bool(val: str, **kwargs: dict[Any, Any]) -> bool:
    val = val.lower()
    if val == "ja":
        return True
    if val == "nee":
        return False
    return bool(val)


def process_cpt_result(el: etree.Element, **kwargs: dict[Any, Any]) -> pl.DataFrame:
    namespaces = kwargs["namespaces"]
    """Resolver for conePenetrometerSurvey/cptcommon:conePenetrationTest/cptcommon:cptResult."""

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


def parse_brocom_location(el: etree.Element, **kwargs: dict[Any, Any]) -> Location:
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
        return QualityClass.Class2
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
