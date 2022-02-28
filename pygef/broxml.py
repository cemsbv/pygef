from abc import ABC
from datetime import datetime

import numpy as np
import polars as pl
from lxml import etree

NS_MAP_VALUES = [
    "http://www.broservices.nl/xsd/brocommon/",
    "http://www.broservices.nl/xsd/isbhr-gt/",
    "http://www.opengis.net/gml/",
    "http://www.broservices.nl/xsd/bhrgtcommon/",
]


class _BroXml(ABC):
    def __init__(self, path: str = None, string: str = None):
        """
        Parser of xml files.

        Parameters
        ----------
        path
            Path to the xml file
        string
            Xml file as string
        """
        assert (
            any([path, string]) is not None
        ), "One of [path, string] should be not none."
        self.path = path
        if string is None and path is not None:
            with open(path, "rb") as f:
                self.s_bin = f.read()
            with open(path, encoding="utf-8", errors="ignore") as f:
                string = f.read()
        elif string is not None:
            self.s_bin = string.encode("ascii")

        self.s = string
        # Initialize attributes
        self.zid = None
        self.x = None
        self.y = None
        self.test_id = None
        self.height_system = None


class _BroXmlBore(_BroXml):
    """
    Parser of boreholes xml files.

    Parameters
    ----------
    path
        Path to the xml file
    string
        Xml file as string
    """

    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)
        self.nen_version = "NEN-EN-ISO 14688"
        self.type = "bore"
        self._root = etree.fromstring(self.s_bin)
        self._ns_map_keys = list(self._root.nsmap.keys())

        # find versions
        self._ns_map_values = []
        for pos in NS_MAP_VALUES:
            for val in list(self._root.nsmap.values()):
                if pos in val:
                    self._ns_map_values.append(val)
                    break

        self._parse_attributes()

        self.df = self._parse_df()

    def _parse_attributes(self) -> None:
        self.test_id = list(
            self._root.iter(
                "{" + self._ns_map_values[1] + "}" + "objectIdAccountableParty"
            )
        )[0].text
        self.zid = float(
            list(self._root.iter("{" + self._ns_map_values[3] + "}" + "offset"))[0].text
        )
        self.file_date = datetime.strptime(
            list(
                list(
                    self._root.iter("{" + self._ns_map_values[3] + "}boringStartDate")
                )[0].iter("{" + self._ns_map_values[0] + "}" + "date")
            )[0].text,
            "%Y-%m-%d",
        ).date()

        coords = list(self._root.iter("{" + self._ns_map_values[2] + "}pos"))[
            0
        ].text.split()
        self.x = float(coords[0])
        self.y = float(coords[1])

    def _parse_df(self) -> pl.DataFrame:
        depth_top = []
        depth_bottom = []
        soil_name = []
        for layer in self._root.iter("{" + self._ns_map_values[3] + "}layer"):
            depth_top.append(
                float(
                    list(layer.iter("{" + self._ns_map_values[3] + "}upperBoundary"))[
                        0
                    ].text
                )
            )
            depth_bottom.append(
                float(
                    list(layer.iter("{" + self._ns_map_values[3] + "}lowerBoundary"))[
                        0
                    ].text
                )
            )
            for loc in layer:
                if loc.tag == "{" + self._ns_map_values[3] + "}soil":
                    s = list(
                        loc.iter("{" + self._ns_map_values[3] + "}geotechnicalSoilName")
                    )[0].text
                    soil_name.append(s)
                elif loc.tag == "{" + self._ns_map_values[3] + "}specialMaterial":
                    soil_name.append(loc.text)
            if len(soil_name) < len(depth_bottom):
                soil_name.append("not classified")

        df = pl.DataFrame(
            {
                "depth_top": depth_top,
                "depth_bottom": depth_bottom,
                "soil_name": soil_name,
            }
        )
        df = soil_name_to_percentages(df)
        return df


class _BroXmlCpt(_BroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)

        raise NotImplementedError(
            "The parsing of cpts in xml format is not yet available."
        )


def soil_name_to_percentages(df):
    """
    Adds the columns
    ["gravel_component", "sand_component", "clay_component", "loam_component", "peat_component", "silt_component"]
    to the Dataframe
    Parameters
    ----------
    df
        DataFrame containing 'soil_name' column
    Returns
    -------

    """
    soil_names_dict = {
        "betonOngebroken": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # specialMaterial
        "keitjes": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "klei": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        "kleiigVeen": [0.0, 0.0, 0.3, 0.0, 0.7, 0.0],
        "kleiigZand": [0.0, 0.7, 0.3, 0.0, 0.0, 0.0],
        "kleiigZandMetGrind": [0.05, 0.65, 0.3, 0.0, 0.0, 0.0],
        "puin": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # specialMaterial
        "siltigZand": [0.0, 0.7, 0.0, 0.0, 0.0, 0.3],
        "siltigZandMetGrind": [0.05, 0.65, 0.0, 0.0, 0.0, 0.3],
        "sterkGrindigZand": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
        "sterkGrindigeKlei": [0.3, 0.0, 0.7, 0.0, 0.0, 0.0],
        "sterkZandigGrind": [0.7, 0.3, 0.0, 0.0, 0.0, 0.0],
        "sterkZandigSilt": [0.0, 0.3, 0.0, 0.0, 0.0, 0.7],
        "sterkZandigeKlei": [0.0, 0.3, 0.7, 0.0, 0.0, 0.0],
        "sterkZandigeKleiMetGrind": [0.05, 0.3, 0.65, 0.0, 0.0, 0.0],
        "veen": [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "zand": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "zwakGrindigZand": [0.1, 0.9, 0.0, 0.0, 0.0, 0.0],
        "zwakGrindigeKlei": [0.1, 0.0, 0.9, 0.0, 0.0, 0.0],
        "zwakZandigGrind": [0.9, 0.1, 0.0, 0.0, 0.0, 0.0],
        "zwakZandigVeen": [0.0, 0.1, 0.0, 0.0, 0.9, 0.0],
        "zwakZandigeKlei": [0.0, 0.1, 0.9, 0.0, 0.0, 0.0],
        "zwakZandigeKleiMetGrind": [0.05, 0.1, 0.85, 0.0, 0.0, 0.0],
    }

    array_ = np.array(
        [
            soil_names_dict[soil_name]
            if soil_name in soil_names_dict.keys()
            else [0, 0, 0, 0, 0, 0]
            for soil_name in df["soil_name"]
        ]
    )
    df_soils = pl.DataFrame(
        array_,
        columns=[
            "gravel_component",
            "sand_component",
            "clay_component",
            "loam_component",
            "peat_component",
            "silt_component",
        ],
    )
    df = df.hstack(df_soils)
    return df
