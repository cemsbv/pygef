import pygef.utils as utils
import pandas as pd
import io
import numpy as np
import pygef.plot_cpt as plot
from pygef import robertson, been_jeffrey
import logging
from pygef.grouping import GroupClassification

COLUMN_NAMES_CPT = ["penetration_length",  # 1
                    "qc",  # 2
                    "fs",  # 3
                    "friction_number",  # 4
                    "u1",  # 5
                    "u2",  # 6
                    "u3",  # 7
                    "inclination",  # 8
                    "inclination_NS",  # 9
                    "inclination_EW",  # 10
                    "corrected_depth",  # 11
                    "time",  # 12
                    "corrected_qc",  # 13
                    "net_cone_resistance",  # 14
                    "pore_ratio",  # 15
                    "cone_resistance_number",  # 16
                    "weight_per_unit_volume",  # 17
                    "initial_pore_pressure",  # 18
                    "total_vertical_soil_pressure",  # 19
                    "effective_vertical_soil_pressure"]  # 20

MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT = {1: "penetration_length",
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
                                       251: "magneto_slope_x"}  # found in:OMPANYID= Danny, Tjaden, 31

COLUMN_NAMES_BORE = ["depth_top",  # 1
                     "depth_bottom",  # 2
                     "lutum_percentage",  # 3
                     "silt_percentage",  # 4
                     "sand_percentage",  # 5
                     "gravel_percentage",  # 6
                     "organic_matter_percentage",  # 7
                     "sand_median",  # 8
                     "gravel_median"]  # 9
MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE = dict(enumerate(COLUMN_NAMES_BORE, 1))

COLUMN_NAMES_BORE_CHILD = ["depth_top",  # 1
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
                           "vertical_strain"]  # 16
MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE_CHILD = dict(enumerate(COLUMN_NAMES_BORE_CHILD, 1))

dict_soil_type_rob = {'Peat': 1,
                      'Clays - silty clay to clay': 2,
                      'Silt mixtures - clayey silt to silty clay': 3,
                      'Sand mixtures - silty sand to sandy silt': 4,
                      'Sands - clean sand to silty sand': 5,
                      'Gravelly sand to dense sand': 6
                      }

dict_soil_type_been = {'Peat': 1,
                       'Clays': 2,
                       'Clayey silt to silty clay': 3,
                       'Silty sand to sandy silt': 4,
                       'Sands: clean sand to silty': 5,
                       'Gravelly sands': 6
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
            with open(path, encoding='utf-8', errors='ignore') as f:
                string = f.read()
        self.s = string

        end_of_header = utils.parse_end_of_header(self.s)
        header_s, data_s = self.s.split(end_of_header)
        self.zid = utils.parse_zid_as_float(header_s)
        self.x = utils.parse_xid_as_float(header_s)
        self.y = utils.parse_yid_as_float(header_s)
        self.file_date = utils.parse_file_date(header_s)

        self.type = utils.parse_gef_type(string)
        if self.type == "cpt":
            parsed = ParseCPT(header_s, data_s, self.zid)
        elif self.type == "bore":
            parsed = ParseBORE(header_s, data_s)
        else:
            raise ValueError("The selected gef file is not a cpt nor a borehole. "
                             "Check the REPORTCODE or the PROCEDURECODE.")

        self.__dict__.update(parsed.__dict__)

    def plot(self, classification=None, water_level_NAP=None, min_thickness=None, p_a=0.1, new=True, show=False,
                 figsize=(12, 30), df_group=None, do_grouping=True):
        if self.type == "cpt":
            return self.plot_cpt(classification, water_level_NAP, min_thickness, p_a, new, show, figsize,
                                 df_group, do_grouping)
        elif self.type == "bore":
            return plot.plot_bore(self.df, figsize=figsize, show=show)
        else:
            raise ValueError("The selected gef file is not a cpt nor a borehole. "
                             "Check the REPORTCODE or the PROCEDURECODE.")

    def plot_cpt(self, classification=None, water_level_NAP=None, min_thickness=None, p_a=None, new=True, show=False,
                 figsize=None, df_group=None, do_grouping=True):

        df = (self.df if classification is None
              else self.classify_soil(classification, water_level_NAP, p_a=p_a, new=new))
        if df_group is None and do_grouping is True:
            df_group = self.group_classification(min_thickness, classification, water_level_NAP, new, p_a)
        return plot.plot_cpt(df, df_group, classification, show=show, figsize=figsize)

    def classify_robertson(self, water_level_NAP, new=True, p_a=0.1):  # True to use the new robertson
        return robertson.classify(self.df, self.zid, water_level_NAP, new,
                                  self.net_surface_area_quotient_of_the_cone_tip,
                                  self.pre_excavated_depth, p_a=p_a)

    def classify_been_jeffrey(self, water_level_NAP):
        return been_jeffrey.classify(self.df, self.zid, water_level_NAP, self.net_surface_area_quotient_of_the_cone_tip,
                                     self.pre_excavated_depth)

    def classify_soil(self, classification, water_level_NAP, p_a=0.1, new=True):

        if classification == 'robertson':
            return self.classify_robertson(water_level_NAP, new, p_a=p_a)
        elif classification == 'been_jeffrey':
            return self.classify_been_jeffrey(water_level_NAP)
        else:
            return logging.error(f'Could not find {classification}. Check the spelling or classification not defined '
                                 f'in the library')

    def group_classification(self, min_thickness, classification, water_level_NAP, new=True, p_a=0.1):
        if classification == 'robertson':
            df = self.classify_robertson(water_level_NAP, new, p_a=p_a)
            return GroupClassification(df, min_thickness).df_group
        elif classification == 'been_jeffrey':
            df = self.classify_been_jeffrey(water_level_NAP)
            return GroupClassification(df, min_thickness).df_group
        else:
            return logging.error(f'Could not find {classification}. Check the spelling or classification not defined '
                                 f'in the library')

    def __str__(self):
        return self.df.__str__()


class ParseCPT:
    def __init__(self, header_s, data_s, zid):
        """
        Parser of the cpt file.

        :param header_s: (str) Header of the file
        :param data_s: (str) Data of the file
        :param zid: (flt) Z attribute.
        """

        self.type = 'cpt'
        self.project_id = utils.parse_project_type(header_s, 'cpt')
        self.column_void = utils.parse_column_void(header_s)
        self.nom_surface_area_cone_tip = utils.parse_measurement_var_as_float(header_s, 1)
        self.nom_surface_area_friction_element = utils.parse_measurement_var_as_float(header_s, 2)
        self.net_surface_area_quotient_of_the_cone_tip = utils.parse_measurement_var_as_float(header_s, 3)
        self.net_surface_area_quotient_of_the_friction_casing = utils.parse_measurement_var_as_float(header_s, 4)
        self.distance_between_cone_and_centre_of_friction_casing = utils.parse_measurement_var_as_float(header_s, 5)
        self.friction_present = utils.parse_measurement_var_as_float(header_s, 6)
        self.ppt_u1_present = utils.parse_measurement_var_as_float(header_s, 7)
        self.ppt_u2_present = utils.parse_measurement_var_as_float(header_s, 8)
        self.ppt_u3_present = utils.parse_measurement_var_as_float(header_s, 9)
        self.inclination_measurement_present = utils.parse_measurement_var_as_float(header_s, 10)
        self.use_of_back_flow_compensator = utils.parse_measurement_var_as_float(header_s, 11)
        self.type_of_cone_penetration_test = utils.parse_measurement_var_as_float(header_s, 12)
        self.pre_excavated_depth = utils.parse_measurement_var_as_float(header_s, 13)
        self.groundwater_level = utils.parse_measurement_var_as_float(header_s, 14)
        self.water_depth_offshore_activities = utils.parse_measurement_var_as_float(header_s, 15)
        self.end_depth_of_penetration_test = utils.parse_measurement_var_as_float(header_s, 16)
        self.stop_criteria = utils.parse_measurement_var_as_float(header_s, 17)
        self.zero_measurement_cone_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 20)
        self.zero_measurement_cone_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 21)
        self.zero_measurement_friction_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 22)
        self.zero_measurement_friction_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 23)
        self.zero_measurement_ppt_u1_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 24)
        self.zero_measurement_ppt_u1_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 25)
        self.zero_measurement_ppt_u2_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 26)
        self.zero_measurement_ppt_u2_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 27)
        self.zero_measurement_ppt_u3_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 28)
        self.zero_measurement_ppt_u3_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 29)
        self.zero_measurement_inclination_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 30)
        self.zero_measurement_inclination_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 31)
        self.zero_measurement_inclination_ns_before_penetration_test = utils.parse_measurement_var_as_float(header_s,
                                                                                                            32)
        self.zero_measurement_inclination_ns_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 33)
        self.zero_measurement_inclination_ew_before_penetration_test = utils.parse_measurement_var_as_float(header_s,
                                                                                                            34)
        self.zero_measurement_inclination_ew_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 35)
        self.mileage = utils.parse_measurement_var_as_float(header_s, 41)

        self.df = (self.parse_data(header_s, data_s)
                   .pipe(self.correct_pre_excavated_depth, self.pre_excavated_depth)
                   .pipe(self.correct_depth_with_inclination)
                   .pipe(lambda df: df.assign(depth=np.abs(df['depth'].values)))
                   .pipe(self.calculate_elevation_respect_to_nap, zid)
                   .pipe(self.replace_column_void, self.column_void)
                   .pipe(self.calculate_friction_number)
                   )

    @staticmethod
    def replace_column_void(df, column_void):
        if column_void is not None:
            return df.replace(column_void, np.nan).interpolate(method='linear')
        return df

    @staticmethod
    def calculate_friction_number(df):
        if 'friction_number' in df.columns:
            return df.assign(Fr=df['friction_number'])
        elif 'fs' in df.columns and 'qc' in df.columns:
            return df.assign(Fr=(df['fs'] / df['qc'] * 100))
        else:
            return df

    @staticmethod
    def calculate_elevation_respect_to_nap(df, zid):
        if zid is not None:
            depth_lst = np.array(df['depth'].tolist())
            lst_zid = np.array([zid] * len(df['depth']))
            return df.assign(elevation_with_respect_to_NAP=(lst_zid - depth_lst))
        return df

    @staticmethod
    def correct_depth_with_inclination(df):
        if 'corrected_depth' in df.columns:
            return df.assign(depth=df['corrected_depth'])
        if 'inclination' in df.columns:
            diff_t_depth = np.diff(df['penetration_length'].values) * np.cos(np.radians(df['inclination'].values[:-1]))
            # corrected depth
            return df.assign(depth=np.concatenate([np.array([df['penetration_length'].iloc[0]]),
                                                   np.cumsum(diff_t_depth)]))
        else:
            return df.assign(depth=df['penetration_length'])

    @staticmethod
    def correct_pre_excavated_depth(df, pre_excavated_depth):
        if pre_excavated_depth is not None and \
                np.any(np.isclose(df['penetration_length'].values - pre_excavated_depth, 0)):
            mask = df['penetration_length'] == pre_excavated_depth
            mask2 = df[mask].reset_index(drop=False)
            i = mask2['index'][0]
            return df[i:].reset_index(drop=True)
        return df

    @staticmethod
    def parse_data(header_s, data_s, columns_number=None, columns_info=None):
        if columns_number is None and columns_info is None:
            columns_number = utils.parse_columns_number(header_s)
            if columns_number is not None:
                columns_info = []
                for column_number in range(1, columns_number + 1):
                    column_info = utils.parse_column_info(header_s, column_number,
                                                          MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT)
                    columns_info.append(column_info)
        new_data = data_s.replace('!', '')
        separator = utils.find_separator(header_s)
        df = pd.read_csv(io.StringIO(new_data), sep=separator, names=columns_info, index_col=False, engine='python')
        return df


class ParseBORE:
    def __init__(self, header_s, data_s):
        """
        Parser of the borehole file.

        :param header_s: (str) Header of the file
        :param data_s: (str) Data of the file
        """
        self.type = 'bore'
        self.project_id = utils.parse_project_type(header_s, 'bore')

        columns_number = utils.parse_columns_number(header_s)
        column_separator = utils.parse_column_separator(header_s)
        record_separator = utils.parse_record_separator(header_s)
        data_s_rows = data_s.split(record_separator)
        data_rows_soil = self.extract_soil_info(data_s_rows, columns_number, column_separator)

        self.df = (self.parse_data_column_info(header_s, data_s, column_separator, columns_number)
                   .pipe(self.parse_data_soil_code, data_rows_soil)
                   .pipe(self.parse_data_soil_type, data_rows_soil)
                   .pipe(self.parse_add_info_as_string, data_rows_soil)
                   ).join(self.data_soil_quantified(data_rows_soil))[
            ['depth_top', 'depth_bottom', 'Soil_code', 'Gravel', 'Sand', 'Clay',
             'Loam', 'Peat', 'Silt']
        ]

        self.df.columns = ['depth_top', 'depth_bottom', 'soil_code', 'G', 'S', 'C', 'L', 'P', 'SI']

    @staticmethod
    def parse_add_info_as_string(df, data_rows_soil):
        return df.assign(additional_info=[''.join(map(utils.parse_add_info, row[1:-1])) for row in data_rows_soil])

    @staticmethod
    def extract_soil_info(data_s_rows, columns_number, column_separator):
        return list(map(lambda x: x.split(column_separator)[columns_number:-1], data_s_rows[:-1]))

    @staticmethod
    def parse_data_column_info(header_s, data_s, sep, columns_number, columns_info=None):
        if columns_info is None:
            col = list(map(lambda x: utils.parse_column_info(header_s, x, MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE),
                           range(1, columns_number + 1)))
            return pd.read_csv(io.StringIO(data_s), sep=sep, names=col, index_col=False,
                               usecols=col)
        else:
            return pd.read_csv(io.StringIO(data_s), sep=sep, names=columns_info, index_col=False,
                               usecols=columns_info)

    @staticmethod
    def parse_data_soil_type(df, data_rows_soil):
        return df.assign(Soil_type=list(map(lambda x: utils.create_soil_type(x[0]), data_rows_soil)))

    @staticmethod
    def parse_data_soil_code(df, data_rows_soil):
        return df.assign(Soil_code=list(map(lambda x: utils.parse_soil_code(x[0]), data_rows_soil)))

    @staticmethod
    def data_soil_quantified(data_rows_soil):
        return pd.DataFrame(list(map(lambda x: utils.soil_quantification(x[0]), data_rows_soil)),
                            columns=['Gravel', 'Sand', 'Clay', 'Loam', 'Peat', 'Silt'])
