import re
import pandas as pd
import io
import numpy as np


def parse_cpt_dino(obj, data, clean, remove_others):
    try:
        # Find column information
        g = re.findall(r"#COLUMNINFO.+", obj.s)

        a = None
        for i in g:
            a = i.split(",")
            obj.units.append(a[1])
            obj.header.append(a[2])

        if a is not None:
            obj.columns = list(range(1, int(a[0][-1]) + 1))
        if data and a is not None:
            g, sep, _ = obj.det_data_and_sep()

            flag = 2
            for i in range(len(obj.header)):
                name = obj.header[i].lower()
                if re.search("(conus|tip|punt|cone)", name, flags=flag) is not None:
                    obj.header[i] = "qc"
                elif re.search("tijd", name, flags=flag) is not None:
                    obj.header[i] = "t"
                elif re.search("(lengte|length|diepte|depth)", name, flags=flag) is not None:
                    obj.header[i] = "l"
                elif re.search("(wrijvingsweerstand|plaatselijke.wrijving|lokale.wrijving|sleeve|sleeve.friction)",
                               name, flags=flag) is not None:
                    obj.header[i] = "fs"
                elif re.search("(u2|waterdruk schouder)", name, flags=flag) is not None:
                    obj.header[i] = "u2"
                elif re.search("u1", name, flags=flag) is not None:
                    obj.header[i] = "u1"
                elif re.search("gecorrigeerd", name, flags=flag) is not None:
                    obj.header[i] = "correction"
                elif re.search(r"helling(?! [xynzow])", name, flags=flag) is not None:
                    obj.header[i] = "slope"  # total slope
                elif re.search(r"helling[ x_]+|helling.+zuid", name, flags=flag):
                    obj.header[i] = "helling_x"
                elif re.search(r"helling[ y_]+|helling.+west", name, flags=flag):
                    obj.header[i] = "helling_y"
                elif re.search(r"wrijvin.+getal", name, flags=flag):
                    obj.header[i] = "Rf"

            if sep == " ":
                g = re.sub(r"[^\S\n]+", ";", g)
                sep = ";"
                g = re.sub(r"(?<=\n);", "", g)
                g = re.sub(r"^;", "", g, 1)

            try:
                obj.df = pd.read_table(io.StringIO(g), sep=sep, names=obj.header, index_col=False, dtype=np.float32)
            except IndexError:
                obj.df = pd.read_table(io.StringIO(g), sep=sep, names=obj.header)

            if 'l' in obj.df.columns:
                obj.df["l"] = np.abs(obj.df["l"].values)
                if obj.z0:
                    obj.df["nap"] = obj.z0 - obj.df.l.values

            # determine helling result
            if "helling_y" in obj.df.columns \
                    and "helling_x" in obj.df.columns \
                    and "slope" not in obj.df.columns:
                obj.df["slope"] = np.sqrt(obj.df.helling_x.values ** 2 + obj.df.helling_y.values ** 2)

            if clean:
                if set(clean).issubset(obj.df):
                    if remove_others:
                        obj.df = obj.df[list(clean)]
                    if "t" in obj.df.columns:
                        del obj.df["t"]

                    obj.df = obj.df[obj.df < 980]
                    obj.df = obj.df[obj.df > - 980]
                    obj.df = obj.df.dropna()
                    obj.contains = True
                else:
                    obj.contains = False
                    print(clean, "not in df")

    except ValueError or AttributeError as e:
        print("Parsing error", e)
        obj.df = None


def parse_cpt_son(obj):
    obj.header = ['l', 'qc', 'fs', 'Rs']
    g = re.search(r'sondering :.+\n\s+\d+|\d+\s+:\s*aantal data-regels\s*\n', obj.s, flags=re.IGNORECASE)

    if g:
        obj.df = pd.read_table(io.StringIO(obj.s.split(g.group(0))[1]), names=obj.header, sep=r'\s+')

    else:
        print('Could not find data?', obj.path)\
