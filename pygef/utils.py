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


def parse_measurement_var_as_float(s, var_number):
    """
    Function that returns a measurement variable as a float.

    :param s: (str) String from which the variable is parsed.
    :param var_number: (int) Variable number.
    :return: Variable value.
    """
    return parse_regex_cast(r'#MEASUREMENTVAR[= ]+{}[, ]+([\d-]+\.?\d*)'.format(var_number), s, float, 1)


def parse_project_type_as_int(s):
    """
    Function that returns the project type as an int.

    :param s: (str) String from which the project type is parsed.
    :return: Project type number.
    """
    return parse_regex_cast(r'PROJECTID[\s=a-zA-Z,]*(\d*)', s, int, 1)


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
    proc_code = parse_regex_cast(r"PROCEDURECODE[^a-zA-Z]+([\w-]+)", s,
                                 lambda x: x.lower(), 1)

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
    return parse_regex_cast(r'#COLUMN[= ]+(\d*)', s, int, 1)


def parse_quantity_number(s, column_number):
    """
    Function that parses the quantity number of a column info.
    :param s:
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


