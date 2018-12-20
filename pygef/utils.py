import re
import logging
from datetime import datetime


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
        logging.error(f'Could not parse {f}. Message: {e}')
        return None


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
    :param s:
    :return:
    """
    return parse_regex_cast(r'(#EOH[= ]+)', s, str, 1)


def parse_measurement_var_as_float(s, var_number):
    """
    Function that returns a measurement variable as a float.

    :param s: (str) String from which the variable is parsed.
    :param var_number: (int) Variable number.
    :return: Variable value.
    """
    return parse_regex_cast(r'#MEASUREMENTVAR[= ]+{}[, ]+([\d-]+\.?\d*)'.format(var_number), s, float, 1)


def parse_project_type(s, gef_type):
    """
    Function that returns the project type as an int.

    :param s: (str) String from which the project type is parsed.
    :param gef_type: (str) String from which the gef type is given.
    :return: Project type number.
    """
    project_id = None
    if gef_type == 'cpt':
        project_id = parse_regex_cast(r'PROJECTID[\s=a-zA-Z,]*(\d*)', s, int, 1)
    elif gef_type == 'bore':
        project_id = parse_regex_cast(r'#PROJECTID+[^a-zA-Z]+([\w-]+)', s, str, 1)
    return project_id


def parse_zid_as_float(s):
    """
    Function that returns the zid as a float.

    :param s: (str) String from which the zid is parsed.
    :return: ZID number.
    """
    return parse_regex_cast(r"#ZID[\s=]*.*?, *((\d|\.)*)", s, float, 1)


def parse_xid_as_float(s):
    """
    Function that returns the x coordinate as a float.

    :param s:(str) String from which the xid is parsed.
    :return: xid value.
    """
    return parse_regex_cast(r"#XYID[ =]*.*?,\s*(\d*(\.|\d)*),\s*(\d*(\.|\d)*)", s, float, 1)


def parse_yid_as_float(s):
    """
    Function that returns the y coordinate as a float.

    :param s: (str) String from which the yid is parsed.
    :return: yid value.
    """
    return parse_regex_cast(r"#XYID[ =]*.*?,\s*(\d*(\.|\d)*),\s*(\d*(\.|\d)*)", s, float, 3)


def parse_gef_type(s):
    proc_code = parse_regex_cast(r"#(REPORTCODE|PROCEDURECODE)[^a-zA-Z]+([\w-]+)", s,
                                 lambda x: x.lower(), 2)

    if "cpt" in proc_code or "dis" in proc_code:
        gef_type = "cpt"
    elif "bore" in proc_code:
        gef_type = "bore"
    else:
        gef_type = None

    return gef_type


def parse_file_date(s):
    g = re.search(r'FILEDATE[\s=]*((\d|[, -])*)', s)

    if g:
        try:
            file_date = g.group(1).replace(',', '-').replace(' ', '')
        except ValueError as e:
            logging.error(f'Could not parse file_date: {e}')
            return None
        return datetime.strptime(file_date, "%Y-%m-%d")


def parse_columns_number(s):

    """
    Function that returns the columns number as an int.
    :param s: (str) String from which the yid is parsed.
    :return: Columns number value.
    """
    return max(map(int, re.findall(r'#COLUMNINFO[= ]+(\d*)', s)))


def parse_quantity_number(s, column_number):
    """

    :param s:
    :param column_number:
    :return:
    """
    return parse_regex_cast(r'#COLUMNINFO[= ]+{}[, ]+\S+[, ][^,]*[, ]+(\d+)'.format(column_number), s, int, 1)


def parse_column_info(s, column_number, dictionary):
    """
    Function that returns the column info assigned to a quantity number.
    :param s:
    :param column_number:
    :param dictionary:
    :return:
    """
    quantity_number = parse_quantity_number(s, column_number)
    column_info = dictionary[quantity_number]

    return column_info


def parse_column_separator(s):
    """

    :param s:
    :return:
    """
    return parse_regex_cast(r"#COLUMNSEPARATOR+[= ]+(.)", s, str, 1)


def parse_record_separator(s):
    """
    
    :param s: 
    :return: 
    """""
    return parse_regex_cast(r"#RECORDSEPARATOR+[= ]+(.)", s, str, 1)


def create_soil_type(s):
    """

    :param s:
    :return:
    """
    # soil_string = parse_soil_type(s)
    string_noquote = s[1:-1]
    split_letters = list(string_noquote)

    # split_soil_string = list(soil_string)
    dict_name = {"G": "gravel",
                 "K": "clay",
                 "L": "loam",
                 "V": "peat",
                 "Z": "sand"}
    dict_addition = {"z": "sandy",
                     "s": "silty",
                     "m": "minerals",
                     "k": "clayy",
                     "g": "grindig",
                     "h": "humeus"}
    dict_intensity = {"1": "weak",
                      "2": "moderate",
                      "3": "strong",
                      "4": "extreme"}
    dict_exceptions = {"GM": "layer information missing",
                       "NBE": "soil cannot be classified properly"}
    soil_name = ""
    if string_noquote in dict_exceptions:
        soil_name = soil_name + dict_exceptions[string_noquote]
    else:
        for i in range(len(split_letters)):
            if split_letters[i] in dict_name:
                soil_name = soil_name + ' ' + dict_name[split_letters[i]]
            elif split_letters[i] in dict_addition:
                soil_name = soil_name + ' ' + dict_addition[split_letters[i]]
            elif split_letters[i] in dict_intensity:
                soil_name = soil_name + ' ' + dict_intensity[split_letters[i]]
    return soil_name


def parse_add_info(s):
    dict_add_info = {"DO": "dark ",
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
                     "BL": "blue|",
                     "BR": "brown|",
                     "GE": "yellow|",
                     "GN": "green|",
                     "GR": "gray|",
                     "OL": "olive|",
                     "OR": "orange|",
                     "PA": "violet|",
                     "RO": "red|",
                     "WI": "white|",
                     "RZ": "pink|",
                     "ZW": "black|",
                     "ZUF": "uiterst fijn|",
                     "ZZF": "zeer fijn|",
                     "ZMF": "matig fijn|",
                     "ZMG": "matig grof|",
                     "ZZG": "zeer grof|",
                     "ZUG": "uiterst grof|",
                     "SZK": "zeer kleine spreiding|",
                     "SMK": "matig kleine spreiding|",
                     "SMG": "matig grote spreiding|",
                     "SZG": "zeer grote spreiding|",
                     "STW": "tweetoppige spreiding|",
                     "ZZH": "sterk hoekig|",
                     "ZHK": "hoekig|",
                     "ZMH": "matig hoekig|",
                     "ZMA": "afgerond|",
                     "ZSA": "sterk afgerond|",
                     "GFN": "fijn grind|",
                     "GMG": "matig grof grind|",
                     "GZG": "zeer grof grind|",
                     "FN1": "spoor fijn grind (<1%)|",
                     "FN2": "weinig fijn grind (1-25%)|",
                     "FN3": "veel fijn grind (25-50%)|",
                     "FN4": "zeer veel fijn grind (50-75%)|",
                     "FN5": "uiterst veel fijn grind (>75%)|",
                     "MG1": "spoor matig grof grind (<1%)|",
                     "MG2": "weinig matig grof grind (1-25%)|",
                     "MG3": "veel matig grof grind (25-50%)|",
                     "MG4": "zeer veel matig grof grind (50-75%)|",
                     "MG5": "uiterst veel matig grof grind(>75%)|",
                     "GG1": "spoor zeer grof grind (<1%)|",
                     "GG2": "weinig zeer grof grind (1-25%)|",
                     "GG3": "veel zeer grof grind (25-50%)|",
                     "GG4": "zeer veel zeer grof grind (50-75%)|",
                     "GG5": "uiterst veel zeer grof grind (>75%)|",
                     "AV1": "zwak amorf|",
                     "AV2": "matig amorf|",
                     "AV3": "sterk amorf|",
                     "BSV": "bosveen|",
                     "HEV": "heideveen|",
                     "MOV": "mosveen|",
                     "RIV": "rietveen|",
                     "SZV": "Scheuchzeriaveen|",
                     "VMV": "veenmosveen|",
                     "WOV": "wollegrasveen|",
                     "ZEV": "zeggeveen|",
                     "KZSL": "klei zeer slap|",
                     "KSLA": "klei slap|",
                     "KMSL": "klei matig slap|",
                     "KMST": "klei stevig|",
                     "KZST": "klei zeer stevig|",
                     "KHRD": "klei hard|",
                     "KZHR": "klei zeer hard|",
                     "LZSL": "leem zeer slap|",
                     "LSLA": "leem slap|",
                     "LMSL": "leem matig slap|",
                     "LMST": "leem matig stevig|",
                     "LSTV": "leem stevig|",
                     "LZST": "leem zeer stevig|",
                     "LHRD": "leem hard|",
                     "LZHR": "leem zeer hard|",
                     "VZSL": "veen zeer slap|",
                     "VSLA": "veen slap|",
                     "VMSL": "veen matig slap|",
                     "VMST": "veen matig stevig|",
                     "VSTV": "stevig|",
                     "LOS": "los gepakt|",
                     "NOR": "normaal gepakt|",
                     "VAS": "vast gepakt|",
                     "VGZZ": "zeer zacht|",
                     "VGZA": "zacht|",
                     "VGMZ": "matig zacht|",
                     "VGMH": "matig hard|",
                     "VGHA": "hard|",
                     "VGZH": "zeer hard|",
                     "VGEH": "extreem hard|",
                     "SCH0": "geen schelpmateriaal 0%|",
                     "SCH1": "spoor schelpmateriaal <1%|",
                     "SCH2": "weinig schelpmateriaal (1-10%)|",
                     "SCH3": "veel schelpmateriaal (10-30%)|",
                     "CA1": "kalkloos|",
                     "CA2": "kalkarm|",
                     "CA3": "kalkrijk|",
                     "GC0": "geen glauconiet 0%|",
                     "GC1": "spoor glauconiet <1%|",
                     "GC2": "weinig glauconiet (1-10%)|",
                     "GC3": "veel glauconiet (10-30%)|",
                     "GC4": "zeer veel glauconiet(30-50%)|",
                     "GC5": "uiterst veel glauconiet (>50%)|",
                     "BST1": "spoor baksteen|",
                     "BST2": "weinig baksteen|",
                     "BST3": "veel baksteen|",
                     "PUR1": "spoor puinresten|",
                     "PUR2": "weinig puinresten|",
                     "PUR3": "veel puinresten|",
                     "SIN1": "spoor sintels|",
                     "SIN2": "weinig sintels|",
                     "SIN3": "veel sintels|",
                     "STO1": "spoor stortsteen|",
                     "STO2": "weinig stortsteen|",
                     "STO3": "veel stortsteen|",
                     "VUI1": "spoor vuilnis|",
                     "VUI2": "weinig vuilnis|",
                     "VUI3": "veel vuilnis|",
                     "AF": "afval|",
                     "AS": "asfalt|",
                     "BE": "beton|",
                     "BI": "bitumen|",
                     "BT": "ballast|",
                     "BST": "baksteen|",
                     "GI": "gips|",
                     "GA": "glas|",
                     "HK": "houtskool|",
                     "HU": "huisvuil|",
                     "KA": "kalk|",
                     "KG": "kolengruis|",
                     "KO": "kolen|",
                     "KT": "krijt|",
                     "ME": "metaal|",
                     "MI": "mijnsteen|",
                     "OE": "oer|",
                     "PL": "planten|",
                     "PU": "puin|",
                     "SI": "sintels|",
                     "SL": "slakken|",
                     "WO": "wortels|",
                     "YZ": "ijzer|",
                     "GL": "gley|",
                     "RT": "roest|",
                     "SE": "silex|",
                     "BIO": "bioturbatie|",
                     "DWO": "doorworteling|",
                     "GCM": "cm-gelaagdheid|",
                     "GDM": "dm-gelaagdheid|",
                     "GDU": "dubbeltjes-gelaagdheid|",
                     "GMM": "mm-gelaagdheid|",
                     "GRG": "graafgangen|",
                     "GSC": "scheve gelaagdheid|",
                     "GSP": "spekkoek-gelaagdheid|",
                     "HOM": "homogeen|",
                     "GE1": "zwak gelaagd|",
                     "GE2": "weinig gelaagd|",
                     "GE3": "sterk gelaagd|",
                     "GEX": "gelaagd|",
                     "STGL": "met grindlagen|",
                     "STKL": "met kleilagen|",
                     "STLL": "met leemlagen",
                     "STSL": "met stenenlagen|",
                     "STVL": "met veenlagen|",
                     "STZL": "met zandlagen|",
                     "STBR": "met bruinkoollagen|",
                     "STDE": "met detrituslagen|",
                     "STGY": "met gyttjalagen|",
                     "STSC": "met schelpenlagen|",
                     "ANT": "Antropogeen|",
                     "BOO": "Boomse klei|",
                     "DEZ": "dekzand|",
                     "KEL": "keileem|",
                     "LSS": "loess|",
                     "POK": "potklei|",
                     "WAR": "warven|",
                     "DR": "Formatie van Drente|",
                     "EC": "Formatie van Echteld|",
                     "KR": "Formatie van Kreftenheye|",
                     "NA": "Formatie van Naaldwijk|",
                     "NI": "Formatie van Nieuwkoop|",
                     "TW": "Formatie van Twente|",
                     "WA": "Formatie van Waalre"}
    string_noquote = s[1:-1]
    split_string_noquote = string_noquote.split(" ")
    add_info = ""
    for i in range(len(split_string_noquote)):
        if split_string_noquote[i] in dict_add_info:
            add_info = add_info + dict_add_info[split_string_noquote[i]]
        else:
            add_info = add_info + str(split_string_noquote[i])+"|"
    return add_info




