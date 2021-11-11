import io
import logging
import re
from typing import List

import numpy as np
import polars as pl
from polars import col, lit, when

import pygef.utils as utils

# Try to import the optimized Rust header parsing but if that doesn't succeed
# use the built-in python regex methods
try:
    import gef

    USE_RUST_PARSED_HEADERS = False
except ImportError:
    USE_RUST_PARSED_HEADERS = False

logger = logging.getLogger(__name__)


MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT = {
    1: "penetration_length",
    2: "qc",  # 2
    3: "fs",  # 3
    4: "friction_number",  # 4
    5: "u1",  # 5
    6: "u2",  # 6
    7: "u3",  # 7
    8: "inclination",  # 8
    9: "inclination_ns",  # 9
    10: "inclination_ew",  # 10
    11: "corrected_depth",  # 11
    12: "time",  # 12
    13: "corrected_qc",  # 13
    14: "net_cone_resistance",  # 14
    15: "pore_ratio",  # 15
    16: "cone_resistance_number",  # 16
    17: "weight_per_unit_volume",  # 17
    18: "initial_pore_pressure",  # 18
    19: "total_vertical_soil_pressure",  # 19
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
    99: "classification_zone_robertson_1990",
    # found in:#COMPANYID= Fugro GeoServices B.V., NL005621409B08, 31
    131: "speed",  # found in:COMPANYID= Multiconsult, 09073590, 31
    135: "Temperature_c",  # found in:#COMPANYID= Inpijn-Blokpoel,
    250: "magneto_slope_y",  # found in:COMPANYID= Danny, Tjaden, 31
    251: "magneto_slope_x",
}  # found in:COMPANYID= Danny, Tjaden, 31

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

dict_soil_type_rob = {
    "Peat": 1,
    "Clays - silty clay to clay": 2,
    "Silt mixtures - clayey silt to silty clay": 3,
    "Sand mixtures - silty sand to sandy silt": 4,
    "Sands - clean sand to silty sand": 5,
    "Gravelly sand to dense sand": 6,
}

dict_soil_type_been = {
    "Peat": 1,
    "Clays": 2,
    "Clayey silt to silty clay": 3,
    "Silty sand to sandy silt": 4,
    "Sands: clean sand to silty": 5,
    "Gravelly sands": 6,
}


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

        if USE_RUST_PARSED_HEADERS:
            # Use the Rust optimized header parser
            self._data, self._headers = gef.parse(string)
        else:
            # Use the fallback python regex parser
            end_of_header = utils.parse_end_of_header(string)
            self._headers, self._data = string.split(end_of_header)

        self.zid = utils.parse_zid_as_float(self._headers)
        self.height_system = utils.parse_height_system(self._headers)
        self.x = utils.parse_xid_as_float(self._headers)
        self.y = utils.parse_yid_as_float(self._headers)
        self.file_date = utils.parse_file_date(self._headers)
        self.test_id = utils.parse_test_id(self._headers)
        self.type = utils.parse_gef_type(self._headers)


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
        self.cpt_class = utils.parse_cpt_class(self._headers)
        self.column_void = utils.parse_column_void(self._headers)
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

        column_names = determine_column_names(self._headers)

        self.df = (
            self.parse_data(self._headers, self._data, column_names)
            .lazy()
            .pipe(replace_column_void, self.column_void)
            .pipe(correct_pre_excavated_depth, self.pre_excavated_depth)
            .with_column(correct_depth_with_inclination(column_names))
            .select(
                # Remove None values since they throw an error
                [
                    expr
                    for expr in [
                        pl.all().exclude(["depth", "friction_number"]),
                        col("depth").abs(),
                        calculate_friction_number(column_names),
                        self.calculate_elevation_with_respect_to_nap(
                            self.zid, self.height_system
                        ),
                    ]
                    if expr is not None
                ]
            )
            .collect()
        )

    @staticmethod
    def calculate_elevation_with_respect_to_nap(zid, height_system):
        if zid is not None and height_system == 31000.0:
            return (zid - pl.col("depth")).alias("elevation_with_respect_to_nap")

        return None

    @staticmethod
    def parse_data(headers, data_s, column_names=None):
        separator = utils.find_separator(headers)

        # Remove multiple whitespaces
        # TODO: find a way for polars to handle columns with variable amounts of whitespace
        if separator == " ":
            new_data = re.sub("[ \t]+", " ", data_s.replace("!", ""))
        else:
            # If we have another separator remove all whitespace around it
            new_data = re.sub(
                f"[\t ]*{re.escape(separator)}[\t ]*",
                separator,
                data_s.replace(separator + "!", "").replace("!", ""),
            )

        # Remove whitespace at the beginning and end of lines, and remove the
        # last trailing line
        new_data = "\n".join([line.strip() for line in new_data.splitlines()]).rstrip()

        return pl.read_csv(
            new_data.encode(),
            sep=separator,
            new_columns=column_names,
            has_headers=False,
        )


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

        # This is usually not correct for the boringen
        columns_number = utils.parse_columns_number(self._headers)
        column_separator = utils.parse_column_separator(self._headers)
        record_separator = utils.parse_record_separator(self._headers)
        data_s_rows = self._data.split(record_separator)
        data_rows_soil = self.extract_soil_info(
            data_s_rows, columns_number, column_separator
        )

        self.df = (
            self.parse_data_column_info(
                self._headers, self._data, column_separator, columns_number
            )
            .pipe(self.parse_data_soil_code, data_rows_soil)
            .pipe(self.parse_data_soil_type, data_rows_soil)
            .pipe(self.parse_add_info_as_string, data_rows_soil)
            .pipe(self.parse_soil_quantification, data_rows_soil)
        )

        # Drop the columns if they exist, do nothing if they don't
        for column in [
            "sand_median",
            "gravel_median",
            "lutum_percentage",
            "silt_percentage",
            "sand_percentage",
            "gravel_percentage",
            "organic_matter_percentage",
            "soil_type",
        ]:
            if column in self.df.columns:
                self.df.drop_in_place(column)

    @staticmethod
    def parse_add_info_as_string(df, data_rows_soil):
        df["remarks"] = [
            utils.parse_add_info("".join(row[1::])) for row in data_rows_soil
        ]

        return df

    @staticmethod
    def extract_soil_info(data_s_rows, columns_number, column_separator):
        return list(
            map(
                lambda x: x.split(column_separator)[columns_number:-1], data_s_rows[:-1]
            )
        )

    @staticmethod
    def parse_data_column_info(headers, data_s, sep, columns_number, columns_info=None):
        if columns_info is None:
            col = list(
                map(
                    lambda x: utils.parse_column_info(
                        headers, x, MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE
                    ),
                    range(1, columns_number + 1),
                )
            )
            return pl.read_csv(
                io.StringIO(data_s),
                sep=sep,
                new_columns=col,
                has_headers=False,
                projection=list(range(0, len(col))),
            )
        else:
            return pl.read_csv(
                io.StringIO(data_s),
                sep=sep,
                new_columns=columns_info,
                has_headers=False,
            )

    @staticmethod
    def parse_data_soil_type(df, data_rows_soil):
        df["soil_type"] = list(
            map(lambda x: utils.create_soil_type(x[0]), data_rows_soil)
        )

        return df

    @staticmethod
    def parse_data_soil_code(df, data_rows_soil):
        df["soil_code"] = list(
            map(lambda x: utils.parse_soil_code(x[0]), data_rows_soil)
        )

        return df

    @staticmethod
    def parse_soil_quantification(df, data_rows_soil):
        data = np.array([utils.soil_quantification(x[0]) for x in data_rows_soil])

        # Gravel
        df["gravel_component"] = data[:, 0]
        # Sand
        df["sand_component"] = data[:, 1]
        # Clay
        df["clay_component"] = data[:, 2]
        # Loam
        df["loam_component"] = data[:, 3]
        # Peat
        df["peat_component"] = data[:, 4]
        # Silt
        df["silt_component"] = data[:, 5]

        return df


def replace_column_void(lf: pl.LazyFrame, column_void) -> pl.LazyFrame:
    if column_void is None:
        return lf

    # TODO: what to do with multiple columnvoids?
    if isinstance(column_void, list):
        column_void = column_void[0]

    return (
        # Get all values matching column_void and change them to null
        lf.select(
            pl.when(pl.all() == pl.lit(column_void))
            .then(pl.lit(None))
            .otherwise(pl.all())
            .keep_name()
        )
        # Interpolate all null values
        .select(pl.all().interpolate())
        # Remove the rows with null values
        .drop_nulls()
    )


def correct_pre_excavated_depth(lf: pl.LazyFrame, pre_excavated_depth) -> pl.LazyFrame:
    if pre_excavated_depth is not None and pre_excavated_depth > 0:
        return lf.filter(col("penetration_length") >= pre_excavated_depth)
    return lf


def correct_depth_with_inclination(columns):
    """
    Return the expression needed to correct depth
    """
    if "corrected_depth" in columns:
        return col("corrected_depth").alias("depth")
    elif "inclination" in columns:
        pt = "penetration_length"

        # every different in depth needs to be corrected with the angle
        correction_factor = np.cos(
            np.radians(col("inclination").cast(pl.Float32).fill_null(0))
        )

        corrected_depth = (correction_factor * col(pt).diff()).cumsum()
        return (
            pl.when(corrected_depth.is_null())
            .then(col(pt))
            .otherwise(corrected_depth)
            .alias("depth")
        )
    else:
        return col("penetration_length").alias("depth")


def determine_column_names(headers, columns_number=None, columns_info=None):
    if columns_number is None and columns_info is None:
        columns_number = utils.parse_columns_number(headers)
        if columns_number is not None:
            columns_info = []
            for column_number in range(1, columns_number + 1):
                columns_info.append(
                    utils.parse_column_info(
                        headers, column_number, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT
                    )
                )

    return columns_info


def calculate_friction_number(column_names: List[str]) -> "pl.Expr":
    if "fs" in column_names and "qc" in column_names:
        return (
            col("fs") / when(col("qc") == 0.0).then(None).otherwise(col("qc")) * 100.0
        ).alias("friction_number")
    else:
        return lit(0.0).alias("friction_number")
