from __future__ import annotations

import io
import os
from pathlib import Path

from lxml import etree

from pygef.broxml import resolvers
from pygef.broxml.xml_parser import read_xml
from pygef.cpt import CPTData

# maps keyword argument to:
# xpath: query passed to elementree.find
# resolver: A function that converts the string to the proper datatype
#           Fn(str) -> Any
# el-atrr: Optional: attribute of an element taken before send to resolver
CPT_ATTRIBS = {
    "bro_id": {"xpath": "brocom:broId"},
    "research_report_date": {
        "xpath": "ns11:researchReportDate/brocom:date",
        "resolver": resolvers.parse_date,
        "el-attr": "text",
    },
    "cpt_standard": {"xpath": "ns11:cptStandard"},
    "delivered_location": {
        "xpath": "ns11:deliveredLocation/cptcommon:location",
        "resolver": resolvers.parse_gml_location,
    },
    "standardized_location": {
        "xpath": "ns11:standardizedLocation/brocom:location",
        "resolver": resolvers.parse_gml_location,
    },
    "dissipationtest_performed": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:dissipationTestPerformed",
        "resolver": resolvers.parse_bool,
        "el-attr": "text",
    },
    "quality_class": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:qualityClass",
        "resolver": resolvers.parse_quality_class,
        "el-attr": "text",
    },
    "groundwater_level": {
        "xpath": "ns11:additionalInvestigation/cptcommon:groundwaterLevel",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "predrilled_depth": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:trajectory/cptcommon:predrilledDepth",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "final_depth": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:trajectory/cptcommon:finalDepth",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "data": {
        "xpath": "ns11:conePenetrometerSurvey",
        "resolver": resolvers.process_cpt_result,
    },
    "cpt_description": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:description",
    },
    "cpt_type": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:conePenetrometerType",
    },
    "cone_surface_area": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneSurfaceArea",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "cone_diameter": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneDiameter",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "cone_surface_quotient": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneSurfaceQuotient",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "cone_to_friction_sleeve_distance": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:coneToFrictionSleeveDistance",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "cone_to_friction_sleeve_surface_area": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:frictionSleeveSurfaceArea",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "cone_to_friction_sleeve_surface_quotient": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:frictionSleeveSurfaceQuotient",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_cone_resistance_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:coneResistanceBefore",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_cone_resistance_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:coneResistanceAfter",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_inclination_ew_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationEWBefore",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_ew_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationEWAfter",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_ns_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationNSBefore",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_ns_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationNSAfter",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_resultant_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationResultantBefore",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "zlm_inclination_resultant_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:inclinationResultantAfter",
        "resolver": resolvers.parse_int,
        "el-attr": "text",
    },
    "zlm_local_friction_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:localFrictionBefore",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_local_friction_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:localFrictionAfter",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u1_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU1Before",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u2_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU2Before",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u3_before": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU3Before",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u1_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU1After",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u2_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU2After",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "zlm_pore_pressure_u3_after": {
        "xpath": "ns11:conePenetrometerSurvey/cptcommon:conePenetrometer/cptcommon:zeroLoadMeasurement/cptcommon:porePressureU3After",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "delivered_vertical_position_offset": {
        "xpath": "ns11:deliveredVerticalPosition/cptcommon:offset",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "delivered_vertical_position_datum": {
        "xpath": "ns11:deliveredVerticalPosition/cptcommon:verticalDatum",
        "resolver": resolvers.parse_local_vertical_reference_point_class,
        "el-attr": "text",
    },
    "delivered_vertical_position_reference_point": {
        "xpath": "ns11:deliveredVerticalPosition/cptcommon:localVerticalReferencePoint",
        "resolver": resolvers.lower_text,
        "el-attr": "text",
    },
}


def read_cpt(file: io.BytesIO | Path | str) -> list[CPTData]:
    if isinstance(file, str) and not os.path.exists(file):
        root = etree.fromstring(file).getroot()
    else:
        root = etree.parse(file).getroot()
    return read_xml(root, CPTData, CPT_ATTRIBS, "ns11:dispatchDocument")
