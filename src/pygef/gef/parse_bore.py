from __future__ import annotations

import polars as pl

from pygef.gef import utils
from pygef.gef.gef import _Gef, parse_all_columns_info, replace_column_void
from pygef.gef.mapping import MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE


class _GefBore(_Gef):
    def __init__(self, path=None, string=None):
        """
        Parser of the borehole file.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.
        """
        super().__init__(path=path, string=string)
        if self.type == "bore":
            pass
        elif self.type == "borehole-report":
            raise ValueError(
                "The selected gef file is a GEF-BOREHOLE-Report. Can only parse "
                "GEF-CPT-Report and GEF-BORE-Report. Check the PROCEDURECODE."
            )
        else:
            raise ValueError(
                "The selected gef file is not a borehole. "
                "Check the REPORTCODE or the PROCEDURECODE."
            )

        self.project_id = utils.parse_project_type(self._headers, "bore")
        self.nen_version = "NEN 5104"

        self.data_info = self.ColumnsInfo(
            *parse_all_columns_info(
                self._headers, MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE
            ),
            col_separator=utils.get_column_separator(self._headers),
            rec_separator=utils.get_record_separator(self._headers),
            column_voids=utils.parse_column_void(self._headers),
        )

        data_s_rows = self._data.split(self.data_info.rec_separator)
        data_rows_soil = self.extract_soil_info(
            data_s_rows, self.data_info.columns_number, self.data_info.col_separator
        )

        self.df = (
            self.parse_data(
                self._data,
                self.data_info.col_separator,
                self.data_info.rec_separator,
                self.data_info.descriptions,
            )
            .pipe(replace_column_void, self.data_info.description_to_void_mapping)
            .pipe(self.parse_data_soil_code, data_rows_soil)
            .pipe(self.parse_add_info_as_string, data_rows_soil)
            .pipe(self.map_soil_code_to_soil_name, data_rows_soil)
        )

        # Remove the rows with null values
        self.df.drop_nulls()

    @staticmethod
    def parse_add_info_as_string(
        df: pl.DataFrame, data_rows_soil: list[list[str]]
    ) -> pl.DataFrame:
        return df.with_columns(
            pl.Series(
                "remarks",
                [utils.parse_add_info("".join(row[1::])) for row in data_rows_soil],
            )
        )

    @staticmethod
    def extract_soil_info(data_s_rows, columns_number, column_separator):
        return list(
            map(
                lambda x: x.split(column_separator)[columns_number:-1], data_s_rows[:-1]
            )
        )

    @staticmethod
    def parse_data_soil_code(df: pl.DataFrame, data_rows_soil: list[list[str]]):
        # return df.with_columns(pl.Series("soil_code", data_rows_soil).apply(utils.parse_soil_code))
        return df.with_columns(
            pl.Series(
                "geotechnicalSoilCode",
                list(map(lambda x: utils.parse_soil_code(x[0]), data_rows_soil)),
            )
        )

    @staticmethod
    def map_soil_code_to_soil_name(df: pl.DataFrame, data_rows_soil: list[str]):
        # return df.with_columns(pl.Series("soil_code", data_rows_soil).apply(utils.parse_soil_code))
        return df.with_columns(
            pl.Series(
                "geotechnicalSoilName",
                list(
                    map(
                        lambda x: utils.parse_soil_name(utils.parse_soil_code(x[0])),
                        data_rows_soil,
                    )
                ),
            )
        )
