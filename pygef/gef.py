import re
import pygef.utils as utils
import numpy as np
import pandas as pd
from pygef.soil import GROUND_CLASS, det_ground_pressure
from pygef import extension
import io
import csv

COLUMN_NAMES = ["penetration length",  # 1
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

MAP_QUANTITY_NUMBER_COLUMN_NAME = dict(enumerate(COLUMN_NAMES, 1))


class ParseSon:
    def __init__(self, path=None, string=None):
        self.path = path
        self.s = string
        self.z0 = None  # ground level
        self.x = None
        self.y = None
        self.type = 'cpt'
        self.end_depth_of_penetration_test = None

        if self.s is None:
            with open(path, encoding='utf-8', errors='ignore') as f:
                self.s = f.read()


class ParseGEF:
    def __init__(self, path=None, string=None):
        """
        Base class of gef parser. Is inherited for both CPT and Borehole gef files.
        :param path: (str) Path to gef file.
        """
        self.path = path
        self.zid = None  # ground level
        self.x = None
        self.y = None
        self.type = None
        self.file_date = None
        self.project_id = None
        self.s = string
        self.columns_number = None

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
        self.project_id = utils.parse_project_type_as_int(header_s)
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

        self.df = self.parse_data(header_s, data_s, path)

    @staticmethod
    def parse_data(header_s, data_s, path, columns_number=None, columns_info=None):
        if path:
            cpt = re.search(r'gef', path.lower())
            if cpt and columns_number is None and columns_info is None:
                columns_number = utils.parse_columns_number(header_s)
                # Return columns info list:
                columns_info = []
                for column_number in range(1, columns_number + 1):
                    column_info = utils.parse_column_info(header_s, column_number, MAP_QUANTITY_NUMBER_COLUMN_NAME)
                    columns_info.append(column_info)

            sep = csv.Sniffer().sniff(data_s).delimiter
            return pd.read_csv(io.StringIO(data_s), sep=sep, names=columns_info, index_col=False)

#        if bore:
#            need to reimplement.


class ParseCPT(ParseGEF, ParseSon):
    def __init__(self, path=None, string=None, data=True, clean=("l", "qc", "fs"), remove_others=True):
        """
        Parse CPT files.

        :param path: (str)
        :param data: (bool) Evaluate the data.
        :param clean:
        :param remove_others:
        """
        self.columns = None
        self.units = []
        self.header = []
        self.df = None
        self.contains = False

        if path:
            g = re.search(r'son|nen$', path.lower())
            if g:
                ParseSon.__init__(self, path, string)
                extension.parse_cpt_son(self)
            else:
                ParseGEF.__init__(self, path, string)
                extension.parse_cpt_dino(self, data, clean, remove_others)

    def det_soil(self, bro):
        """
        Determine the soil based on a drill.

        :param bro: ParseBro object
        :return:
        """
        # soil print
        # [[ 0.8, 0, 0.1, 0.1, 0],
        #  [ 0.8, 0, 0.1, 0.1, 0]]
        sp = []

        no_soil = np.zeros(5)

        # Check if there is enough data to determine the soil layers.
        if bro.percentage_print.size == 0 \
                or self.zid is None:
            self.df = pd.DataFrame()
            return

        for i in range(self.df.shape[0]):
            z = self.zid - self.df.l.values[i]

            for j in range(len(bro.depth_btm)):
                top = bro.z0 - bro.depth_top[j]
                btm = bro.z0 - bro.depth_btm[j]

                if btm < z < top:
                    soil_percentage = bro.percentage_print[j]

                    if np.sum(soil_percentage) > 0:
                        sp.append(soil_percentage)
                    else:
                        sp.append(no_soil)

            # Some depths are no soil measured.
            if i == len(sp) - 1:
                pass
            else:
                sp.append(no_soil)

        # Extrapolate the last soil in reversed order
        last = sp[-1]
        for i in range(2, len(sp) + 1):
            if np.sum(last) != 0 and np.sum(sp[-i]) == 0:  # if np.sum(s) == 0 --> there is no soil
                sp[-i] = last
            last = sp[-i]

        # soil print
        sp = np.vstack(sp)

        if sp.size == 0 or np.sum(sp) == 0:
            self.df["soil_print"] = np.nan
            return False

        # find the first index where the sum of the soil print == 0, thus no soil
        indexes = np.argwhere(np.sum(sp, axis=1) == 0)
        if indexes.size == 0:
            i = -1
        else:
            i = indexes[0][0]

        sig = det_ground_pressure(self.df.l.values[:i], sp[:i])
        sp = pd.Series(np.split(sp.flatten(), sp.shape[0], axis=0), name="soil_print")
        sig = pd.Series(sig, name="ground_pressure_bro")
        self.df = pd.concat([self.df, sig, sp], axis=1)
        self.df = self.df.dropna()
        return True


class ParseBRO(ParseGEF):
    def __init__(self, path=None, string=None, data=True):
        """
        Parse borehole gef files.

        :param path: (str)
        :param data: (bool) Parse the data. Otherwise only the header will be parsed.
        """
        ParseGEF.__init__(self, path, string)
        self.depth_top = []
        self.depth_btm = []
        self.main_soil = []
        self.sub_soil = []
        self.sub_soil_2 = []
        self.sub_soil_3 = []
        self.notes = []
        self.color = []
        self.main_class = []
        self.soil = None  # [2, 1, 0]  Soil classes
        self.percentage = None  # [0.8, 0.1. 0.1]  Percentages

        # [0.7, 0.1, 0.1, 0, 0.1]  Percentages of the whole soil print
        self.percentage_print = None

        if data:
            self._parse_soil_coding()
            self._det_soil_print()

    def _parse_soil_coding(self):
        g, sep, col_index = self.det_data_and_sep()
        rq = re.compile(r"[shkgz]\d?")

        col_index = 9 if col_index is None else col_index

        for line in g.split("\n"):
            a = line.split(sep)

            if len(a) > 2:
                self.depth_top.append(float(a[0]))
                self.depth_btm.append(float(a[1]))

                if len(a) > col_index:
                    s = a[col_index].replace("'", "").split(" ")[0]

                    if "NBE" in s:
                        self.main_soil.append(None)
                        self.sub_soil.append(None)
                        self.sub_soil_2.append(None)
                        self.sub_soil_3.append(None)
                    elif s[0] in GROUND_CLASS:
                        self.main_soil.append(s[0])
                        matches = rq.findall(s)

                        if len(matches) == 0:
                            matches.append(None)
                        if len(matches) == 1:
                            matches.append(None)
                        if len(matches) == 2:
                            matches.append(None)

                        c = 0
                        for subsoil in matches:
                            if subsoil and len(subsoil) == 1:
                                subsoil += "1"  # change code of 'z' to 'z1'

                            # Filter flawed codes the subsoils may not be the same as the mail soil. Like 'Kk1'
                            if subsoil and subsoil[0] == s[0].lower():
                                subsoil = None
                            if c == 0:
                                self.sub_soil.append(subsoil)
                                c += 1
                            elif c == 1:
                                self.sub_soil_2.append(subsoil)
                                c += 1
                            else:
                                self.sub_soil_3.append(subsoil)

                if len(a) > 10:
                    self.color.append(a[10].replace("'", ""))
                else:
                    self.color.append(None)
                if len(a) > 11:
                    self.notes.append(a[11].replace("'", ""))
                else:
                    self.notes.append(None)

    def _det_soil_print(self):
        for i in range(len(self.main_soil)):
            if self.main_soil[i]:
                a = GROUND_CLASS.get(self.main_soil[i], GROUND_CLASS.get(self.main_soil[i][0], None))
            else:
                a = None
            self.main_class.append(a)

        # Soils are divided in numerical classes

        self.soil = np.zeros((len(self.main_soil), 4))
        self.percentage = np.zeros_like(self.soil)
        self.percentage_print = np.zeros((len(self.main_soil), 5))

        i = 0
        for ms, s1, s2, s3 in zip(self.main_soil, self.sub_soil, self.sub_soil_2, self.sub_soil_3):
            """
            ms = main soil
            s1 = sub soil
            s2 = sub soil 2
            """
            s1_int = GROUND_CLASS[s1[0].upper()] if s1 else None
            s2_int = GROUND_CLASS[s2[0].upper()] if s2 else None
            s3_int = GROUND_CLASS[s3[0].upper()] if s3 else None
            ms_int = GROUND_CLASS[ms] if ms else None

            # If Main soil = L and subsoil = s than the main soil should be L 100%
            if ms_int == 2:
                if s3_int == 2:
                    s3 = None
                    s3_int = None
                if s2_int == 2:
                    s2 = None
                    s2_int = None
                if s1_int == 2:
                    s1 = None
                    s1_int = None

            self.soil[i] = np.array([ms_int, s1_int, s2_int, s3_int])

            for _ in range(4):
                ms_p = 1 if ms_int is not None else 0
                s1_p = 0
                s2_p = 0
                s3_p = 0

                if s1 is not None:
                    s1_p = float(s1[1]) / 20
                    ms_p -= s1_p
                if s2 is not None:
                    s2_p = float(s2[1]) / 20
                    ms_p -= s2_p
                if s3 is not None:
                    s3_p = float(s3[1]) / 20
                    ms_p -= s3_p

            self.percentage[i] = np.array([ms_p, s1_p, s2_p, s3_p])

            # Vector encoding
            if ms_int is not None:
                self.percentage_print[i, ms_int] = ms_p
            if s1_int is not None:
                self.percentage_print[i, s1_int] = s1_p
            if s2_int is not None:
                self.percentage_print[i, s2_int] = s2_p
            if s3_int is not None:
                self.percentage_print[i, s3_int] = s3_p
            i += 1
