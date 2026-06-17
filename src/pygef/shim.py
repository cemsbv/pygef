from __future__ import annotations

import io
import os
import re
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pygef.bore import BoreData
from pygef.broxml.parse_bore import read_bore as read_bore_xml
from pygef.broxml.parse_cpt import read_cpt as read_cpt_xml
from pygef.common import Location, VerticalDatumClass, convert_coordinate_system_to_gml
from pygef.cpt import CPTData
from pygef.exceptions import ParseGefError
from pygef.gef.parse_bore import _GefBore
from pygef.gef.parse_cpt import _GefCpt

# A GEF header line looks like "#KEY= value" or "#KEY = value". Accepting any
# such line (not only #GEFID) makes string-vs-path disambiguation robust to
# GEF files that don't put #GEFID first.
_GEF_HEADER_RE = re.compile(r"^\s*#[A-Z][A-Z0-9]*\s*=")

_PEEK_BYTES = 128


class _InputKind(Enum):
    BYTES = "bytes"
    PATH = "path"
    GEF_TEXT = "gef_text"
    XML_TEXT = "xml_text"


class _DetectedFormat(str, Enum):
    GEF = "gef"
    XML = "xml"


_LSTRIP_CHARS = " \t\r\n﻿"  # whitespace + optional UTF-8 BOM

# A string looks like a filesystem path if it contains a path separator OR ends
# with a short alphanumeric extension. Bare random words ("foo bar baz") fail
# this test and so are reported as ambiguous input rather than missing files.
_PATH_LIKE_RE = re.compile(r"[/\\]|\.[A-Za-z0-9]{1,8}$")


def _looks_like_gef(head: str) -> bool:
    return bool(_GEF_HEADER_RE.match(head.lstrip(_LSTRIP_CHARS)))


def _looks_like_xml(head: str) -> bool:
    return head.lstrip(_LSTRIP_CHARS).startswith("<")


def _detect_format(head: str, source: str) -> _DetectedFormat:
    if _looks_like_gef(head):
        return _DetectedFormat.GEF
    if _looks_like_xml(head):
        return _DetectedFormat.XML
    raise ValueError(
        f"Could not detect file format of {source}: content matches neither "
        "the GEF header pattern (#KEY=...) nor the XML root element pattern "
        "(starting with '<')."
    )


def _classify_input(
    file: io.BytesIO | Path | str,
) -> tuple[_InputKind, _DetectedFormat, Any]:
    """
    Classify ``file`` into one of the four input kinds and detect whether the
    content looks like GEF or XML.

    Returns ``(kind, detected_format, payload)`` where ``payload`` is the value
    to hand off to the chosen parser (BytesIO/Path/string).

    Raises ``FileNotFoundError`` if ``file`` resolves to a path that doesn't
    exist on disk; raises ``ValueError`` if the content cannot be classified
    as GEF or XML.
    """
    if isinstance(file, io.BytesIO):
        pos = file.tell()
        head = file.read(_PEEK_BYTES).decode(errors="ignore")
        file.seek(pos)
        return _InputKind.BYTES, _detect_format(head, "BytesIO input"), file

    if isinstance(file, Path):
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        with open(file, encoding="utf-8", errors="ignore") as f:
            head = f.read(_PEEK_BYTES)
        return _InputKind.PATH, _detect_format(head, str(file)), file

    if isinstance(file, str):
        if _looks_like_gef(file):
            return _InputKind.GEF_TEXT, _DetectedFormat.GEF, file
        if _looks_like_xml(file):
            return _InputKind.XML_TEXT, _DetectedFormat.XML, file
        if os.path.exists(file):
            with open(file, encoding="utf-8", errors="ignore") as f:
                head = f.read(_PEEK_BYTES)
            return _InputKind.PATH, _detect_format(head, file), file

        raise ValueError(
            "Could not interpret string input: it does not look like GEF or "
            "XML and is not an existing filesystem path."
        )

    raise TypeError(
        f"Unsupported file type {type(file).__name__}; "
        "expected io.BytesIO, pathlib.Path, or str."
    )


def _check_engine_match(engine: str, detected_format: _DetectedFormat) -> None:
    """Raise if the user-forced engine doesn't match the detected format."""
    if engine == "auto":
        return
    if engine != detected_format:
        raise ValueError(
            f"engine={engine!r} but file content looks like {detected_format!r}; "
            "refusing to parse."
        )


def read_bore(
    file: io.BytesIO | Path | str,
    index: int = 0,
    engine: Literal["auto", "gef", "xml"] = "auto",
) -> BoreData:
    """
    Parse the bore file. Can either be BytesIO, Path or str

    :param file: bore file. A ``str`` argument is interpreted as raw file
        content if it starts with a GEF header line (``#KEY=...``) or with
        ``<`` (XML); otherwise it is treated as a filesystem path.
    :param index: only valid for xml files
    :param engine: default is "auto". Parsing engine.
        When set to "gef" or "xml" the engine must match the detected file
        content, otherwise a ValueError is raised.
    """
    kind, detected_format, payload = _classify_input(file)
    _check_engine_match(engine, detected_format)

    if detected_format == "gef":
        if index > 0:
            raise ValueError("an index > 0 not supported for GEF files")
        try:
            if kind is _InputKind.BYTES:
                gef_bore = _GefBore(string=payload.read().decode())
            elif kind is _InputKind.PATH:
                gef_bore = _GefBore(path=payload)
            else:
                gef_bore = _GefBore(string=payload)
        except ValueError as e:
            raise ParseGefError(str(e)) from e
        return gef_bore_to_bore_data(gef_bore)

    return read_bore_xml(payload)[index]


def read_cpt(
    file: io.BytesIO | Path | str,
    index: int = 0,
    engine: Literal["auto", "gef", "xml"] = "auto",
    replace_column_voids: bool = True,
    remove_pre_excavated_rows: bool = True,
) -> CPTData:
    """
    Parse the cpt file. Can either be BytesIO, Path or str

    :param file: cpt file. A ``str`` argument is interpreted as raw file
        content if it starts with a GEF header line (``#KEY=...``) or with
        ``<`` (XML); otherwise it is treated as a filesystem path.
    :param index: only valid for xml files
    :param engine: default is "auto". Parsing engine.
        When set to "gef" or "xml" the engine must match the detected file
        content, otherwise a ValueError is raised.
    :param replace_column_voids: default True. How to handle rows with void values.
        If true, replace void values with nulls or interpolate; else retain value.
    :param remove_pre_excavated_rows: default True. How to handle pre-excavated row values.
        If true, drop rows above pre-excavated depth; else retain.
    """
    kind, detected_format, payload = _classify_input(file)
    _check_engine_match(engine, detected_format)

    if detected_format == "gef":
        if index > 0:
            raise ValueError("an index > 0 not supported for GEF files")
        try:
            if kind is _InputKind.BYTES:
                gef = _GefCpt(
                    string=payload.read().decode(),
                    replace_column_voids=replace_column_voids,
                    remove_pre_excavated_rows=remove_pre_excavated_rows,
                )
            elif kind is _InputKind.PATH:
                gef = _GefCpt(
                    path=payload,
                    replace_column_voids=replace_column_voids,
                    remove_pre_excavated_rows=remove_pre_excavated_rows,
                )
            else:
                gef = _GefCpt(
                    string=payload,
                    replace_column_voids=replace_column_voids,
                    remove_pre_excavated_rows=remove_pre_excavated_rows,
                )
        except ValueError as e:
            raise ParseGefError(str(e)) from e
        return gef_cpt_to_cpt_data(gef)

    return read_cpt_xml(payload)[index]


def convert_height_system_to_vertical_datum(height_system: float) -> str:
    if height_system == 31000.0:
        return "nap"
    else:
        return f"{int(height_system):05d}"


def gef_cpt_to_cpt_data(gef_cpt: _GefCpt) -> CPTData:
    kwargs: dict[str, Any] = {}

    kwargs["delivered_location"] = Location(
        # all gef files are RD new
        srs_name=convert_coordinate_system_to_gml(gef_cpt.coordinate_system),
        x=gef_cpt.x,
        y=gef_cpt.y,
    )
    kwargs["standardized_location"] = None
    kwargs["bro_id"] = None
    kwargs["alias"] = gef_cpt.test_id
    kwargs["data"] = gef_cpt.df
    kwargs["column_void_mapping"] = gef_cpt.columns_info.description_to_void_mapping
    kwargs["raw_headers"] = gef_cpt._headers
    kwargs["research_report_date"] = gef_cpt.file_date
    kwargs["cpt_standard"] = None
    kwargs["groundwater_level"] = gef_cpt.groundwater_level
    kwargs["dissipationtest_performed"] = None
    kwargs["quality_class"] = gef_cpt.cpt_class
    kwargs["predrilled_depth"] = gef_cpt.pre_excavated_depth
    kwargs["final_depth"] = gef_cpt.end_depth_of_penetration_test
    kwargs["cpt_description"] = ""
    kwargs["cpt_type"] = gef_cpt.type_of_cone_penetration_test
    kwargs["cone_surface_area"] = gef_cpt.nom_surface_area_cone_tip
    kwargs["cone_diameter"] = None
    kwargs["cone_surface_quotient"] = gef_cpt.net_surface_area_quotient_of_the_cone_tip
    kwargs["cone_to_friction_sleeve_distance"] = (
        gef_cpt.distance_between_cone_and_centre_of_friction_casing
    )
    kwargs["cone_to_friction_sleeve_surface_area"] = None
    kwargs["cone_to_friction_sleeve_surface_quotient"] = (
        gef_cpt.net_surface_area_quotient_of_the_friction_casing
    )

    kwargs["zlm_cone_resistance_before"] = (
        gef_cpt.zero_measurement_cone_before_penetration_test
    )
    kwargs["zlm_cone_resistance_after"] = (
        gef_cpt.zero_measurement_cone_after_penetration_test
    )
    kwargs["zlm_inclination_ew_before"] = (
        gef_cpt.zero_measurement_inclination_ew_before_penetration_test
    )
    kwargs["zlm_inclination_ew_after"] = (
        gef_cpt.zero_measurement_inclination_ew_after_penetration_test
    )
    kwargs["zlm_inclination_ns_before"] = (
        gef_cpt.zero_measurement_inclination_ns_before_penetration_test
    )
    kwargs["zlm_inclination_ns_after"] = (
        gef_cpt.zero_measurement_inclination_ns_after_penetration_test
    )
    kwargs["zlm_inclination_resultant_before"] = None
    kwargs["zlm_inclination_resultant_after"] = None
    kwargs["zlm_local_friction_before"] = (
        gef_cpt.zero_measurement_friction_before_penetration_test
    )
    kwargs["zlm_local_friction_after"] = (
        gef_cpt.zero_measurement_friction_after_penetration_test
    )
    kwargs["zlm_pore_pressure_u1_before"] = (
        gef_cpt.zero_measurement_ppt_u1_before_penetration_test
    )
    kwargs["zlm_pore_pressure_u2_before"] = (
        gef_cpt.zero_measurement_ppt_u2_before_penetration_test
    )
    kwargs["zlm_pore_pressure_u3_before"] = (
        gef_cpt.zero_measurement_ppt_u3_before_penetration_test
    )
    kwargs["zlm_pore_pressure_u1_after"] = (
        gef_cpt.zero_measurement_ppt_u1_after_penetration_test
    )
    kwargs["zlm_pore_pressure_u2_after"] = (
        gef_cpt.zero_measurement_ppt_u2_after_penetration_test
    )
    kwargs["zlm_pore_pressure_u3_after"] = (
        gef_cpt.zero_measurement_ppt_u3_after_penetration_test
    )
    kwargs["delivered_vertical_position_offset"] = gef_cpt.zid
    kwargs["delivered_vertical_position_datum"] = VerticalDatumClass(
        f"{int(gef_cpt.height_system):05d}"
    )

    # TODO! parse measurementtext 9 in gef?
    kwargs["delivered_vertical_position_reference_point"] = "unknown"

    return CPTData(**kwargs)


def gef_bore_to_bore_data(gef_bore: _GefBore) -> BoreData:
    kwargs: dict[str, Any] = {}

    kwargs["delivered_location"] = Location(
        # all gef files are RD new
        srs_name=convert_coordinate_system_to_gml(gef_bore.coordinate_system),
        x=gef_bore.x,
        y=gef_bore.y,
    )
    kwargs["standardized_location"] = None
    kwargs["bro_id"] = None
    kwargs["alias"] = gef_bore.test_id
    kwargs["groundwater_level"] = None
    kwargs["research_report_date"] = gef_bore.file_date
    kwargs["description_procedure"] = "unknown"
    kwargs["delivered_vertical_position_offset"] = gef_bore.zid
    kwargs["delivered_vertical_position_datum"] = "unknown"
    kwargs["delivered_vertical_position_reference_point"] = "unknown"
    kwargs["bore_rock_reached"] = None
    kwargs["final_bore_depth"] = None
    kwargs["final_sample_depth"] = None
    kwargs["bore_hole_completed"] = None
    kwargs["data"] = gef_bore.df
    return BoreData(**kwargs)
