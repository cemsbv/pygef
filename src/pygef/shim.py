from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any, Literal

from pygef.bore import BoreData
from pygef.broxml.parse_bore import read_bore as read_bore_xml
from pygef.broxml.parse_cpt import read_cpt as read_cpt_xml
from pygef.common import Location, VerticalDatumClass, convert_coordinate_system_to_gml
from pygef.cpt import CPTData
from pygef.gef.parse_bore import _GefBore
from pygef.gef.parse_cpt import _GefCpt

GEF_ID = "#GEFID"


def is_gef_file(file: io.BytesIO | Path | str) -> bool:
    """
    gef files start with '#GEFID' so we check the content
    of the file
    """
    if isinstance(file, io.BytesIO):
        pos = file.tell()
        is_gef = file.read(6).decode().startswith(GEF_ID)
        file.seek(pos)
        return is_gef
    if os.path.exists(file):
        with open(file, errors="ignore") as f:
            return f.read(6).startswith(GEF_ID)
    if isinstance(file, str):
        return file[:6].startswith(GEF_ID)
    raise FileNotFoundError("Could not find the GEF file.")


def read_bore(
    file: io.BytesIO | Path | str,
    index: int = 0,
    engine: Literal["auto", "gef", "xml"] = "auto",
) -> BoreData:
    """
    Parse the bore file. Can either be BytesIO, Path or str

    :param file: bore file
    :param index: only valid for xml files
    :param engine: default is "auto". parsing engine.
        Please note that auto engine checks if the files starts with `#GEFID`.
    """
    if engine == "gef" or is_gef_file(file) and engine == "auto":
        if index > 0:
            raise ValueError("an index > 0 not supported for GEF files")
        if isinstance(file, io.BytesIO):
            return gef_bore_to_bore_data(_GefBore(string=file.read().decode()))
        if os.path.exists(file):
            return gef_bore_to_bore_data(_GefBore(path=file))
        else:
            return gef_bore_to_bore_data(_GefBore(string=file))
    return read_bore_xml(file)[index]


def read_cpt(
    file: io.BytesIO | Path | str,
    index: int = 0,
    engine: Literal["auto", "gef", "xml"] = "auto",
    replace_column_voids=True,
) -> CPTData:
    """
    Parse the cpt file. Can either be BytesIO, Path or str

    :param file: bore file
    :param index: only valid for xml files
    :param engine: default is "auto". parsing engine.
    :param replace_column_voids: if true replace void values with nulls or interpolate; else retain value.
        Please note that auto engine checks if the files starts with `#GEFID`.
    """

    if engine == "gef" or is_gef_file(file) and engine == "auto":
        if index > 0:
            raise ValueError("an index > 0 not supported for GEF files")
        if isinstance(file, io.BytesIO):
            return gef_cpt_to_cpt_data(
                _GefCpt(
                    string=file.read().decode(),
                    replace_column_voids=replace_column_voids,
                )
            )
        if os.path.exists(file):
            return gef_cpt_to_cpt_data(
                _GefCpt(path=file, replace_column_voids=replace_column_voids)
            )
        else:
            return gef_cpt_to_cpt_data(
                _GefCpt(string=file, replace_column_voids=replace_column_voids)
            )
    return read_cpt_xml(file)[index]


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
