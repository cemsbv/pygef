from __future__ import annotations

import io
import typing
from pathlib import Path
from typing import Any, cast
from warnings import warn
import polars as pl
import textwrap

from .cpt import CPTXml, Location

from lxml import etree


def process_cpt_result(el: etree.Element, **kwargs: dict[Any, Any]) -> pl.DataFrame:
    """Resolver for conePenetrometerSurvey/cptcommon:conePenetrationTest/cptcommon:cptResult."""
    text_enc = el.find(
        "./swe:encoding/swe:TextEncoding", namespaces=kwargs["namespaces"]
    )
    decimal_sep = text_enc.attrib["decimalSeparator"]
    if decimal_sep != ".":
        warn(
            f"Found a '{decimal_sep}' as decimal separator, this may lead to parsing errors."
        )

    delimiter = text_enc.attrib["tokenSeparator"]
    new_line_char = text_enc.attrib["blockSeparator"]

    # we strip the data because there is leading and trailing whitespace.
    data = el.find("./cptcommon:values", namespaces=kwargs["namespaces"]).text.strip()
    return pl.read_csv(
        data.encode(),
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


def parse_bool(val: str, **kwargs: dict[Any, Any]) -> bool:
    val = val.lower()
    if val == "ja":
        return True
    if val == "nee":
        return False
    return bool(val)


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


# maps keyword argument to:
# xpath: query passed to elementree.find
# resolver: A function that converts the string to the proper datatype
#           Fn(str) -> Any
# el-atrr: Optional: attribute of an element taken before send to resolver
CPT_ATTRIBS = {
    "bro_id": {"xpath": "brocom:broId"},
    "research_report_date": {"xpath": "./researchReportDate/brocom:date"},
    "cpt_standard": {"xpath": "cptStandard"},
    "standardized_location": {
        "xpath": "./standardizedLocation/brocom:location",
        "resolver": parse_brocom_location,
    },
    "dissipationtest_performed": {
        "xpath": "./conePenetrometerSurvey/cptcommon:dissipationTestPerformed",
        "resolver": parse_bool,
        "el-attr": "text",
    },
    "quality_class": {
        "xpath": "./conePenetrometerSurvey/cptcommon:qualityClass",
    },
    "data": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrationTest/cptcommon:cptResult",
        "resolver": process_cpt_result,
    },
}


def read_cpt(file: io.BytesIO | Path | str) -> list[CPTXml]:
    tree = etree.parse(file)

    root = tree.getroot()
    namespaces = root.nsmap
    dd = root.find("dispatchDocument", namespaces)

    out: list[CPTXml] = []

    cpts = dd.findall("./*")
    for cpt in cpts:

        # kwargs of attribute: value
        resolved = dict()

        for (atrib, d) in CPT_ATTRIBS.items():
            d = cast(dict[str, Any], d)
            el = cpt.find(d["xpath"], cpt.nsmap)

            if el is not None:
                if "resolver" in d:
                    func = d["resolver"]

                    if "el-attr" in d:
                        el = getattr(el, d["el-attr"])

                    # ignore mypy error as it thinks we get a
                    # str from the dict
                    resolved[atrib] = func(el, namespaces=namespaces)
                else:
                    resolved[atrib] = el.text
        out.append(CPTXml(**resolved))

    return out
