import re
import pygef.utils as utils
import pandas as pd
import io
import csv

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

MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT = dict(enumerate(COLUMN_NAMES_CPT, 1))

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


class ParseSon:
    def __init__(self, path=None, string=None):
        self.path = path
        self.s = string
        self.z0 = None  # ground level
        self.x = None
        self.y = None
        self.type = None
        self.end_depth_of_penetration_test = None
        self.project_id = None

        # List of all the possible measurement variables

        if self.s is None:
            with open(path, encoding='utf-8', errors='ignore') as f:
                self.s = f.read()


class ParseGEF:
    def __init__(self, path=None, string=None):
        """
        Base class of gef parser. Is inherited for both CPT and Borehole gef files.
        :param path:
        :param string:
        """
        self.path = path
        self.s = string
        self.z0 = None  # ground level
        self.x = None
        self.y = None
        self.type = None
        self.end_depth_of_penetration_test = None
        self.project_id = None

        # List of all the possible measurement variables

        if self.s is None:
            with open(path, encoding='utf-8', errors='ignore') as f:
                self.s = f.read()

#        self.type = utils.parse_gef_type(self.s)
#        if self.type == "cpt":
#            obj = ParseCPT()
#        elif self.type == "bore":
#            obj = ParseBORE()
#        else:
#            print("The selected gef file is not a cpt nor a borehole. Check the REPORTCODE or the PROCEDURECODE.")


class ParseCPT:
    def __init__(self, path=None, string=None):
        """

        :param path:
        :param string:
        """
        self.path = path
        self.zid = None  # ground level
        self.x = None
        self.y = None
        self.type = None
        self.file_date = None
        self.project_id = None
        self.s = string

        # List of all the possible measurement variables
        self.nom_surface_area_cone_tip = None
        self.nom_surface_area_friction_element = None
        self.net_surface_area_quotient_of_the_cone_tip = None
        self.net_surface_area_quotient_of_the_friction_casing = None
        self.distance_between_cone_and_centre_of_friction_casing = None
        self.friction_present = None
        self.ppt_u1_present = None
        self.ppt_u2_present = None
        self.ppt_u3_present = None
        self.inclination_measurement_present = None
        self.use_of_back_flow_compensator = None
        self.type_of_cone_penetration_test = None
        self.pre_excavated_depth = None
        self.groundwater_level = None
        self.water_depth_offshore_activities = None
        self.end_depth_of_penetration_test = None
        self.stop_criteria = None
        self.zero_measurement_cone_before_penetration_test = None
        self.zero_measurement_cone_after_penetration_test = None
        self.zero_measurement_friction_before_penetration_test = None
        self.zero_measurement_friction_after_penetration_test = None
        self.zero_measurement_ppt_u1_before_penetration_test = None
        self.zero_measurement_ppt_u2_before_penetration_test = None
        self.zero_measurement_ppt_u3_before_penetration_test = None
        self.zero_measurement_ppt_u1_after_penetration_test = None
        self.zero_measurement_ppt_u2_after_penetration_test = None
        self.zero_measurement_ppt_u3_after_penetration_test = None
        self.zero_measurement_inclination_before_penetration_test = None
        self.zero_measurement_inclination_after_penetration_test = None
        self.zero_measurement_cone_after_penetration_test = None
        self.zero_measurement_inclination_ns_before_penetration_test = None
        self.zero_measurement_inclination_ns_after_penetration_test = None
        self.zero_measurement_inclination_ew_before_penetration_test = None
        self.zero_measurement_inclination_ew_after_penetration_test = None
        self.mileage = None

        if self.s is None:
            with open(path, encoding='utf-8', errors='ignore') as f:
                self.s = f.read()

        end_of_header = utils.parse_end_of_header(self.s)
        header_s, data_s = self.s.split(end_of_header)

        self.file_date = utils.parse_file_date(header_s)
        self.project_id = utils.parse_project_type(header_s, self.type)
        self.zid = utils.parse_zid_as_float(header_s)
        self.type = utils.parse_gef_type(header_s)
        self.x = utils.parse_xid_as_float(header_s)
        self.y = utils.parse_yid_as_float(header_s)
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
        self.zero_measurement_inclination_ns_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 32)
        self.zero_measurement_inclination_ns_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 33)
        self.zero_measurement_inclination_ew_before_penetration_test = utils.parse_measurement_var_as_float(header_s, 34)
        self.zero_measurement_inclination_ew_after_penetration_test = utils.parse_measurement_var_as_float(header_s, 35)
        self.mileage = utils.parse_measurement_var_as_float(header_s, 41)

        self.df = self.parse_data(header_s, data_s, path, self.type)

    @staticmethod
    def parse_data(header_s, data_s, path, type_gef, columns_number=None, columns_info=None):
        if path:
            gef = re.search(r'gef', path.lower())
            if gef and type_gef == 'cpt' and columns_number is None and columns_info is None:
                columns_number = utils.parse_columns_number(header_s)
                columns_info = []
                for column_number in range(1, columns_number + 1):
                    column_info = utils.parse_column_info(header_s, column_number,
                                                          MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT)
                    columns_info.append(column_info)
            sep = csv.Sniffer().sniff(data_s).delimiter
            return pd.read_csv(io.StringIO(data_s), sep=sep, names=columns_info, index_col=False)


class ParseBORE:
    def __init__(self, path=None, string=None):
        self.path = path
        self.s = string
        self.zid = None  # ground level
        self.x = None
        self.y = None
        self.type = None
        self.end_depth_of_penetration_test = None
        self.project_id = None
        self.column_separator = None
        self.record_separator = None
        self.file_date = None
        self.project_id = None
        self.type = None

        # List of all the possible measurement variables

        if self.s is None:
            with open(path, encoding='utf-8', errors='ignore') as f:
                self.s = f.read()

        end_of_header = utils.parse_end_of_header(self.s)
        header_s, data_s = self.s.split(end_of_header)

        columns_number = utils.parse_columns_number(header_s)
        self.file_date = utils.parse_file_date(header_s)
        self.project_id = utils.parse_project_type(header_s, self.type)
        self.type = utils.parse_gef_type(header_s)
        self.x = utils.parse_xid_as_float(header_s)
        self.y = utils.parse_yid_as_float(header_s)
        self.zid = utils.parse_zid_as_float(header_s)
        column_separator = utils.parse_column_separator(header_s)
        record_separator = utils.parse_record_separator(header_s)
        data_s_rows = data_s.split(record_separator)
        data_rows_soil = self.extract_soil_info(data_s_rows, columns_number, column_separator)
        df_column_info = self.parse_data_column_info(header_s, data_s, column_separator, columns_number)
        df_soil_type = self.parse_data_soil_type(data_rows_soil)
        df_soil_code = self.parse_data_soil_code(data_rows_soil)
        df_soil_quantified = self.data_soil_quantified(data_rows_soil)
        df_additional_info = self.parse_add_info_as_string(data_rows_soil)
        self.df_bore = pd.concat([df_column_info, df_soil_code, df_soil_type, df_soil_quantified,
                                  df_additional_info], axis=1,
                                 sort=False)

    @staticmethod
    def parse_add_info_as_string(data_rows_soil):
        add_infos = ['additional_info']
        lst = []
        for row in data_rows_soil:
            add_info = ""
            for i in range(len(row)-1):
                if i >= 1:
                    add_info = add_info + utils.parse_add_info(row[i])
            lst.append(add_info)
        df_add_infos = pd.DataFrame(lst, columns=add_infos)
        return df_add_infos

    @staticmethod
    def extract_soil_info(data_s_rows, columns_number, column_separator):
        data_rows_soil = []
        for row in data_s_rows:
            new_row = row.split(column_separator)[columns_number:-1]
            data_rows_soil.append(new_row)
        return data_rows_soil[:-1]

    @staticmethod
    def parse_data_column_info(header_s, data_s, sep, columns_number, columns_info=None):
        if columns_info is None:
            columns_info = []
            for column_number in range(1, columns_number + 1):
                column_info = utils.parse_column_info(header_s, column_number,
                                                      MAP_QUANTITY_NUMBER_COLUMN_NAME_BORE)
                columns_info.append(column_info)
        df_column_info = pd.read_csv(io.StringIO(data_s), sep=sep, names=columns_info, index_col=False,
                                     usecols=columns_info)
        return df_column_info

    @staticmethod
    def parse_data_soil_type(data_rows_soil):
        lst = []
        for row in data_rows_soil:
            for i in range(len(row)):
                if i == 0:
                    soil_quantified = utils.create_soil_type(row[i])
                    lst.append(soil_quantified)
        df_soil_type = pd.DataFrame(lst, columns=['Soil_type'])
        return df_soil_type

    @staticmethod
    def parse_data_soil_code(data_rows_soil):
        lst = []
        for row in data_rows_soil:
            for i in range(len(row)):
                if i == 0:
                    soil_type = utils.parse_soil_code(row[i])
                    lst.append(soil_type)
        df_soil_code = pd.DataFrame(lst, columns=['Soil_code'])
        return df_soil_code

    @staticmethod
    def data_soil_quantified(data_rows_soil):
        lst = []
        for row in data_rows_soil:
            for i in range(len(row)):
                if i == 0:
                    soil_quantified = utils.soil_quantification(row[i])
                    lst.append(soil_quantified)
        df_soil_quantified = pd.DataFrame(lst, columns=['Gravel', 'Sand', 'Clay', 'Loam', 'Peat', 'Silt'])
        return df_soil_quantified



