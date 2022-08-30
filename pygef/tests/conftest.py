from pytest import fixture
import os

TEST_FILES = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "test_files")
)


@fixture()
def bore_xml() -> str:
    return os.path.join(TEST_FILES, "bore_xml", "bore.xml")


@fixture()
def cpt_xml() -> str:
    return os.path.join(TEST_FILES, "cpt_xml", "example.xml")
