from pygef import read_cpt


def test_cpt_attributes(cpt_xml: str) -> None:
    parsed = read_cpt(cpt_xml)
    assert len(parsed) == 1

    cpt = parsed[0]
    assert cpt.bro_id == "CPT000000099543"
    assert cpt.research_report_date == "2019-04-23"
    assert cpt.data.shape == (373, 9)
