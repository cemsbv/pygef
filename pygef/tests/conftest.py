from pytest import fixture
import os

TEST_FILES = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "test_files")
)


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
    return os.path.join(TEST_FILES, "cpt.gef")


@fixture()
def cpt_gef_2() -> str:
    return os.path.join(TEST_FILES, "cpt2.gef")


@fixture()
def cpt_gef_3() -> str:
    return os.path.join(TEST_FILES, "cpt3.gef")


@fixture()
def cpt_gef_4() -> str:
    return os.path.join(TEST_FILES, "cpt4.gef")
