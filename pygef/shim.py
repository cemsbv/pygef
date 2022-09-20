from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from pygef.gef.cpt import _GefCpt
from pygef.cpt import CPTData
from pygef.cpt import Location, QualityClass
from pygef import broxml


def read_cpt(file: io.BytesIO | Path | str, index: int = 0) -> CPTData:
    # gef files start with '#GEFID' so we check the content
    # of the file

    gef_id = "#GEFID"

    if isinstance(file, io.BytesIO):
        pos = file.tell()
        is_gef = file.read(6).decode().startswith(gef_id)
        file.seek(pos)
    else:
        with open(file, errors="ignore") as f:
            is_gef = f.read(6).startswith(gef_id)

    if is_gef:
        if index > 0:
            raise ValueError("an index > 0 not supported for GEF files")
        if isinstance(file, io.BytesIO):
            return gef_cpt_to_cpt_data(_GefCpt(string=file.read().decode()))
        else:
            return gef_cpt_to_cpt_data(_GefCpt(path=file))

    return broxml.read_cpt(file)[index]


def gef_cpt_to_cpt_data(gef_cpt: _GefCpt) -> CPTData:
    kwargs: dict[str, Any] = {}

    kwargs["standardized_location"] = Location(
        # all gef files are RD new
        srs_name="urn:ogc:def:crs:EPSG::28992",
        x=gef_cpt.x,
        y=gef_cpt.y,
    )
    kwargs["bro_id"] = gef_cpt.project_id
    kwargs["data"] = gef_cpt.df
    kwargs["research_report_date"] = None
    kwargs["cpt_standard"] = None
    kwargs["dissipationtest_performed"] = None
    kwargs["quality_class"] = QualityClass(gef_cpt.cpt_class)
    kwargs["predrilled_depth"] = gef_cpt.pre_excavated_depth
    kwargs["final_depth"] = gef_cpt.end_depth_of_penetration_test
    kwargs["cpt_description"] = ""
    kwargs["cpt_type"] = gef_cpt.type_of_cone_penetration_test
    kwargs["cone_surface_area"] = gef_cpt.nom_surface_area_cone_tip
    kwargs["cone_diameter"] = None
    kwargs["cone_surface_quotient"] = gef_cpt.net_surface_area_quotient_of_the_cone_tip
    kwargs[
        "cone_to_friction_sleeve_distance"
    ] = gef_cpt.distance_between_cone_and_centre_of_friction_casing
    kwargs["cone_to_friction_sleeve_surface_area"] = None
    kwargs[
        "cone_to_friction_sleeve_surface_quotient"
    ] = gef_cpt.net_surface_area_quotient_of_the_friction_casing

    kwargs[
        "zlm_cone_resistance_before"
    ] = gef_cpt.zero_measurement_cone_before_penetration_test
    kwargs[
        "zlm_cone_resistance_after"
    ] = gef_cpt.zero_measurement_cone_after_penetration_test
    kwargs[
        "zlm_inclination_ew_before"
    ] = gef_cpt.zero_measurement_inclination_ew_before_penetration_test
    kwargs[
        "zlm_inclination_ew_after"
    ] = gef_cpt.zero_measurement_inclination_ew_after_penetration_test
    kwargs[
        "zlm_inclination_ns_before"
    ] = gef_cpt.zero_measurement_inclination_ns_before_penetration_test
    kwargs[
        "zlm_inclination_ns_after"
    ] = gef_cpt.zero_measurement_inclination_ns_after_penetration_test
    kwargs["zlm_inclination_resultant_before"] = None
    kwargs["zlm_inclination_resultant_after"] = None
    kwargs[
        "zlm_local_friction_before"
    ] = gef_cpt.zero_measurement_friction_before_penetration_test
    kwargs[
        "zlm_local_friction_after"
    ] = gef_cpt.zero_measurement_friction_after_penetration_test
    kwargs[
        "zlm_pore_pressure_u1_before"
    ] = gef_cpt.zero_measurement_ppt_u1_before_penetration_test
    kwargs[
        "zlm_pore_pressure_u2_before"
    ] = gef_cpt.zero_measurement_ppt_u2_before_penetration_test
    kwargs[
        "zlm_pore_pressure_u3_before"
    ] = gef_cpt.zero_measurement_ppt_u3_before_penetration_test
    kwargs[
        "zlm_pore_pressure_u1_after"
    ] = gef_cpt.zero_measurement_ppt_u1_after_penetration_test
    kwargs[
        "zlm_pore_pressure_u2_after"
    ] = gef_cpt.zero_measurement_ppt_u2_after_penetration_test
    kwargs[
        "zlm_pore_pressure_u3_after"
    ] = gef_cpt.zero_measurement_ppt_u3_after_penetration_test

    return CPTData(**kwargs)