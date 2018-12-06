import re
import logging
from dateutil.parser import parse
import numpy as np
import pandas as pd
from pygef.soil import GROUND_CLASS, det_ground_pressure
from pygef import extension


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

        g = re.search(r'FILEDATE[\s=]*((\d|[,-])*)', self.s)
        if g:
            try:
                self.file_date = parse(g.group(1).replace(',', '-'))
            except ValueError as e:
                logging.error(f'Could not parse file_date: {e}')

        g = re.search(r'PROJECTID[\s=a-zA-Z,]*(\d*)', self.s)
        if g:
            try:
                self.project_id = int(g.group(1))
            except ValueError as e:
                logging.error(f'Could not cast project_id to int: {e}')

        g = re.search(r"#ZID[\s=]*.*?, *((\d|\.)*)", self.s)
        if g:
            try:
                self.zid = float(g.group(1))
            except ValueError as e:
                logging.error(f'Could not cast z_id to float: {e}')

        g = re.search(r"REPORTCODE[^a-zA-Z]+[\w-]+", self.s)
        if g:
            report_code = re.sub(r"REPORTCODE[^a-zA-Z]+", "", g.group()).lower()
            if "cpt" in report_code or "diss" in report_code:
                self.type = "cpt"
            elif "bore" in report_code:
                self.type = "bore"

        g = re.search(r"PROCEDURECODE[^a-zA-Z]+[\w-]+", self.s)
        if g:
            proc_code = re.sub(r"PROCEDURECODE[^a-zA-Z]+", "", g.group().lower())
            if "cpt" in proc_code or "dis" in proc_code:
                self.type = "cpt"
            elif "bore" in proc_code:
                self.type = "bore"

        g = re.search(r"#XYID[ =]*.*?,\s*(\d*(\.|\d)*),\s*(\d*(\.|\d)*)", self.s)
        if g:
            try:
                self.x = float(g.group(1))
                self.y = float(g.group(3))
            except ValueError as e:
                logging.error(f'Could not cast x, y coordinates to float: {e}')

        g = re.search(r'#MEASUREMENTVAR[= ]+1[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.nom_surface_area_cone_tip = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+2[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.nom_surface_area_friction_element = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+3[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.net_surface_area_quotient_of_the_cone_tip = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+4[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.net_surface_area_quotient_of_the_friction_casing = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+5[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.distance_between_cone_and_centre_of_friction_casing = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+6[, ]+(\d)', self.s)
        if g:
            self.friction_present = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+7[, ]+(\d+)', self.s)
        if g:
            self.ppt_u1_present = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+8[, ]+(\d+)', self.s)
        if g:
            self.ppt_u2_present = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+9[, ]+(\d+)', self.s)
        if g:
            self.ppt_u3_present = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+10[, ]+(\d+)', self.s)
        if g:
            self.inclination_measurement_present = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+11[, ]+(\d+)', self.s)
        if g:
            self.use_of_back_flow_compensator = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+12[, ]+(\d+)', self.s)
        if g:
            self.type_of_cone_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+13[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.pre_excavated_depth = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+14[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.groundwater_level = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+15[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.water_depth_offshore_activities = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+16[, ]+(\d+\.?\d*)', self.s)
        if g:
            self.end_depth_of_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+17[, ]+(\d+)', self.s)
        if g:
            self.stop_criteria = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+20[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_cone_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+21[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_cone_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+22[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_friction_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+23[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_friction_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+24[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_ppt_u1_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+25[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_ppt_u1_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+26[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_ppt_u2_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+27[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_ppt_u2_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+28[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_ppt_u3_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+29[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_ppt_u3_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+30[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_inclination_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+31[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_inclination_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+32[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_inclination_ns_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+33[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_inclination_ns_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+34[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_inclination_ew_before_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+35[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.zero_measurement_inclination_ew_after_penetration_test = float(g.group(1))

        g = re.search(r'#MEASUREMENTVAR[= ]+41[, ]+([\d-]+\.?\d*)', self.s)
        if g:
            self.mileage = float(g.group(1))

    def det_data_and_sep(self):
        g = re.search(r"(?<=#COLUMN\D.)\d+|(?<=#COLUMN\D..)\d+|(?<=#COLUMN\D)\d+", self.s)
        col_index = None
        if g is not None:
            col_index = int(g.group())

        # Parse measure data and determine the separator.
        g = re.search(r"#EOH.*?\n((.|[\r\n])*)", self.s)
        g = re.sub(r'[|!];!', '', g.group(1))
        g = re.sub(r'[;!|]\n', '\n', g)

        sep = re.search(r'[; \t]', g).group(0)

        return g, sep, col_index


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
