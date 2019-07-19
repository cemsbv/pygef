import pygef.utils as utils
import pandas as pd
import io
import numpy as np
import pygef.plot_utils as plot
from pygef import robertson, been_jefferies
import logging
from pygef.grouping import GroupClassification


MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT = {
    1: "penetration_length",
    2: "qc",  # 2
    3: "fs",  # 3
    4: "friction_number",  # 4
    5: "u1",  # 5
    6: "u2",  # 6
    7: "u3",  # 7
    8: "inclination",  # 8
    9: "inclination_NS",  # 9
    10: "inclination_EW",  # 10
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
    21: "Inclination_in_X_direction",
    22: "Inclination_in_Y_direction",
    23: "Electric_conductivity",
    31: "magnetic_field_x",
    32: "magnetic_field_y",
    33: "magnetic_field_z",
    34: "total_magnetic_field",
    35: "magnetic_inclination",
    36: "magnetic_declination",
    99: "Classification_zone_Robertson_1990",
    # found in:#COMPANYID= Fugro GeoServices B.V., NL005621409B08, 31
    131: "speed",  # found in:COMPANYID= Multiconsult, 09073590, 31
    135: "Temperature_C",  # found in:#COMPANYID= Inpijn-Blokpoel,
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


class ParseGEF:
    def __init__(self, path=None, string=None):
        """
        Base class of gef parser. It switches between the cpt or borehole parser.

        :param path:(str) Path of the .gef file to parse.
        :param string:(str) String to parse.
        """
        self.path = path
        self.df = None
        self.net_surface_area_quotient_of_the_cone_tip = None
        self.pre_excavated_depth = None

        if string is None:
            with open(path, encoding="utf-8", errors="ignore") as f:
                string = f.read()
        self.s = string

        end_of_header = utils.parse_end_of_header(self.s)
        header_s, data_s = self.s.split(end_of_header)
        self.zid = utils.parse_zid_as_float(header_s)
        self.x = utils.parse_xid_as_float(header_s)
        self.y = utils.parse_yid_as_float(header_s)
        self.file_date = utils.parse_file_date(header_s)
        self.test_id = utils.parse_test_id(header_s)

        self.type = utils.parse_gef_type(string)
        if self.type == "cpt":
            parsed = ParseCPT(header_s, data_s, self.zid)
        elif self.type == "bore":
            parsed = ParseBORE(header_s, data_s)
        elif self.type == "borehole-report":
            raise ValueError(
                "Selected gef file is a GEF-BOREHOLE-Report. Can only parse "
                "GEF-CPT-Report and GEF-BORE-Report. Check the PROCEDURECODE."
            )
        else:
            raise ValueError(
                "The selected gef file is not a cpt nor a borehole. "
                "Check the REPORTCODE or the PROCEDURECODE."
            )

        self.__dict__.update(parsed.__dict__)
        self.df = self.df.dropna().reset_index(drop=True)

    def plot(
        self,
        classification=None,
        water_level_NAP=None,
        water_level_wrt_depth=None,
        min_thickness=None,
        p_a=0.1,
        new=True,
        show=False,
        figsize=(11, 8),
        df_group=None,
        do_grouping=False,
        grid_step_x=None,
        dpi=100,
        colors=None,
        z_NAP=False,
    ):
        """
        Plot cpt and return matplotlib figure.

        :param classification: (str) Specify this to classify the cpt, possible choice : "robertson", "been_jefferies".
        :param water_level_NAP: (float)
        :param water_level_wrt_depth: (float)
        :param min_thickness: (float) Minimum accepted thickness for grouping.
        :param p_a: (float) Atmospheric pressure at ground level in MPa.
        :param new: (bool) Old(1990) or New(2016) implementation of Robertson.
        :param show: (bool) Set to True to show the plot.
        :param figsize: (tpl) Figure size (x, y).
        :param df_group: (DataFrame) Specify your own DataFrame if you don't agree with the automatic one.
        :param do_grouping: (bool) Plot the grouping if True.
        :param grid_step_x: (int) Grid step of x-axes qc.
        :param dpi: (int) Matplotlib dpi settings.
        :param colors: (dict) Dictionary with soil type and related color, use this to plot your own classification.
        :param z_NAP: (bool) True to plot the z-axis with respect to NAP. Default: False.
        :return: matplotlib Figure.
        """
        if self.type == "cpt":
            if classification is None:
                df = self.df
            else:
                df = self.classify(
                    classification=classification,
                    water_level_NAP=water_level_NAP,
                    water_level_wrt_depth=water_level_wrt_depth,
                    p_a=p_a,
                    new=new,
                )

                if df_group is None and do_grouping is True:
                    df_group = self.classify(
                        classification=classification,
                        water_level_NAP=water_level_NAP,
                        water_level_wrt_depth=water_level_wrt_depth,
                        p_a=p_a,
                        new=new,
                        do_grouping=True,
                        min_thickness=min_thickness,
                    )

            return plot.plot_cpt(
                df,
                df_group,
                classification,
                show=show,
                figsize=figsize,
                grid_step_x=grid_step_x,
                colors=colors,
                dpi=dpi,
                z_NAP=z_NAP,
            )

        elif self.type == "bore":
            return plot.plot_bore(self.df, figsize=figsize, show=show, dpi=dpi)

        else:
            raise ValueError(
                "The selected gef file is not a cpt nor a borehole. "
                "Check the REPORTCODE or the PROCEDURECODE."
            )

    def classify(
        self,
        classification,
        water_level_NAP=None,
        water_level_wrt_depth=None,
        p_a=0.1,
        new=True,
        do_grouping=False,
        min_thickness=None,
    ):
        """
        Classify function, classify gef files and return a dataframe with the classified gef.

        :param classification: (str) Specify the classification, possible choice : "robertson", "been_jefferies".
        :param water_level_NAP:(float)
        :param water_level_wrt_depth: (float)
        :param p_a: (float) Atmospheric pressure at ground level in MPa.
        :param new: (bool) Old(1990) or New(2016) implementation of Robertson.
        :param do_grouping: (bool) Do grouping if True.
        :param min_thickness: (float) Minimum accepted thickness for layers.
        :return: (DataFrame) DataFrame with classification.
        """
        water_level_and_zid_NAP = dict(water_level_NAP=water_level_NAP, zid=self.zid)

        if water_level_NAP is None and water_level_wrt_depth is None:
            water_level_wrt_depth = -1
            logging.warn(
                f"You did not input the water level, a default value of -1 m respect to the ground is used."
                f" Change it using the kwagr water_level_NAP or water_level_wrt_depth."
            )
        if min_thickness is None:
            min_thickness = 0.2
            logging.warn(
                f"You did not input the accepted minimum thickness, a default value of 0.2 m is used."
                f" Change it using th kwarg min_thickness"
            )

        if classification == "robertson":
            df = robertson.classify(
                self.df,
                water_level_and_zid_NAP=water_level_and_zid_NAP,
                water_level_wrt_depth=water_level_wrt_depth,
                new=new,
                area_quotient_cone_tip=self.net_surface_area_quotient_of_the_cone_tip,
                pre_excavated_depth=self.pre_excavated_depth,
                p_a=p_a,
            )
            if do_grouping:
                return GroupClassification(df, min_thickness).df_group
            return df

        elif classification == "been_jefferies":
            df = been_jefferies.classify(
                self.df,
                water_level_and_zid_NAP=water_level_and_zid_NAP,
                water_level_wrt_depth=water_level_wrt_depth,
                area_quotient_cone_tip=self.net_surface_area_quotient_of_the_cone_tip,
                pre_excavated_depth=self.pre_excavated_depth,
            )
            if do_grouping:
                return GroupClassification(df, min_thickness).df_group
            return df
        else:
            return logging.error(
                f"Could not find {classification}. Check the spelling or classification not defined "
                f"in the library"
            )

    def __str__(self):
        return (
            "test id: {} \n"
            "type: {} \n"
            "(x,y): ({:.2f},{:.2f}) \n"
            "First rows of dataframe: \n {}".format(
                self.test_id, self.type, self.x, self.y, self.df.head(n=2)
            )
        )


class ParseCPT:
    def __init__(self, header_s, data_s, zid):
        """
        Parser of the cpt file.

        :param header_s: (str) Header of the file
        :param data_s: (str) Data of the file
        :param zid: (flt) Z attribute.
        """

        self.type = "cpt"
        self.project_id = utils.parse_project_type(header_s, "cpt")
        self.column_void = utils.parse_column_void(header_s)
        self.nom_surface_area_cone_tip = utils.parse_measurement_var_as_float(
            header_s, 1
        )
        self.nom_surface_area_friction_element = utils.parse_measurement_var_as_float(
            header_s, 2
        )
        self.net_surface_area_quotient_of_the_cone_tip = utils.parse_measurement_var_as_float(
            header_s, 3
        )
        self.net_surface_area_quotient_of_the_friction_casing = utils.parse_measurement_var_as_float(
            header_s, 4
        )
        self.distance_between_cone_and_centre_of_friction_casing = utils.parse_measurement_var_as_float(
            header_s, 5
        )
        self.friction_present = utils.parse_measurement_var_as_float(header_s, 6)
        self.ppt_u1_present = utils.parse_measurement_var_as_float(header_s, 7)
        self.ppt_u2_present = utils.parse_measurement_var_as_float(header_s, 8)
        self.ppt_u3_present = utils.parse_measurement_var_as_float(header_s, 9)
        self.inclination_measurement_present = utils.parse_measurement_var_as_float(
            header_s, 10
        )
        self.use_of_back_flow_compensator = utils.parse_measurement_var_as_float(
            header_s, 11
        )
        self.type_of_cone_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 12
        )
        self.pre_excavated_depth = utils.parse_measurement_var_as_float(header_s, 13)
        self.groundwater_level = utils.parse_measurement_var_as_float(header_s, 14)
        self.water_depth_offshore_activities = utils.parse_measurement_var_as_float(
            header_s, 15
        )
        self.end_depth_of_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 16
        )
        self.stop_criteria = utils.parse_measurement_var_as_float(header_s, 17)
        self.zero_measurement_cone_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 20
        )
        self.zero_measurement_cone_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 21
        )
        self.zero_measurement_friction_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 22
        )
        self.zero_measurement_friction_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 23
        )
        self.zero_measurement_ppt_u1_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 24
        )
        self.zero_measurement_ppt_u1_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 25
        )
        self.zero_measurement_ppt_u2_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 26
        )
        self.zero_measurement_ppt_u2_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 27
        )
        self.zero_measurement_ppt_u3_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 28
        )
        self.zero_measurement_ppt_u3_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 29
        )
        self.zero_measurement_inclination_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 30
        )
        self.zero_measurement_inclination_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 31
        )
        self.zero_measurement_inclination_ns_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 32
        )
        self.zero_measurement_inclination_ns_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 33
        )
        self.zero_measurement_inclination_ew_before_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 34
        )
        self.zero_measurement_inclination_ew_after_penetration_test = utils.parse_measurement_var_as_float(
            header_s, 35
        )
        self.mileage = utils.parse_measurement_var_as_float(header_s, 41)

        self.df = (
            self.parse_data(header_s, data_s)
            .pipe(self.correct_pre_excavated_depth, self.pre_excavated_depth)
            .pipe(self.correct_depth_with_inclination)
            .pipe(lambda df: df.assign(depth=np.abs(df["depth"].values)))
            .pipe(self.calculate_elevation_with_respect_to_nap, zid)
            .pipe(self.replace_column_void, self.column_void)
            .pipe(self.calculate_friction_number)
        )

    @staticmethod
    def replace_column_void(df, column_void):
        if column_void is not None:
            return df.replace(column_void, np.nan).interpolate(method="linear")
        return df

    @staticmethod
    def calculate_friction_number(df):
        if "fs" in df.columns and "qc" in df.columns:
            df = df.assign(friction_number=(df["fs"].values / df["qc"].values * 100))
        if "friction_number" not in df.columns:
            df = df.assign(friction_number=(np.zeros(df.shape[0])))
        return df

    @staticmethod
    def calculate_elevation_with_respect_to_nap(df, zid):
        if zid is not None:
            df = df.assign(
                elevation_with_respect_to_NAP=np.subtract(zid, df["depth"].values)
            )
        return df

    @staticmethod
    def correct_depth_with_inclination(df):
        if "corrected_depth" in df.columns:
            return df.rename(columns={"corrected_depth": "depth"})
        if "inclination" in df.columns:
            diff_t_depth = np.diff(df["penetration_length"].values) * np.cos(
                np.radians(df["inclination"].values[:-1])
            )
            # corrected depth
            return df.assign(
                depth=np.concatenate(
                    [
                        np.array([df["penetration_length"].iloc[0]]),
                        np.cumsum(diff_t_depth),
                    ]
                )
            )
        return df.assign(depth=df["penetration_length"])

    @staticmethod
    def correct_pre_excavated_depth(df, pre_excavated_depth):
        if pre_excavated_depth is not None and np.any(
            np.isclose(df["penetration_length"].values - pre_excavated_depth, 0)
        ):
            mask = df["penetration_length"] == pre_excavated_depth
            start_idx = df[mask].reset_index(drop=False)["index"][0]
            return df[start_idx:].reset_index(drop=True)
        return df

    @staticmethod
    def parse_data(header_s, data_s, columns_number=None, columns_info=None):
        if columns_number is None and columns_info is None:
            columns_number = utils.parse_columns_number(header_s)
            if columns_number is not None:
                columns_info = []
                for column_number in range(1, columns_number + 1):
                    column_info = utils.parse_column_info(
                        header_s, column_number, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT
                    )
                    columns_info.append(column_info)
        new_data = data_s.replace("!", "")
        separator = utils.find_separator(header_s)
        return pd.read_csv(
            io.StringIO(new_data),
            sep=separator,
            names=columns_info,
            index_col=False,
            engine="python",
        )


class ParseBORE:
    def __init__(self, header_s, data_s):
        """
        Parser of the borehole file.

        :param header_s: (str) Header of the file
        :param data_s: (str) Data of the file
        """
        self.type = "bore"
        self.project_id = utils.parse_project_type(header_s, "bore")

        # This is usually not correct for the boringen
        columns_number = utils.parse_columns_number(header_s)
        column_separator = utils.parse_column_separator(header_s)
        record_separator = utils.parse_record_separator(header_s)
        data_s_rows = data_s.split(record_separator)
        data_rows_soil = self.extract_soil_info(
            data_s_rows, columns_number, column_separator
        )

        self.df = (
            self.parse_data_column_info(
                header_s, data_s, column_separator, columns_number
            )
            .pipe(self.parse_data_soil_code, data_rows_soil)
            .pipe(self.parse_data_soil_type, data_rows_soil)
            .pipe(self.parse_add_info_as_string, data_rows_soil)
        ).join(self.data_soil_quantified(data_rows_soil))[
            [
                "depth_top",
                "depth_bottom",
                "Soil_code",
                "Gravel",
                "Sand",
                "Clay",
                "Loam",
                "Peat",
                "Silt",
                "remarks",
            ]
        ]
        self.df.columns = [
            "depth_top",
            "depth_bottom",
            "soil_code",
            "G",
            "S",
            "C",
            "L",
            "P",
            "SI",
            "Remarks",
        ]

    @staticmethod
    def parse_add_info_as_string(df, data_rows_soil):
        return df.assign(
            remarks=[utils.parse_add_info("".join(row[1::])) for row in data_rows_soil]
        )

    @staticmethod
    def extract_soil_info(data_s_rows, columns_number, column_separator):
        return list(
            map(
                lambda x: x.split(column_separator)[columns_number:-1], data_s_rows[:-1]
            )
        )

    @staticmethod
    def parse_data_column_info(
        header_s, data_s, sep, columns_number, columns_info=None
    ):
        if columns_info is None:
            col = list(
                map(
                    lambda x: utils.parse_column_info(
                        header_s, x, MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE
                    ),
                    range(1, columns_number + 1),
                )
            )
            return pd.read_csv(
                io.StringIO(data_s), sep=sep, names=col, index_col=False, usecols=col
            )
        else:
            return pd.read_csv(
                io.StringIO(data_s),
                sep=sep,
                names=columns_info,
                index_col=False,
                usecols=columns_info,
            )

    @staticmethod
    def parse_data_soil_type(df, data_rows_soil):
        return df.assign(
            Soil_type=list(map(lambda x: utils.create_soil_type(x[0]), data_rows_soil))
        )

    @staticmethod
    def parse_data_soil_code(df, data_rows_soil):
        return df.assign(
            Soil_code=list(map(lambda x: utils.parse_soil_code(x[0]), data_rows_soil))
        )

    @staticmethod
    def data_soil_quantified(data_rows_soil):
        return pd.DataFrame(
            list(map(lambda x: utils.soil_quantification(x[0]), data_rows_soil)),
            columns=["Gravel", "Sand", "Clay", "Loam", "Peat", "Silt"],
        )
