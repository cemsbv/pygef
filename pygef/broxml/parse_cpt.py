from __future__ import annotations

import io
from pathlib import Path
from typing import Any, cast
from warnings import warn
import polars as pl

from pygef.cpt import CPTData, Location, QualityClass

from lxml import etree


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


def parse_bool(val: str, **kwargs: dict[Any, Any]) -> bool:
    val = val.lower()
    if val == "ja":
        return True
    if val == "nee":
        return False
    return bool(val)


def parse_int(val: str, **kwargs: dict[Any, Any]) -> int:
    return int(val)


def parse_float(val: str, **kwargs: dict[Any, Any]) -> float:
    return float(val)


def lower_text(val: str, **kwargs: dict[Any, Any]) -> str:
    return val.lower()


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
        "resolver": parse_quality_class,
        "el-attr": "text",
    },
    "predrilled_depth": {
        "xpath": "./conePenetrometerSurvey/cptcommon:trajectory/cptcommon:predrilledDepth",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "final_depth": {
        "xpath": "./conePenetrometerSurvey/cptcommon:trajectory/cptcommon:finalDepth",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "data": {
        "xpath": "./conePenetrometerSurvey",
        "resolver": process_cpt_result,
    },
    "cpt_description": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:description",
    },
    "cpt_type": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:conePenetrometerType",
    },
    "cone_surface_area": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneSurfaceArea",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "cone_diameter": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneDiameter",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "cone_surface_quotient": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneSurfaceQuotient",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "cone_to_friction_sleeve_distance": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneToFrictionSleeveDistance",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "cone_to_friction_sleeve_surface_area": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:frictionSleeveSurfaceArea",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "cone_to_friction_sleeve_surface_quotient": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:frictionSleeveSurfaceQuotient",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_cone_resistance_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:coneResistanceBefore",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_cone_resistance_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:coneResistanceAfter",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_inclination_ew_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationEWBefore",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_ew_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationEWAfter",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_ns_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationNSBefore",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_ns_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationNSAfter",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_resultant_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationResultantBefore",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_resultant_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationResultantAfter",
        "resolver": parse_int,
        "el-attr": "text",
    },
    "zlm_local_friction_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:localFrictionBefore",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_local_friction_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:localFrictionAfter",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u1_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU1Before",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u2_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU2Before",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u3_before": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU3Before",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u1_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU1After",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u2_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU2After",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u3_after": {
        "xpath": "./conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU3After",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "delivered_vertical_position_offset": {
        "xpath": "./deliveredVerticalPosition/cptcommon:offset",
        "resolver": parse_float,
        "el-attr": "text",
    },
    "delivered_vertical_position_datum": {
        "xpath": "./deliveredVerticalPosition/cptcommon:verticalDatum",
        "resolver": lower_text,
        "el-attr": "text",
    },
    "delivered_vertical_position_reference_point": {
        "xpath": "./deliveredVerticalPosition/cptcommon:localVerticalReferencePoint",
        "resolver": lower_text,
        "el-attr": "text",
    },
}


def read_cpt(file: io.BytesIO | Path | str) -> list[CPTData]:
    tree = etree.parse(file)

    root = tree.getroot()
    namespaces = root.nsmap
    dd = root.find("dispatchDocument", namespaces)

    out: list[CPTData] = []

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
            else:
                resolved[atrib] = None
        out.append(CPTData(**resolved))

    return out
