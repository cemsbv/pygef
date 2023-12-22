from __future__ import annotations

import io
import os
import re
from pathlib import Path

from lxml import etree

from pygef.bore import BoreData
from pygef.broxml import resolvers
from pygef.broxml.xml_parser import BaseParser, read_xml

# maps keyword argument to:
# xpath: query passed to elementree.find
# resolver: A function that converts the string to the proper datatype
#           Fn(str) -> Any
# el-atrr: Optional: attribute of an element taken before send to resolver
# Version 1 not supported, this is a WIP
BORE_ATTRIBS_V1 = {
    "research_report_date": {
        "xpath": "./researchReportDate/brocom:date",
        "resolver": resolvers.parse_date,
        "el-attr": "text",
    },
    "description_procedure": {
        "xpath": "./isbhrgt:boreholeSampleDescription/bhrgtcom:descriptionProcedure",
        "el-attr": "text",
    },
    "delivered_location": {
        "xpath": "./isbhrgt:deliveredLocation/bhrgtcom:location/gml:Point",
        "resolver": resolvers.parse_gml_location,
    },
    "delivered_vertical_position_offset": {
        "xpath": "./isbhrgt:deliveredVerticalPosition/bhrgtcom:offset",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "delivered_vertical_position_datum": {
        "xpath": "./isbhrgt:deliveredVerticalPosition/bhrgtcom:verticalDatum",
        "resolver": resolvers.lower_text,
        "el-attr": "text",
    },
    "delivered_vertical_position_reference_point": {
        "xpath": "./isbhrgt:deliveredVerticalPosition/bhrgtcom:localVerticalReferencePoint",
        "resolver": resolvers.lower_text,
        "el-attr": "text",
    },
    "bore_rock_reached": {
        "xpath": "./isbhrgt:boring/bhrgtcom:rockReached",
        "resolver": resolvers.parse_bool,
        "el-attr": "text",
    },
    "final_bore_depth": {
        "xpath": "./isbhrgt:boring/bhrgtcom:finalDepthBoring",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "final_sample_depth": {
        "xpath": "./isbhrgt:boring/bhrgtcom:finalDepthSampling",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "bore_hole_completed": {
        "xpath": "./isbhrgt:boring",
        "resolver": resolvers.parse_bool,
        "el-attr": "text",
    },
}

BORE_ATTRIBS_V2 = {
    "bro_id": {"xpath": "brocom:broId"},
    "research_report_date": {
        "xpath": "./researchReportDate/brocom:date",
        "resolver": resolvers.parse_date,
        "el-attr": "text",
    },
    "groundwater_level": {
        "xpath": "./boring/bhrgtcom:groundwaterLevel",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "description_procedure": {
        "xpath": "./boreholeSampleDescription/bhrgtcom:descriptionProcedure",
        "el-attr": "text",
    },
    "delivered_location": {
        "xpath": "./deliveredLocation/bhrgtcom:location/gml:Point",
        "resolver": resolvers.parse_gml_location,
    },
    "standardized_location": {
        "xpath": "./standardizedLocation/brocom:location",
        "resolver": resolvers.parse_gml_location,
    },
    "delivered_vertical_position_offset": {
        "xpath": "./deliveredVerticalPosition/bhrgtcom:offset",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "delivered_vertical_position_datum": {
        "xpath": "./deliveredVerticalPosition/bhrgtcom:verticalDatum",
        "resolver": resolvers.lower_text,
        "el-attr": "text",
    },
    "delivered_vertical_position_reference_point": {
        "xpath": "./deliveredVerticalPosition/bhrgtcom:localVerticalReferencePoint",
        "resolver": resolvers.lower_text,
        "el-attr": "text",
    },
    "bore_rock_reached": {
        "xpath": "./boring/bhrgtcom:rockReached",
        "resolver": resolvers.parse_bool,
        "el-attr": "text",
    },
    "final_bore_depth": {
        "xpath": "./boring/bhrgtcom:finalDepthBoring",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "final_sample_depth": {
        "xpath": "./boring/bhrgtcom:finalDepthSampling",
        "resolver": resolvers.parse_float,
        "el-attr": "text",
    },
    "bore_hole_completed": {
        "xpath": "./boring/bhrgtcom:boreholeCompleted",
        "resolver": resolvers.parse_bool,
        "el-attr": "text",
    },
    "data": {
        "xpath": "./boreholeSampleDescription/bhrgtcom:descriptiveBoreholeLog",
        "resolver": resolvers.process_bore_result,
    },
}


def read_bore(file: io.BytesIO | Path | str) -> list[BoreData]:
    if isinstance(file, str) and not os.path.exists(file):
        root = etree.fromstring(file, parser=BaseParser).getroot()
    else:
        root = etree.parse(file, parser=BaseParser).getroot()
    match = re.compile(r"xsd/.*/(\d\.\d)")
    matched = match.search(root.nsmap["bhrgtcom"])

    if matched is None:
        raise ValueError("could not find the brhtcom version")
    else:
        if 3.0 >= float(matched.group(1)) < 2.0:
            raise ValueError("only bhrgtcom/2.x is supported ")
        return read_xml(root, BoreData, BORE_ATTRIBS_V2, "dispatchDocument")
