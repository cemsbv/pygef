from pygef import read_cpt


def test_gef_to_cpt_data(cpt_gef_1: str) -> None:
    cpt_data = read_cpt(cpt_gef_1)
    print(cpt_data)
    # TODO! add height NAP
    # TODO! convert GEF types to correct CptData type

    assert False
