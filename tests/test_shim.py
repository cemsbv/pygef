from pygef import read_cpt, QualityClass, Location


def test_gef_to_cpt_data(cpt_gef_1: str) -> None:
    cpt_data = read_cpt(cpt_gef_1)

    assert cpt_data.attributes() == {
        "bro_id": "1801726",
        "cone_diameter": None,
        "cone_surface_area": 1000.0,
        "cone_surface_quotient": 0.8,
        "cone_to_friction_sleeve_distance": 80.0,
        "cone_to_friction_sleeve_surface_area": None,
        "cone_to_friction_sleeve_surface_quotient": 1.0,
        "cpt_description": "",
        "cpt_standard": None,
        "cpt_type": 4.0,
        "data": (999, 12),
        "delivered_vertical_position_datum": 31000.0,
        "delivered_vertical_position_offset": -0.09,
        "delivered_vertical_position_reference_point": "unknown",
        "dissipationtest_performed": None,
        "final_depth": 20.0,
        "predrilled_depth": 0.0,
        "quality_class": QualityClass(2),
        "research_report_date": None,
        "standardized_location": Location(
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