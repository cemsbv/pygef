from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import numpy as np
import polars as pl
from gef_file_to_map import gef_to_map
from polars import lit, when

from pygef import exceptions
from pygef.broxml.mapping import MAPPING_PARAMETERS
from pygef.gef import utils

logger = logging.getLogger(__name__)

MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT = {
    1: "penetration_length",
    2: "qc",
    3: "fs",
    4: "friction_number",
    5: "u1",
    6: "u2",
    7: "u3",
    8: "inclination",
    9: "inclination_ns",
    10: "inclination_ew",
    11: "corrected_depth",
    12: "time",
    13: "corrected_qc",
    14: "net_cone_resistance",
    15: "pore_ratio",
    16: "cone_resistance_number",
    17: "weight_per_unit_volume",
    18: "initial_pore_pressure",
    19: "total_vertical_soil_pressure",
    20: "effective_vertical_soil_pressure",
    21: "inclination_in_x_direction",
    22: "inclination_in_y_direction",
    23: "electric_conductivity",
    31: "magnetic_field_x",
    32: "magnetic_field_y",
    33: "magnetic_field_z",
    34: "total_magnetic_field",
    35: "magnetic_inclination",
    36: "magnetic_declination",
}

COLUMN_NAMES_BORE = [
    "depth_top",  # 1
    "depth_bottom",  # 2
    "lutum_percentage",  # 3
    "silt_percentage",  # 4
    "sand_percentage",  # 5
    "gravel_percentage",  # 6
    "organic_matter_percentage",  # 7
    "sand_median",  # 8
    "gravel_median",
]  # 9
MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE = dict(enumerate(COLUMN_NAMES_BORE, 1))

COLUMN_NAMES_BORE_CHILD = [
    "depth_top",  # 1
    "depth_bottom",  # 2
    "undrained_shear_strength",  # 3
    "vertical_permeability",  # 4
    "horizontal_permeability",  # 5
    "effective_cohesion_at_x%_strain",  # 6
    "friction_angle_at_x%_strain",  # 7
    "water_content",  # 8
    "dry_volumetric_mass",  # 9
    "wet_volumetric_mass",  # 10
    "d_50",  # 11
    "d_60/d_10_uniformity",  # 12
    "d_90/d_10_gradation",  # 13
    "dry_volumetric_weight",  # 14
    "wet_volumetric_weight",  # 15
    "vertical_strain",
]  # 16
MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE_CHILD = dict(enumerate(COLUMN_NAMES_BORE_CHILD, 1))


class _Gef:
    """
    The gef parser is built following the conventional format described in:
    https://publicwiki.deltares.nl/download/attachments/102204318/GEF-CPT.pdf?version=1&modificationDate=1409732008000&api=v2
    """

    def __init__(self, path=None, string=None):
        """
        Base class of gef parser. It switches between the cpt or borehole parser.

        It takes as input either the path to the gef file or the gef file as string.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.

        """
        self.path = path
        self.df = None
        self.net_surface_area_quotient_of_the_cone_tip = None
        self.pre_excavated_depth = None

        if string is None:
            with open(path, encoding="utf-8", errors="ignore") as f:
                string = f.read()

        self.s = string

        # Use the Rust optimized header parser
        self._data, self._headers = gef_to_map(string)

        self.zid = utils.parse_zid_as_float(self._headers)
        self.height_system = utils.parse_height_system(self._headers)
        self.x = utils.parse_xid_as_float(self._headers)
        self.y = utils.parse_yid_as_float(self._headers)
        self.file_date = utils.parse_file_date(self._headers)
        self.test_id = utils.parse_test_id(self._headers)
        self.type = utils.parse_gef_type(self._headers)

    @dataclass
    class ColumnsInfo:
        """
        Dataclass carrying the #COLUMNINFO headers
        All inputs should be sorted on increasing column-number.
        """

        column_numbers: List[int]
        units: List[str]
        descriptions: List[str]
        column_quantities: List[int]
        col_separator: str
        rec_separator: str
        column_voids: Dict[int, float]
        default_void: float = float(-9999)

        def __post_init__(self):
            self.columns_number = len(self.column_numbers)
            self.column_voids = self.fill_default_column_voids()

            self.validate()

        @property
        def description_to_void_mapping(self) -> Dict[str, float]:
            return {
                desc: self.column_voids[num]
                for num, desc in zip(self.column_numbers, self.descriptions)
            }

        def fill_default_column_voids(self) -> Dict[int, float]:
            default_column_voids = {
                num: self.default_void for num in self.column_numbers
            }
            default_column_voids.update(self.column_voids)
            return default_column_voids

        def validate(self):
            if not len(self.column_numbers) == self.column_numbers[-1]:
                raise exceptions.ParseGefError(
                    "One or more #COLUMNINFO headers are missing: We counted "
                    f"{len(self.column_numbers)} #COLUMNINFO headers, but the highest column index "
                    f"is {self.column_numbers[-1]}"
                )

            if not self.column_numbers == list(range(1, self.column_numbers[-1] + 1)):
                raise exceptions.ParseGefError(
                    "One or more #COLUMNINFO headers have duplicates in the .gef file."
                )

    @staticmethod
    def parse_data(
        data_s: str,
        col_separator: str,
        rec_separator: str,
        column_names: List[str],
    ) -> pl.DataFrame:
        """
        Parses all data in the data string, returns a pl.DataFrame

        Parameters
        ----------
        data_s: str
            A string with the measurement data, in Delimiter-separated format.
        col_separator: str
            The character that separates the columns
        rec_separator: str
            The character that separates the records/rows
        column_names: List[str]
            List of column names

        Returns
        -------
        df: pl.DataFrame
            The DataFrame with measurement data
        """

        # Remove all horizontal whitespace characters around the column separator
        new_data = re.sub(
            rf"[^\S\r\n]*{re.escape(col_separator)}[^\S\r\n]*",
            col_separator,
            data_s,
        )

        # Split string by record separator into lines
        # Remove all whitespaces and column separators at the beginning and end of lines
        # Also remove the last trailing line
        regex = rf"[\s{re.escape(col_separator)}]+"
        new_data = "\n".join(
            re.sub(f"{regex}$", "", re.sub(f"^{regex}", "", line))
            for line in new_data.split(rec_separator)
        ).rstrip()

        return pl.read_csv(
            new_data.encode(),
            sep=col_separator,
            new_columns=column_names,
            has_header=False,
            columns=list(range(0, len(column_names))),
        )


class _GefCpt(_Gef):
    def __init__(self, path=None, string=None):
        """
        Parser of the cpt file.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.
        """
        super().__init__(path=path, string=string)
        if not self.type == "cpt":
            raise ValueError(
                "The selected gef file is not a cpt. "
                "Check the REPORTCODE or the PROCEDURECODE."
            )
        self.project_id = utils.parse_project_type(self._headers, "cpt")
        self.cone_id = utils.parse_cone_id(self._headers)

        cpt_class = utils.parse_cpt_class(self._headers)
        self.cpt_class = -1 if cpt_class is None else cpt_class

        self.nom_surface_area_cone_tip = utils.parse_measurement_var_as_float(
            self._headers, 1
        )
        self.nom_surface_area_friction_element = utils.parse_measurement_var_as_float(
            self._headers, 2
        )
        self.net_surface_area_quotient_of_the_cone_tip = (
            utils.parse_measurement_var_as_float(self._headers, 3)
        )
        self.net_surface_area_quotient_of_the_friction_casing = (
            utils.parse_measurement_var_as_float(self._headers, 4)
        )
        self.distance_between_cone_and_centre_of_friction_casing = (
            utils.parse_measurement_var_as_float(self._headers, 5)
        )
        self.friction_present = utils.parse_measurement_var_as_float(self._headers, 6)
        self.ppt_u1_present = utils.parse_measurement_var_as_float(self._headers, 7)
        self.ppt_u2_present = utils.parse_measurement_var_as_float(self._headers, 8)
        self.ppt_u3_present = utils.parse_measurement_var_as_float(self._headers, 9)
        self.inclination_measurement_present = utils.parse_measurement_var_as_float(
            self._headers, 10
        )
        self.use_of_back_flow_compensator = utils.parse_measurement_var_as_float(
            self._headers, 11
        )
        self.type_of_cone_penetration_test = utils.parse_measurement_var_as_float(
            self._headers, 12
        )
        self.pre_excavated_depth = utils.parse_measurement_var_as_float(
            self._headers, 13
        )
        self.groundwater_level = utils.parse_measurement_var_as_float(self._headers, 14)
        self.water_depth_offshore_activities = utils.parse_measurement_var_as_float(
            self._headers, 15
        )
        self.end_depth_of_penetration_test = utils.parse_measurement_var_as_float(
            self._headers, 16
        )
        self.stop_criteria = utils.parse_measurement_var_as_float(self._headers, 17)
        self.zero_measurement_cone_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 20)
        )
        self.zero_measurement_cone_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 21)
        )
        self.zero_measurement_friction_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 22)
        )
        self.zero_measurement_friction_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 23)
        )
        self.zero_measurement_ppt_u1_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 24)
        )
        self.zero_measurement_ppt_u1_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 25)
        )
        self.zero_measurement_ppt_u2_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 26)
        )
        self.zero_measurement_ppt_u2_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 27)
        )
        self.zero_measurement_ppt_u3_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 28)
        )
        self.zero_measurement_ppt_u3_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 29)
        )
        self.zero_measurement_inclination_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 30)
        )
        self.zero_measurement_inclination_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 31)
        )
        self.zero_measurement_inclination_ns_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 32)
        )
        self.zero_measurement_inclination_ns_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 33)
        )
        self.zero_measurement_inclination_ew_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 34)
        )
        self.zero_measurement_inclination_ew_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 35)
        )
        self.mileage = utils.parse_measurement_var_as_float(self._headers, 41)

        self.columns_info = self.ColumnsInfo(
            *parse_all_columns_info(self._headers, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT),
            utils.get_column_separator(self._headers),
            utils.get_record_separator(self._headers),
            utils.parse_column_void(self._headers),
        )

        self.df = (
            self.parse_data(
                self._data,
                self.columns_info.col_separator,
                self.columns_info.rec_separator,
                self.columns_info.descriptions,
            )
            .lazy()
            .pipe(replace_column_void, self.columns_info.description_to_void_mapping)
            # Remove the rows with null values
            .drop_nulls()
            .pipe(correct_pre_excavated_depth, self.pre_excavated_depth)
            .with_columns(
                correct_depth_with_inclination(self.columns_info.descriptions)
            )
            .select(
                # Remove None values since they throw an error
                [
                    expr
                    for expr in [
                        pl.all().exclude(["depth", "friction_number"]),
                        pl.col("depth").abs(),
                        calculate_friction_number(self.columns_info.descriptions),
                        self.calculate_elevation_with_respect_to_nap(
                            self.zid, self.height_system
                        ),
                    ]
                    if expr is not None
                ]
            )
            .collect()
        )

        _mapping = {
            "qc": "coneResistance",
            "friction_number": "frictionRatio",
            "fs": "localFriction",
        }
        for key in _mapping.keys():
            if key not in self.df.columns:
                _mapping.pop(key)
        self.df = self.df.rename(_mapping)

    @staticmethod
    def calculate_elevation_with_respect_to_nap(zid, height_system):
        if zid is not None and height_system == 31000.0:
            return (zid - pl.col("depth")).alias("elevation_with_respect_to_nap")

        return None


class _GefBore(_Gef):
    def __init__(self, path=None, string=None, include_soil_dist: bool = True):
        """
        Parser of the borehole file.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.
        include_soil_dist: bool
            Map the soil distribution to the dataframe
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
            utils.get_column_separator(self._headers),
            utils.get_record_separator(self._headers),
            utils.parse_column_void(self._headers),
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
            .rename(
                {
                    "depth_top": "upper_boundary",
                    "depth_bottom": "lower_boundary",
                }
            )
        )
        if include_soil_dist:
            tbl = MAPPING_PARAMETERS.dist_table()
            self.df = self.df.join(tbl, on="geotechnical_soil_name", how="left")
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
    def parse_data_soil_code(df: pl.DataFrame, data_rows_soil: list[str]):
        # return df.with_columns(pl.Series("soil_code", data_rows_soil).apply(utils.parse_soil_code))
        return df.with_columns(
            pl.Series(
                "soil_code",
                list(map(lambda x: utils.parse_soil_code(x[0]), data_rows_soil)),
            )
        )

    @staticmethod
    def map_soil_code_to_soil_name(df: pl.DataFrame, data_rows_soil: list[str]):
        # return df.with_columns(pl.Series("soil_code", data_rows_soil).apply(utils.parse_soil_code))
        return df.with_columns(
            pl.Series(
                "geotechnical_soil_name",
                list(
                    map(
                        lambda x: utils.parse_soil_name(utils.parse_soil_code(x[0])),
                        data_rows_soil,
                    )
                ),
            )
        )


def replace_column_void(
    lf: pl.LazyFrame, col_name_to_void_mapping: Dict[str, float]
) -> pl.LazyFrame:
    return (
        # Get all values matching column_void and change them to null
        # Interpolate all null values
        lf.select(
            [
                pl.when(pl.col(col) == pl.lit(col_name_to_void_mapping[col]))
                .then(None)
                .otherwise(pl.col(col))
                .interpolate()
                .keep_name()
                for col in lf.columns
            ]
        )
    )


def correct_pre_excavated_depth(lf: pl.LazyFrame, pre_excavated_depth) -> pl.LazyFrame:
    if pre_excavated_depth is not None and pre_excavated_depth > 0:
        return lf.filter(pl.col("penetration_length") >= pre_excavated_depth)
    return lf


def correct_depth_with_inclination(columns: List[str]):
    """
    Return the expression needed to correct depth
    """
    if "corrected_depth" in columns:
        return pl.col("corrected_depth").abs().alias("depth")
    elif "inclination" in columns:
        pt = "penetration_length"

        # every different in depth needs to be corrected with the angle
        correction_factor = np.cos(
            np.radians(pl.col("inclination").cast(pl.Float32).fill_null(0))
        )

        delta_height = pl.col(pt).diff()
        corrected_depth = correction_factor * delta_height

        return (
            # this sets the first as depth
            pl.when(pl.arange(0, corrected_depth.count()) == 0)
            .then(pl.col(pt))
            .otherwise(corrected_depth)
            .cumsum()
            .alias("depth")
        )
    else:
        return pl.col("penetration_length").alias("depth")


def parse_all_columns_info_from_dict(
    headers: dict, quantity_dict: dict
) -> List[Tuple[int, str, str, int]]:
    """
    Function that parses and returns all COLUMNINFO header data from a dictionary.

    :param headers:(str) String of headers.
    :param quantity_dict: (dict) Dictionary that maps quanity numbers to descriptions
    :return: (List[Tuple[int, str, str, int]]) List of Tuples with the COLUMNINFO header values
    """

    columns_info: List[Tuple[int, str, str, int]] = []

    if "COLUMNINFO" in headers:
        # Loop over all headers to find the right number
        for values in headers["COLUMNINFO"]:
            try:
                col_number = int(values[0])
                quantity = int(values[3])
            except ValueError:
                raise exceptions.ParseGefError(
                    "One or more #COLUMNINFO headers do not have integers in the first "
                    "and/or last positions, which is required."
                )

            unit = values[1]
            description = utils.get_description(quantity, values[2], quantity_dict)

            columns_info.append((col_number, unit, description, quantity))

    return columns_info


def parse_all_columns_info_from_str(
    headers: str, quantity_dict: dict
) -> List[Tuple[int, str, str, int]]:
    """
    Function that parses and returns all COLUMNINFO header data from a string.

    :param headers:(dict) Dictionary of headers.
    :param quantity_dict: (dict) Dictionary that maps quanity numbers to descriptions
    :return: (List[Tuple[int, str, str, int]]) List of Tuples with the COLUMNINFO header values
    """

    columns_info: List[Tuple[int, str, str, int]] = []

    # Find all '#COLUMNINFO= **,' strings first
    for match in re.finditer(
        r"#COLUMNINFO\s*=\s*(\d+)\s*,{1}\s*([^,]+)\s*,{1}([^,]+)\s*,{1}\s*(\d+)",
        headers,
    ):
        column_number = utils.cast_string(int, match.group(1))
        column_quantity = utils.cast_string(int, match.group(4))

        custom_description = match.group(3).strip()
        description = utils.get_description(
            column_quantity, custom_description, quantity_dict
        )

        if column_number is not None and column_quantity is not None:
            columns_info.append(
                (
                    column_number,
                    match.group(2).strip(),
                    description,
                    column_quantity,
                )
            )

    return columns_info


def parse_all_columns_info(
    headers: Union[dict, str], quantity_dict: dict
) -> Tuple[List[int], List[str], List[str], List[int]]:
    """
    Function that parses and returns all COLUMNINFO header data from a string or dictionary.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :param quantity_dict: (dict) Dictionary that maps quanity numbers to descriptions
    :return: Tuple with lists of column_numbers, units, descriptions and column_quantities, sorted by column_numbers
    """

    if isinstance(headers, dict):
        columns_info = parse_all_columns_info_from_dict(headers, quantity_dict)

    else:
        columns_info = parse_all_columns_info_from_str(headers, quantity_dict)

    columns_info.sort()

    column_numbers = []
    units = []
    descriptions = []
    column_quantities = []

    for col in columns_info:
        column_numbers.append(col[0])
        units.append(col[1])
        descriptions.append(col[2])
        column_quantities.append(col[3])

    return column_numbers, units, descriptions, column_quantities


def calculate_friction_number(column_names: List[str]) -> "pl.Expr":
    if "fs" in column_names and "qc" in column_names:
        return (
            pl.col("fs")
            / when(pl.col("qc") == 0.0).then(None).otherwise(pl.col("qc"))
            * 100.0
        ).alias("friction_number")
    else:
        return lit(0.0).alias("friction_number")
