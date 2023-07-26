import os
from io import BytesIO
from typing import Dict

from pytest import fixture

TEST_FILES = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_files"))


@fixture()
def bore_xml_v1() -> str:
    return os.path.join(TEST_FILES, "bore_xml", "bore.xml")


@fixture()
def bore_xml_v2() -> str:
    return os.path.join(TEST_FILES, "bore_xml", "DP14+074_MB_KR.xml")


@fixture()
def cpt_xml() -> str:
    return os.path.join(TEST_FILES, "cpt_xml", "example.xml")


@fixture()
def cpt_gef_1() -> str:
    return os.path.join(TEST_FILES, "cpt_gef", "cpt.gef")


@fixture()
def cpt_gef_1_bytes(cpt_gef_1) -> BytesIO:
    with open(cpt_gef_1, encoding="utf-8", errors="ignore") as f:
        data = BytesIO(f.read().encode("utf-8"))
    return data


@fixture()
def cpt_gef_1_string(cpt_gef_1) -> str:
    with open(cpt_gef_1, encoding="utf-8", errors="ignore") as f:
        string = f.read()
    return string


@fixture()
def cpt_gef_2() -> str:
    return os.path.join(TEST_FILES, "cpt_gef", "cpt2.gef")


@fixture()
def cpt_gef_3() -> str:
    return os.path.join(TEST_FILES, "cpt_gef", "cpt3.gef")


@fixture()
def cpt_gef_4() -> str:
    return os.path.join(TEST_FILES, "cpt_gef", "cpt4.gef")


@fixture()
def cpt_gef_5() -> str:
    return os.path.join(TEST_FILES, "cpt_gef", "cpt5.GEF")


@fixture
def valid_gef_cpt_paths(
    cpt_gef_1, cpt_gef_2, cpt_gef_3, cpt_gef_4, cpt_gef_5
) -> Dict[str, str]:
    return {
        "cpt_gef_1": cpt_gef_1,
        "cpt_gef_2": cpt_gef_2,
        "cpt_gef_3": cpt_gef_3,
        "cpt_gef_4": cpt_gef_4,
        "cpt_gef_5": cpt_gef_5,
    }
