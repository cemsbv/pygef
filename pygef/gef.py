import io
import re
import numpy as np
import pandas as pd
from pygef.soil import GROUND_CLASS, det_ground_pressure


class ParseGEF:
    def __init__(self, path=None, string=None):
        """
        Base class of gef parser. Is inherited for both CPT and Borehole gef files.
        :param path: (str) Path to gef file.
        """
        self.path = path
        self.z0 = None  # ground level
        self.x = None
        self.y = None
        self.type = None
        self.s = string

        if self.s is None:
            with open(path) as f:
                self.s = f.read()

        g = re.search(r"#ZID.+", self.s)
        if g:
            self.z0 = float(g.group().split(",")[1])

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

        g = re.search(r"#XYID.+", self.s)
        if g:
            g = g.group().split(",")
            self.x = int(g[1].split('.')[0])
            self.y = int(g[2].split('.')[0])

    def det_data_and_sep(self):
        g = re.search(r"(?<=#COLUMN\D.)\d+|(?<=#COLUMN\D..)\d+|(?<=#COLUMN\D)\d+", self.s)
        col_index = None
        if g is not None:
            col_index = int(g.group())

        # Parse measure data and determine the separator.
        g = re.search(r"#EOH(\n|.)+", self.s)
        g = g.group().replace(";!", "")
        g = "\n".join(g.split("\n")[1:])
        g = g.replace(" \n ", "\n")
        g = g.replace("|", "")
        g = g.replace("!", "")

        if ";" in g:
            sep = ";"
        elif " " in g:
            sep = " "
        elif "\t" in g:
            sep = "\t"

        return g, sep, col_index


class ParseCPT(ParseGEF):
    def __init__(self, path=None, string=None, data=True, clean=("l", "qc", "fs"), remove_others=True):
        """
        Parse CPT files.

        :param path: (str)
        :param data: (bool) Evaluate the data.
        :param clean:
        :param remove_others:
        """
        ParseGEF.__init__(self, path, string)
        self.columns = None
        self.units = []
        self.header = []
        self.df = None
        self.contains = False

        try:
            # Find column information
            g = re.findall(r"#COLUMNINFO.+", self.s)

            a = None
            for i in g:
                a = i.split(",")
                self.units.append(a[1])
                self.header.append(a[2])

            if a is not None:
                self.columns = list(range(1, int(a[0][-1]) + 1))
            if data and a is not None:
                g, sep, _ = self.det_data_and_sep()

                flag = 2
                for i in range(len(self.header)):
                    name = self.header[i].lower()
                    if re.search("(conus|tip|punt|cone)", name, flags=flag) is not None:
                        self.header[i] = "qc"
                    elif re.search("tijd", name, flags=flag) is not None:
                        self.header[i] = "t"
                    elif re.search("(lengte|length|diepte|depth)", name, flags=flag) is not None:
                        self.header[i] = "l"
                    elif re.search("(wrijvingsweerstand|plaatselijke.wrijving|lokale.wrijving|sleeve|sleeve.friction)",
                                   name, flags=flag) is not None:
                        self.header[i] = "fs"
                    elif re.search("(u2|waterdruk schouder)", name, flags=flag) is not None:
                        self.header[i] = "u2"
                    elif re.search("u1", name, flags=flag) is not None:
                        self.header[i] = "u1"
                    elif re.search("gecorrigeerd", name, flags=flag) is not None:
                        self.header[i] = "correction"
                    elif re.search(r"helling(?! [xynzow])", name, flags=flag) is not None:
                        self.header[i] = "slope"  # total slope
                    elif re.search(r"helling[ x_]+|helling.+zuid",  name, flags=flag):
                        self.header[i] = "helling_x"
                    elif re.search(r"helling[ y_]+|helling.+west", name, flags=flag):
                        self.header[i] = "helling_y"
                    elif re.search(r"wrijvin.+getal", name, flags=flag):
                        self.header[i] = "Rf"

                if sep == " ":
                    g = re.sub(r"[^\S\n]+", ";", g)
                    sep = ";"
                    g = re.sub(r"(?<=\n);", "", g)
                    g = re.sub(r"^;", "", g, 1)

                try:
                    self.df = pd.read_table(io.StringIO(g), sep=sep, names=self.header, index_col=False, dtype=np.float32)
                except IndexError:
                    self.df = pd.read_table(io.StringIO(g), sep=sep, names=self.header)

                if 'l' in self.df.columns:
                    self.df["l"] = np.abs(self.df["l"].values)
                    if self.z0:
                        self.df["nap"] = self.z0 - self.df.l.values

                # determine helling result
                if "helling_y" in self.df.columns \
                    and "helling_x" in self.df.columns \
                        and "slope" not in self.df.columns:
                    self.df["slope"] = np.sqrt(self.df.helling_x.values**2 + self.df.helling_y.values**2)

                if clean:
                    if set(clean).issubset(self.df):
                        if remove_others:
                            self.df = self.df[list(clean)]
                        if "t" in self.df.columns:
                            del self.df["t"]

                        self.df = self.df[self.df < 980]
                        self.df = self.df[self.df > - 980]
                        self.df = self.df.dropna()
                        self.contains = True
                    else:
                        self.contains = False
                        print(clean, "not in df")

        except ValueError or AttributeError as e:
            print("Parsing error", e)
            self.df = None

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
                or self.z0 is None:
            self.df = pd.DataFrame()
            return

        for i in range(self.df.shape[0]):
            z = self.z0 - self.df.l.values[i]

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
                                subsoil += "1"
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


