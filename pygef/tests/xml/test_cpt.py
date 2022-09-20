from pygef import read_cpt, QualityClass, Location


def test_cpt_attributes(cpt_xml: str) -> None:
    parsed = read_cpt(cpt_xml)
    assert len(parsed) == 1

    cpt = parsed[0]
    assert cpt.bro_id == "CPT000000099543"
    assert cpt.research_report_date == "2019-04-23"
    assert cpt.data.shape == (373, 9)
    assert cpt.quality_class == QualityClass.Class2
    assert cpt.cpt_standard == "ISO22476D1"
    assert cpt.standardized_location == Location(
        srs_name="urn:ogc:def:crs:EPSG::4258", x=52.365336590, y=5.609079550
    )
    assert not cpt.dissipationtest_performed
    assert cpt.predrilled_depth == 0.0
    assert cpt.final_depth == 7.439
    assert cpt.cpt_description == "Hyson"
    assert cpt.cpt_type == "I-CFXY-15/190206"
    assert cpt.cone_surface_area == 1500
    assert cpt.cone_diameter == 44
    assert cpt.cone_surface_quotient == 0.67
    assert cpt.cone_to_friction_sleeve_distance == 100
    assert cpt.cone_to_friction_sleeve_surface_area == 22530
    assert cpt.cone_to_friction_sleeve_surface_quotient == 1.0
    assert cpt.zlm_cone_resistance_before == 0.173
    assert cpt.zlm_cone_resistance_after == 0.109
    assert cpt.zlm_inclination_ew_before == -2
    assert cpt.zlm_inclination_ew_after == -1
    assert cpt.zlm_inclination_ns_before == 0
    assert cpt.zlm_inclination_ns_after == 0
    assert cpt.zlm_inclination_resultant_before == 0
    assert cpt.zlm_inclination_resultant_after == 0
    assert cpt.zlm_local_friction_before == -0.002
    assert cpt.zlm_local_friction_after == -0.002
    assert cpt.zlm_pore_pressure_u1_before is None
    assert cpt.zlm_pore_pressure_u2_before is None
    assert cpt.zlm_pore_pressure_u3_before is None
    assert cpt.zlm_pore_pressure_u1_after is None
    assert cpt.zlm_pore_pressure_u2_after is None
    assert cpt.zlm_pore_pressure_u3_after is None
