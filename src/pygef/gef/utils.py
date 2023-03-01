from __future__ import annotations

import logging
import re
from datetime import date
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from pygef import exceptions
from pygef.gef.mapping import MAPPING_PARAMETERS

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
    except ValueError:
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


def parse_column_void(headers: Union[dict, str]) -> Dict[int, float]:
    """
    Function that parses the column void headers and returns a dictionary that maps
    column-numbers to their void value.

    Returns a ParseGefError on duplicates and ill header formats
    Does not guarantee that all columns have a void value.

    :param headers:(Union[Dict,str]) Gef headers
    :return: (Dict[int, float]) Mapping of column-numbers to their void value.
    """
    voids_info: List[Tuple[int, float]] = []
    if isinstance(headers, dict):
        # Return a list of all the second float values of all COLUMN_VOID lines
        if "COLUMNVOID" in headers:
            try:
                voids_info = list(
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
    elif "bore" in proc_code and "borehole" not in proc_code:
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


def parse_soil_code(s: str) -> str:
    """
    Function to parse the soil code.

    :param s: (str) String with the soil code.
    :return: Soil code.
    """
    return s.replace("'", "")


def parse_soil_name(s: str) -> str:
    """
    Function to parse the soil name.

    NOTE: interpretation of the soil code to NEN-EN-ISO 14688-1:2019+NEN 8990:2020

    :param s: (str) String with the soil code.
    :return: Soil name.
    """
    return MAPPING_PARAMETERS.dino_to_bro(s)


def parse_add_info(headers):
    """
    Function to parse all the additional informations.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :return: (str) Additional informations.
    """
    dict_add_info = MAPPING_PARAMETERS.code_to_text()

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
