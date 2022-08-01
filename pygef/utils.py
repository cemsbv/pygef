import logging
import re
from datetime import date
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from pygef import exceptions

logger = logging.getLogger(__name__)


def cast_string(f, s):
    """
    Generic function that casts a string.

    :param f: (function) Any casting function.
    :param s: (str) String to cast.
    :return: The casted object
    """
    try:
        return f(s)
    except ValueError as e:
        return None


def first_header_value(headers, name, index=0, cast=None):
    """
    Get the first matching line with a header.

    Throws an error when the header exists but doesn't have the value at the
    passed index.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :param name:(str) Header name.
    :param index:(int) Index of the value.
    :param cast: (function) Cast to the specified type.
    :return: (str) The header value.
    """
    if name in headers:
        result = headers[name][0][index]
        if cast:
            return cast(result)
        else:
            return result


def parse_regex_cast(regex_string, s, f, group_number):
    """
    Function that searches a regex match and casts the result.

    :param regex_string: (str) Regex pattern.
    :param s: (str) String to search for regex pattern.
    :param f: (function) To apply to the regex match.
    :param group_number: (int) Which group number to query when there is a match.
    :return: Casted result.
    """
    g = re.search(regex_string, s)
    if g:
        return cast_string(f, g.group(group_number))
    else:
        return None


def parse_end_of_header(s):
    """
    Function that parses the end of the header.

    :param s:(str) String to search for regex pattern.
    :return:(str) End of the header.
    """
    return parse_regex_cast(r"(#EOH[=\s+]+)", s, str, 1)


def parse_column_void(headers: Union[dict, str]) -> Dict[int, float]:
    """
    Function that parses the column void headers and returns a dictionary that maps
    column-numbers to their void value.

    Returns a ParseGefError on duplicates and ill header formats
    Does not guarantee that all columns have a void value.

    :param headers:(Union[Dict,str]) Gef headers
    :return: (Dict[int, float]) Mapping of column-numbers to their void value.
    """
    if isinstance(headers, dict):
        # Return a list of all the second float values of all COLUMN_VOID lines
        if "COLUMNVOID" in headers:

            try:
                voids_info: List[Tuple[int, float]] = list(
                    map(
                        lambda values: (int(values[0]), float(values[1])),
                        headers["COLUMNVOID"],
                    )
                )
            except ValueError:
                raise exceptions.ParseGefError(
                    ": One of more #COLUMNVOID headers have an invalid format."
                )

    else:
        voids_info = []

        for void_line in re.finditer(r"#COLUMNVOID\s*=\s*(.*)", headers):

            voids = re.search(r"^(\d+)\s*,\s*([-+]?\d+\.?\d*)", void_line.group(1))

            if not voids:
                raise exceptions.ParseGefError(
                    ": One of more #COLUMNVOID headers have an invalid format."
                )

            voids_info.append((int(voids.group(1)), float(voids.group(2))))

    col_numbers = list(map(lambda values: values[0], voids_info))
    if any(np.unique(col_numbers, return_counts=True)[1] > 1):
        raise exceptions.ParseGefError(
            ": One or more #COLUMNVOID headers have duplicate definitions."
        )

    column_void = {item[0]: item[1] for item in voids_info}

    return column_void


def parse_measurement_var_as_float(headers, var_number):
    """
    Function that returns a measurement variable as a float.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :param var_number: (int) Variable number.
    :return: Variable value.
    """
    # Convert the variable number to a string so it's cheaper to compare
    var_number_str = str(var_number)

    try:
        if isinstance(headers, dict):
            # Loop over all headers to find the right number
            if "MEASUREMENTVAR" in headers:
                for values in headers["MEASUREMENTVAR"]:
                    if values[0] == var_number_str:
                        return float(values[1])
        else:
            # Find all '#MEASUREMENTVAR= **,' strings first
            for match in re.finditer(
                r"#MEASUREMENTVAR[=\s+]+(\d+)[, ]+([\d-]+\.?\d*)", headers
            ):
                # The first group is the variable number
                if match.group(1) == var_number_str:
                    # The second group is the actual value
                    return cast_string(float, match.group(2))

    except ValueError:
        pass


def parse_cone_id(headers):
    """
    Function that returns the cone id specified in GEF-CPT file.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: cone id.
    """
    if isinstance(headers, dict):
        return first_header_value(headers, "MEASUREMENTTEXT", index=1)
    else:
        try:
            return parse_regex_cast(
                r"#MEASUREMENTTEXT[=\s+]+4[, ]+([\w.-]+)", headers, str, 1
            )
        except ValueError:
            return None


def parse_cpt_class(headers):
    """
    Function that returns the class of the cpt as an int.
    The word class or klasse has to be defined in the parsed string.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: Cpt class.
    """
    if isinstance(headers, dict):
        all_definition = first_header_value(headers, "MEASUREMENTTEXT", index=1)
    else:
        all_definition = parse_regex_cast(
            r"#MEASUREMENTTEXT[=\s+]+6[, ](.*)", headers, str, 1
        )

    if all_definition is not None:
        return parse_regex_cast(
            r"^.*?(klasse|class).*?(\d{1})", all_definition.lower(), int, 2
        )


def parse_project_type(headers, gef_type):
    """
    Function that returns the project type as an int.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :param gef_type: (str) String from which the gef type is given.
    :return: Project type number.
    """
    if isinstance(headers, dict):
        if gef_type == "cpt":
            try:
                # Try to get the second value first
                return first_header_value(headers, "PROJECTID", index=1)
            except Exception:
                # If that fails get the first one
                return first_header_value(headers, "PROJECTID")
        elif gef_type == "bore":
            return first_header_value(headers, "PROJECTID")
    else:
        if gef_type == "cpt":
            return parse_regex_cast(r"PROJECTID[\s=a-zA-Z,]*([\w-]+)", headers, str, 1)
        elif gef_type == "bore":
            return parse_regex_cast(r"#PROJECTID+[^a-zA-Z]+([\w-]+)", headers, str, 1)


def parse_zid_as_float(headers):
    """
    Function that returns the zid as a float.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return:(float) ZID number.
    """
    if isinstance(headers, dict):
        if "ZID" in headers:
            return first_header_value(headers, "ZID", index=1, cast=float)
    else:
        return parse_regex_cast(
            r"#ZID[=\s+]+[^,]*[,\s+]+([^?!,$|\s$]+)", headers, float, 1
        )


def parse_height_system(headers):
    """
    Function that returns the zid as a float.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return:(float) ZID number.
    """
    if isinstance(headers, dict):
        return first_header_value(headers, "ZID", cast=float)
    else:
        return parse_regex_cast(r"#ZID[=\s+]+([^,]*)", headers, float, 1)


def parse_xid_as_float(headers):
    """
    Function that returns the x coordinate as a float.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return:(float) x coordinate value.
    """
    if isinstance(headers, dict):
        return first_header_value(headers, "XYID", index=1, cast=float)
    else:
        return parse_regex_cast(
            r"#XYID[=\s+]*.*?,\s*(\d*\s*(\.|\d)*),\s*(\d*(\.|\d)*)", headers, float, 1
        )


def parse_yid_as_float(headers):
    """
    Function that returns the y coordinate as a float.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return:(float) y coordinate value.
    """
    if isinstance(headers, dict):
        return first_header_value(headers, "XYID", index=2, cast=float)
    else:
        return parse_regex_cast(
            r"#XYID[=\s+]*.*?,\s*(\d*\s*(\.|\d)*),\s*(\d*(\.|\d)*)", headers, float, 3
        )


def parse_gef_type(headers):
    """
    Function that returns the gef type.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: (str) Gef type.
    """
    proc_code = ""
    if isinstance(headers, dict):
        if "REPORTCODE" in headers:
            proc_code = first_header_value(headers, "REPORTCODE").lower()
        elif "PROCEDURECODE" in headers:
            proc_code = first_header_value(headers, "PROCEDURECODE").lower()
        else:
            return None
    else:
        if parse_regex_cast(
            r"#PROCEDURECODE[^a-zA-Z]+([\w-]+)", headers, lambda x: x.lower(), 1
        ) and parse_regex_cast(
            r"#REPORTCODE[^a-zA-Z]+([\w-]+)", headers, lambda x: x.lower(), 1
        ):
            proc_code = parse_regex_cast(
                r"#REPORTCODE[^a-zA-Z]+([\w-]+)", headers, lambda x: x.lower(), 1
            )
        else:
            proc_code = parse_regex_cast(
                r"#(REPORTCODE|PROCEDURECODE)[^a-zA-Z]+([\w-]+)",
                headers,
                lambda x: x.lower(),
                2,
            )

    if "cpt" in proc_code or "dis" in proc_code:
        return "cpt"
    elif "bore" in proc_code and not "borehole" in proc_code:
        return "bore"
    elif "borehole" in proc_code:
        return "borehole-report"


def parse_file_date(headers):
    """
    Fuction to parse the file date.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: File date.
    """
    year = None
    month = None
    day = None

    if isinstance(headers, dict):
        if "FILEDATE" in headers:
            year = first_header_value(headers, "FILEDATE", index=0, cast=int)
            month = first_header_value(headers, "FILEDATE", index=1, cast=int)
            day = first_header_value(headers, "FILEDATE", index=2, cast=int)
        else:
            return None
    else:
        g = re.search(r"#FILEDATE[\s=]*(\d+)[,\s+]+(\d+)[,\s+]+(\d+)", headers)
        if g:
            year = int(g.group(1))
            month = int(g.group(2))
            day = int(g.group(3))
        else:
            return None

    return date(year, month, day)


def parse_columns_number(headers: Union[dict, str]) -> int:
    """
    Function that returns the columns number as an int.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: Columns number value.
    """
    if isinstance(headers, dict):
        if "COLUMNINFO" in headers:
            return len(headers["COLUMNINFO"])

    else:
        col_numbers = re.findall(r"#COLUMNINFO[=\s]+(\d+)", headers)
        if col_numbers:
            return len(col_numbers)

    return 0


def get_description(
    quantity_number: int,
    custom_description: str,
    dictionary: Optional[Dict[int, str]] = None,
) -> str:
    """
    Returns the default description of a quantity number if available in the
    provided dictionary, else returns the custom_description.

    :param quantity_number: (int) The quantity number of the column
    :param custom_description: (str) The column description from the .gef file
    :param dictionary: (Optional[Dict[int, str]]) The dictionary that maps
        quantity-numbers to descriptions
    :return: (str) The column description
    """

    if dictionary is not None and quantity_number in dictionary:
        return dictionary[quantity_number]
    return custom_description


def parse_column_separator(headers):
    """
    Function to parse the column separator. It is used only in the borehole class.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: Column separator.
    """
    if isinstance(headers, dict):
        return first_header_value(headers, "COLUMNSEPARATOR")
    else:
        return parse_regex_cast(r"#COLUMNSEPARATOR+[=\s+]+(.)", headers, str, 1)


def parse_test_id(headers):
    """
    Function to parse the test id.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: test id.
    """
    result = None
    if isinstance(headers, dict):
        result = first_header_value(headers, "TESTID")
    else:
        result = parse_regex_cast(r"#TESTID+[=\s+]+(.*)", headers, str, 1)

    if result is not None:
        return result.strip()


def parse_record_separator(headers):
    """
    Function to parse the record separator(end of the line). It is used only in the borehole class.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: Record separator.
    """
    if isinstance(headers, dict):
        return first_header_value(headers, "RECORDSEPARATOR")
    else:
        return parse_regex_cast(r"#RECORDSEPARATOR+[=\s+]+(.)", headers, str, 1)


def get_column_separator(headers: Union[dict, str]) -> str:
    """
    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return:
    """
    return parse_column_separator(headers) or " "


def get_record_separator(headers: Union[dict, str]) -> str:
    """
    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return:
    """
    return parse_record_separator(headers) or "\n"


def parse_soil_code(s):
    """
    Function to parse the soil code.

    :param s: (str) String with the soil code.
    :return: Soil code.
    """
    return s.replace("'", "")


def create_soil_type(s):
    """
    Function to create the description of the soil type.

    :param s: (str) Soil code.
    :return: (str) Description of the soil code.
    """
    string_noquote = s.replace("'", "")
    split_letters = list(string_noquote)

    # split_soil_string = list(soil_string)
    dict_name = {"G": "gravel", "K": "clay", "L": "loam", "V": "peat", "Z": "sand"}
    dict_addition = {
        "z": "sand",
        "s": "silt",
        "m": "mineral",
        "k": "clay",
        "g": "gravel",
        "h": "humeus",
    }
    dict_intensity = {"1": 5, "2": 10, "3": 15, "4": 20}
    dict_exceptions = {
        "GM": "layer information missing",
        "NBE": "soil cannot be classified properly",
        "W": "water",
    }
    soil_name = ""
    try:
        if string_noquote != "":
            if string_noquote in dict_exceptions:
                soil_name = soil_name + dict_exceptions[string_noquote]
            else:
                sum_addition = 0
                percentage_main_component = 100
                main_component = dict_name[split_letters[0]]
                soil_additions = ""
                for i in range(1, len(split_letters)):
                    if split_letters[i] in dict_addition:
                        soil_additions = (
                            soil_additions + " with " + dict_addition[split_letters[i]]
                        )
                    elif split_letters[i] in dict_intensity:
                        soil_additions = (
                            soil_additions
                            + " "
                            + str(dict_intensity[split_letters[i]])
                            + "%"
                        )
                        sum_addition = sum_addition + dict_intensity[split_letters[i]]
                if sum_addition > 0:
                    percentage_main_component = percentage_main_component - sum_addition
                soil_name = (
                    main_component
                    + " "
                    + str(percentage_main_component)
                    + "%"
                    + soil_additions
                )
        else:
            soil_name = "soil_not_defined"
    except KeyError:
        soil_name = "soil_not_according_with_NEN_classification"
    return soil_name


INDICES = {"g": 0, "z": 1, "k": 2, "s": 5, "m": 1, "h": 4, "l": 3, "v": 4, "p": 4}

INTENSITY = {"1": 0.05, "2": 0.10, "3": 0.15, "4": 0.20}

NO_CLASSIFY = {
    "gm": "layer information missing",
    "nbe": "soil cannot be classified properly",
    "w": "water",
}


def soil_quantification(s):
    """
    Function to create the quantification of the soil type.

    :param s:(str) Soil code.
    :return: Quantification of the soil code.
    """
    #   0    1    2    3    4     5
    # ['G', 'S', 'C', 'L', 'P', 'SI']
    dist = np.zeros(6)

    s = s.replace("'", "").split(" ")[0].lower()

    if s in NO_CLASSIFY or len(s) == 0:
        return np.ones(6) * -1

    tokens = list(enumerate(s))
    numerics = dict(filter(lambda t: t[1].isnumeric(), tokens))
    alphabetics = dict(
        filter(lambda t: not t[1].isnumeric(), tokens[1:])
    )  # skip the first one.

    for i, token in alphabetics.items():
        idx = INDICES[token]
        if (i + 1) in numerics:
            v = INTENSITY[numerics[i + 1]]
        else:
            v = 0.05
        dist[idx] = v

    # Sometimes the same soil type has multiple tokens ?? e.g. Kkgh2.
    dist[INDICES[s[0]]] = 0
    dist[INDICES[s[0]]] = 1 - dist.sum()
    return dist


def parse_add_info(headers):
    """
    Function to parse all the additional informations.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: (str) Additional informations.
    """
    dict_add_info = {
        "DO": "dark ",
        "LI": "light ",
        "TBL": "blue-",
        "TBR": "brown-",
        "TGE": "yellow-",
        "TGN": "green-",
        "TGR": "gray-",
        "TOL": "olive-",
        "TOR": "orange-",
        "TPA": "violet-",
        "TRO": "red-",
        "TWI": "white-",
        "TRZ": "pink-",
        "TZW": "black-",
        "BL": "blue ",
        "BR": "brown ",
        "GE": "yellow ",
        "GN": "green ",
        "GR": "gray ",
        "OL": "olive ",
        "OR": "orange ",
        "PA": "violet ",
        "RO": "red ",
        "WI": "white ",
        "RZ": "pink ",
        "ZW": "black ",
        "ZUF": "uiterst fijn ",
        "ZZF": "zeer fijn ",
        "ZMF": "matig fijn ",
        "ZMG": "matig grof ",
        "ZZG": "zeer grof ",
        "ZUG": "uiterst grof ",
        "SZK": "zeer kleine spreiding ",
        "SMK": "matig kleine spreiding|",
        "SMG": "matig grote spreiding ",
        "SZG": "zeer grote spreiding ",
        "STW": "tweetoppige spreiding ",
        "ZZH": "sterk hoekig ",
        "ZHK": "hoekig ",
        "ZMH": "matig hoekig ",
        "ZMA": "afgerond ",
        "ZSA": "sterk afgerond ",
        "GFN": "fijn grind ",
        "GMG": "matig grof grind ",
        "GZG": "zeer grof grind ",
        "FN1": "spoor fijn grind (<1%) ",
        "FN2": "weinig fijn grind (1-25%) ",
        "FN3": "veel fijn grind (25-50%) ",
        "FN4": "zeer veel fijn grind (50-75%) ",
        "FN5": "uiterst veel fijn grind (>75%) ",
        "MG1": "spoor matig grof grind (<1%) ",
        "MG2": "weinig matig grof grind (1-25%) ",
        "MG3": "veel matig grof grind (25-50%) ",
        "MG4": "zeer veel matig grof grind (50-75%) ",
        "MG5": "uiterst veel matig grof grind(>75%) ",
        "GG1": "spoor zeer grof grind (<1%) ",
        "GG2": "weinig zeer grof grind (1-25%) ",
        "GG3": "veel zeer grof grind (25-50%) ",
        "GG4": "zeer veel zeer grof grind (50-75%) ",
        "GG5": "uiterst veel zeer grof grind (>75%) ",
        "AV1": "zwak amorf ",
        "AV2": "matig amorf ",
        "AV3": "sterk amorf ",
        "BSV": "bosveen ",
        "HEV": "heideveen ",
        "MOV": "mosveen ",
        "RIV": "rietveen ",
        "SZV": "Scheuchzeriaveen ",
        "VMV": "veenmosveen ",
        "WOV": "wollegrasveen ",
        "ZEV": "zeggeveen ",
        "KZSL": "klei zeer slap ",
        "KSLA": "klei slap ",
        "KMSL": "klei matig slap ",
        "KMST": "klei stevig ",
        "KZST": "klei zeer stevig ",
        "KHRD": "klei hard ",
        "KZHR": "klei zeer hard ",
        "LZSL": "leem zeer slap ",
        "LSLA": "leem slap ",
        "LMSL": "leem matig slap ",
        "LMST": "leem matig stevig ",
        "LSTV": "leem stevig ",
        "LZST": "leem zeer stevig ",
        "LHRD": "leem hard ",
        "LZHR": "leem zeer hard ",
        "VZSL": "veen zeer slap ",
        "VSLA": "veen slap ",
        "VMSL": "veen matig slap ",
        "VMST": "veen matig stevig ",
        "VSTV": "stevig ",
        "LOS": "los gepakt ",
        "NOR": "normaal gepakt ",
        "VAS": "vast gepakt ",
        "VGZZ": "zeer zacht ",
        "VGZA": "zacht ",
        "VGMZ": "matig zacht ",
        "VGMH": "matig hard ",
        "VGHA": "hard ",
        "VGZH": "zeer hard ",
        "VGEH": "extreem hard ",
        "SCH0": "geen schelpmateriaal 0% ",
        "SCH1": "spoor schelpmateriaal <1% ",
        "SCH2": "weinig schelpmateriaal (1-10%) ",
        "SCH3": "veel schelpmateriaal (10-30%) ",
        "CA1": "kalkloos ",
        "CA2": "kalkarm ",
        "CA3": "kalkrijk ",
        "GC0": "geen glauconiet 0% ",
        "GC1": "spoor glauconiet <1% ",
        "GC2": "weinig glauconiet (1-10%) ",
        "GC3": "veel glauconiet (10-30%) ",
        "GC4": "zeer veel glauconiet(30-50%) ",
        "GC5": "uiterst veel glauconiet (>50%) ",
        "BST1": "spoor baksteen ",
        "BST2": "weinig baksteen ",
        "BST3": "veel baksteen ",
        "PUR1": "spoor puinresten ",
        "PUR2": "weinig puinresten ",
        "PUR3": "veel puinresten ",
        "SIN1": "spoor sintels ",
        "SIN2": "weinig sintels ",
        "SIN3": "veel sintels ",
        "STO1": "spoor stortsteen ",
        "STO2": "weinig stortsteen ",
        "STO3": "veel stortsteen ",
        "VUI1": "spoor vuilnis ",
        "VUI2": "weinig vuilnis ",
        "VUI3": "veel vuilnis ",
        "AF": "afval ",
        "AS": "asfalt ",
        "BE": "beton ",
        "BI": "bitumen ",
        "BT": "ballast ",
        "BST": "baksteen ",
        "GI": "gips ",
        "GA": "glas ",
        "HK": "houtskool ",
        "HU": "huisvuil ",
        "KA": "kalk ",
        "KG": "kolengruis ",
        "KO": "kolen ",
        "KT": "krijt ",
        "ME": "metaal ",
        "MI": "mijnsteen ",
        "OE": "oer ",
        "PL": "planten ",
        "PU": "puin ",
        "SI": "sintels ",
        "SL": "slakken ",
        "WO": "wortels ",
        "YZ": "ijzer ",
        "GL": "gley ",
        "RT": "roest ",
        "SE": "silex ",
        "BIO": "bioturbatie ",
        "DWO": "doorworteling ",
        "GCM": "cm-gelaagdheid ",
        "GDM": "dm-gelaagdheid ",
        "GDU": "dubbeltjes-gelaagdheid ",
        "GMM": "mm-gelaagdheid ",
        "GRG": "graafgangen ",
        "GSC": "scheve gelaagdheid ",
        "GSP": "spekkoek-gelaagdheid ",
        "HOM": "homogeen ",
        "GE1": "zwak gelaagd ",
        "GE2": "weinig gelaagd ",
        "GE3": "sterk gelaagd ",
        "GEX": "gelaagd ",
        "STGL": "met grindlagen ",
        "STKL": "met kleilagen ",
        "STLL": "met leemlagen ",
        "STSL": "met stenenlagen ",
        "STVL": "met veenlagen ",
        "STZL": "met zandlagen ",
        "STBR": "met bruinkoollagen ",
        "STDE": "met detrituslagen ",
        "STGY": "met gyttjalagen ",
        "STSC": "met schelpenlagen ",
        "ANT": "Antropogeen ",
        "BOO": "Boomse klei ",
        "DEZ": "dekzand ",
        "KEL": "keileem ",
        "LSS": "loess ",
        "POK": "potklei ",
        "WAR": "warven ",
        "DR": "Formatie van Drente ",
        "EC": "Formatie van Echteld ",
        "KR": "Formatie van Kreftenheye ",
        "NA": "Formatie van Naaldwijk ",
        "NI": "Formatie van Nieuwkoop ",
        "TW": "Formatie van Twente ",
        "WA": "Formatie van Waalre ",
    }

    if isinstance(headers, dict):
        raise Exception("todo")
    else:
        string_noquote = headers[1:-1]
        string2list = string_noquote.split("''")
        add_info = ""
        for i, string in enumerate(string2list):
            if string:
                add_info += "{}) ".format(i + 1) + "".join(
                    [
                        dict_add_info[string_split]
                        if string_split in dict_add_info
                        else string_split + " "
                        for string_split in string.split(" ")
                    ]
                )
        return add_info


def assign_multiple_columns(df, columns, partial_df):
    return df.drop(columns).hstack(partial_df[columns])


def kpa_to_mpa(df, columns):
    return assign_multiple_columns(df, columns, df[columns] * 10**-3)


def none_to_zero(df):
    return df.fill_null(0.0)


def nap_to_depth(zid, nap):
    return -(nap - zid)


def depth_to_nap(depth, zid):
    return zid - depth


def join_gef(bore, cpt):
    """
    Join a cpt and bore file in one Dataframe based on depth.

    :param bore: (ParseBORE)
    :param cpt: (ParseCPT)
    :return: (pl.DataFrame)
    """
    df_cpt = cpt.df.assign(join_idx=0)
    df_bore = bore.df.loc[
        bore.df[["G", "S", "C", "L", "P", "SI"]].sum(1) == 1
    ].reset_index(drop=True)

    df_cpt = df_cpt[df_cpt["depth"] > df_bore["depth_top"].min()].reset_index(drop=True)
    idx = np.searchsorted(df_cpt["depth"].values, df_bore["depth_top"].values)

    a = np.zeros(df_cpt.shape[0])
    for i in range(len(idx) - 1):
        a[idx[i] : idx[i + 1]] = i

    a[idx[i + 1] :] = i + 1
    df_cpt["join_idx"] = a

    return df_cpt.merge(
        df_bore[["soil_code", "G", "S", "C", "L", "P", "SI"]].reset_index(-1),
        left_on="join_idx",
        right_on="index",
    ).drop(["index", "join_idx"], axis=1)
