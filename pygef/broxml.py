from abc import ABC

import xmlschema
import numpy as np
import os.path

from datetime import datetime
import polars as pl


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
            with open(path, encoding="utf-8", errors="ignore") as f:
                string = f.read()

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

        if (
            self.s.find(
                'isbhrgt:registrationRequest xmlns:isbhrgt="http://www.broservices.nl/xsd/isbhr-gt/1.0"'
            )
            > 0.0
        ):  # version 1.0.
            schema = xmlschema.XMLSchema(
                os.path.join(
                    os.path.dirname(__file__), "resources", "isbhr-gt-messages_v1.xsd"
                )
            )

            self._schema_type = "isbhrgt:"
            self._schema2 = "bhrgtcom"
            self._schema3 = "gml"
            self._schema4 = "brocom"

            self._validate(schema)

            self._parse_attributes()
            self.df = self._parse_df()
        elif (
            self.s.find(
                'ns1:registrationRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            )
            > 0
        ):  # version 2.1
            schema = xmlschema.XMLSchema(
                os.path.join(
                    os.path.dirname(__file__), "resources", "isbhr-gt-messages_v2.1.xsd"
                )
            )
            self._validate(schema)
            self._schema_type = "ns1:"
            self._schema2 = "ns3"
            self._schema3 = "ns2"
            self._schema4 = "ns"

            self._parse_attributes()
            self.df = self._parse_df()
        elif (
            self.s.find(
                'registrationRequest xmlns="http://www.broservices.nl/xsd/isbhr-gt/2.1"'
            )
            > 0
        ):  # version 2.1
            schema = xmlschema.XMLSchema(
                os.path.join(
                    os.path.dirname(__file__), "resources", "isbhr-gt-messages_v2.1.xsd"
                )
            )

            self._validate(schema)
            self._schema_type = ""
            self._schema2 = "bhrgtcom"
            self._schema3 = "gml"
            self._schema4 = "brocom"

            self._parse_attributes()
            self.df = self._parse_df()
        else:
            raise ValueError("This xml schema type is not supported yet.")

    def _validate(self, schema: xmlschema.XMLSchema) -> None:
        """
        Validate xml file with xsd.

        Parameters
        ----------
        schema
            xmlschema.XMLSchema based on xsd file
        """
        schema.validate(self.s)
        self._isvalid = schema.is_valid(self.s)
        self._decoded = schema.to_dict(self.s)

    def _parse_attributes(self) -> None:
        report_name = "BHR_GT_CompleteReport_V1"

        self._main_dict = self._decoded[f"{self._schema_type}sourceDocument"][
            f"{self._schema_type}{report_name}"
        ]

        # Main attributes
        self.zid = self._main_dict[f"{self._schema_type}deliveredVerticalPosition"][
            f"{self._schema2}:offset"
        ]["$"]
        coords = self._main_dict[f"{self._schema_type}deliveredLocation"][
            f"{self._schema2}:location"
        ][f"{self._schema3}:Point"][f"{self._schema3}:pos"]

        self.x = coords[0]
        self.y = coords[1]
        self.file_date = datetime.strptime(
            self._main_dict[f"{self._schema_type}boring"][
                f"{self._schema2}:boringStartDate"
            ][f"{self._schema4}:date"],
            "%Y-%m-%d",
        ).date()
        self.test_id = self._main_dict[f"{self._schema_type}objectIdAccountableParty"]

    def _parse_df(self) -> pl.DataFrame:
        depth_top = []
        depth_bottom = []
        soil_name = []
        for i, layer in enumerate(
            self._main_dict[f"{self._schema_type}boreholeSampleDescription"][
                f"{self._schema2}:descriptiveBoreholeLog"
            ][0][f"{self._schema2}:layer"]
        ):
            depth_top.append(layer[f"{self._schema2}:upperBoundary"]["$"])
            depth_bottom.append(layer[f"{self._schema2}:lowerBoundary"]["$"])
            if f"{self._schema2}:specialMaterial" in layer.keys():
                soil_name.append(layer[f"{self._schema2}:specialMaterial"]["$"])
            elif f"{self._schema2}:soil" in layer.keys():
                soil_name.append(
                    layer[f"{self._schema2}:soil"][
                        f"{self._schema2}:geotechnicalSoilName"
                    ]["$"]
                )
            else:
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
        "kleiigZandMetGrind": [0.5, 0.65, 0.3, 0.0, 0.0, 0.0],
        "puin": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # specialMaterial
        "siltigZand": [0.0, 0.7, 0.0, 0.0, 0.0, 0.3],
        "siltigZandMetGrind": [0.5, 0.65, 0.0, 0.0, 0.0, 0.3],
        "sterkGrindigZand": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
        "sterkGrindigeKlei": [0.3, 0.0, 0.7, 0.0, 0.0, 0.0],
        "sterkZandigGrind": [0.7, 0.3, 0.0, 0.0, 0.0, 0.0],
        "sterkZandigSilt": [0.0, 0.3, 0.0, 0.0, 0.0, 0.7],
        "sterkZandigeKlei": [0.0, 0.3, 0.7, 0.0, 0.0, 0.0],
        "sterkZandigeKleiMetGrind": [0.5, 0.3, 0.65, 0.0, 0.0, 0.0],
        "veen": [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "zand": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "zwakGrindigZand": [0.1, 0.9, 0.0, 0.0, 0.0, 0.0],
        "zwakGrindigeKlei": [0.1, 0.0, 0.9, 0.0, 0.0, 0.0],
        "zwakZandigGrind": [0.9, 0.1, 0.0, 0.0, 0.0, 0.0],
        "zwakZandigVeen": [0.0, 0.1, 0.0, 0.0, 0.9, 0.0],
        "zwakZandigeKlei": [0.0, 0.1, 0.9, 0.0, 0.0, 0.0],
        "zwakZandigeKleiMetGrind": [0.5, 0.1, 0.85, 0.0, 0.0, 0.0],
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
