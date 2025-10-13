from datetime import datetime

import pytest
from lxml.etree import XMLSyntaxError

from pygef import read_cpt
from pygef.common import Location, VerticalDatumClass
from pygef.cpt import CPTData


def test_engine(cpt_gef_1) -> None:
    # read test with force incorrect engine
    with pytest.raises(XMLSyntaxError):
        read_cpt(cpt_gef_1, engine="xml")
    # read test with force engine
    gef = read_cpt(cpt_gef_1, engine="gef")
    isinstance(gef, CPTData)
    # read test with auto engine
    gef = read_cpt(cpt_gef_1, engine="auto")
    isinstance(gef, CPTData)


@pytest.mark.parametrize("_type", ["string", "path", "byte"])
def test_gef_to_cpt_data(_type, cpt_gef_1, cpt_gef_1_bytes, cpt_gef_1_string) -> None:
    _format = {
        "string": cpt_gef_1_string,
        "path": cpt_gef_1,
        "byte": cpt_gef_1_bytes,
    }

    cpt_data = read_cpt(_format[_type])

    assert cpt_data.attributes() == {
        "bro_id": None,
        "alias": "CPTU17.8 + 83BITE",
        "cone_diameter": None,
        "cone_surface_area": 1000.0,
        "cone_surface_quotient": 0.8,
        "cone_to_friction_sleeve_distance": 80.0,
        "cone_to_friction_sleeve_surface_area": None,
        "cone_to_friction_sleeve_surface_quotient": 1.0,
        "cpt_description": "",
        "cpt_standard": None,
        "groundwater_level": None,
        "cpt_type": 4.0,
        "data": (999, 12),
        "column_void_mapping": {
            "coneResistance": -999999.0,
            "correctedConeResistance": -999999.0,
            "depth": -999999.0,
            "frictionRatio": -999999.0,
            "inclinationEW": -999999.0,
            "inclinationNS": -999999.0,
            "inclinationResultant": -999999.0,
            "localFriction": -999999.0,
            "penetrationLength": -9999.0,
            "porePressureU2": -999999.0,
        },
        "delivered_vertical_position_datum": VerticalDatumClass("31000"),
        "delivered_vertical_position_offset": -0.09,
        "delivered_vertical_position_reference_point": "unknown",
        "dissipationtest_performed": None,
        "final_depth": 20.0,
        "predrilled_depth": 0.0,
        "quality_class": int(2),
        "research_report_date": datetime(2019, 2, 13).date(),
        "standardized_location": None,
        "delivered_location": Location(
            srs_name="urn:ogc:def:crs:EPSG::28992", x=79578.38, y=424838.97
        ),
        "zlm_cone_resistance_after": -0.245,
        "zlm_cone_resistance_before": -0.257,
        "zlm_inclination_ew_after": None,
        "zlm_inclination_ew_before": None,
        "zlm_inclination_ns_after": None,
        "zlm_inclination_ns_before": None,
        "zlm_inclination_resultant_after": None,
        "zlm_inclination_resultant_before": None,
        "zlm_local_friction_after": -0.016,
        "zlm_local_friction_before": -0.015,
        "zlm_pore_pressure_u1_after": None,
        "zlm_pore_pressure_u1_before": None,
        "zlm_pore_pressure_u2_after": -0.013,
        "zlm_pore_pressure_u2_before": -0.028,
        "zlm_pore_pressure_u3_after": None,
        "zlm_pore_pressure_u3_before": None,
    }
