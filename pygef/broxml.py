from abc import ABC
import xmlschema

from datetime import datetime
import polars as pl


class _BroXml(ABC):
    def __init__(self, path=None, string=None):
        self.path = path
        if string is None:
            with open(path, encoding="utf-8", errors="ignore") as f:
                string = f.read()

        self.s = string

        # todo: Automatically get the schema from the bro website based on the xsi:schemaLocation of the xml file
        # Validate
        schema = xmlschema.XMLSchema("./pygef/resources/isbhr-gt-messages.xsd")
        self._schema_type = "isbhrgt"
        report_name = "BHR_GT_CompleteReport_V1"

        schema.validate(self.s)
        self._isvalid = schema.is_valid(self.s)
        # Decode
        self._decoded = schema.to_dict(self.s)
        self._main_dict = self._decoded[f"{self._schema_type}:sourceDocument"][
            f"{self._schema_type}:{report_name}"
        ]

        # Main attributes
        self.zid = self._main_dict[f"{self._schema_type}:deliveredVerticalPosition"][
            "bhrgtcom:offset"
        ]["$"]
        coords = self._main_dict[f"{self._schema_type}:deliveredLocation"][
            "bhrgtcom:location"
        ]["gml:Point"]["gml:pos"]

        self.x = coords[0]
        self.y = coords[1]
        self.file_date = datetime.strptime(
            self._main_dict[f"{self._schema_type}:boring"]["bhrgtcom:boringStartDate"][
                "brocom:date"
            ],
            "%Y-%m-%d",
        ).date()
        self.height_system = None
        self.type = "bore"
        self.test_id = self._main_dict[f"{self._schema_type}:objectIdAccountableParty"]
        self.nen_version = "NEN-EN-ISO 14688"
        self.df = self._parse_df()

    def _parse_df(self) -> pl.DataFrame:
        depth_top = []
        depth_bottom = []
        soil_name = []
        for i, layer in enumerate(
            self._main_dict[f"{self._schema_type}:boreholeSampleDescription"][
                "bhrgtcom:descriptiveBoreholeLog"
            ][0]["bhrgtcom:layer"]
        ):
            depth_top.append(layer["bhrgtcom:upperBoundary"]["$"])
            depth_bottom.append(layer["bhrgtcom:lowerBoundary"]["$"])
            soil_name.append(
                layer["bhrgtcom:soil"]["bhrgtcom:geotechnicalSoilName"]["$"]
            )

        df = pl.DataFrame(
            {
                "depth_top": depth_top,
                "depth_bottom": depth_bottom,
                "soil_name": soil_name,
            }
        )
        return df


class _BroXmlBore(_BroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)


class _BroXmlCpt(_BroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)

        raise NotImplementedError(
            "The parsing of cpts in xml format is not yet available."
        )


def soil_name_to_percentages(df):

    return df
