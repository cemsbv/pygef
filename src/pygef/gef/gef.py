from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import polars as pl
from gef_file_to_map import gef_to_map

from pygef import exceptions
from pygef.gef import utils

logger = logging.getLogger(__name__)


class _Gef:
    """
    The gef parser is built following the conventional format described in:
    https://publicwiki.deltares.nl/download/attachments/102204318/GEF-CPT.pdf?version=1&modificationDate=1409732008000&api=v2
    """

    def __init__(self, path=None, string=None):
        """
        Base class of gef parser. It switches between the cpt or borehole parser.

        It takes as input either the path to the gef file or the gef file as string.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.

        """
        self.path = path
        self.df = None
        self.net_surface_area_quotient_of_the_cone_tip = None
        self.pre_excavated_depth = None

        if string is None:
            with open(path, encoding="utf-8", errors="ignore") as f:
                string = f.read()

        self.s = string

        # Use the Rust optimized header parser
        self._data, self._headers = gef_to_map(string)

        self.zid = utils.parse_zid_as_float(self._headers)
        self.height_system = utils.parse_height_system(self._headers)
        self.x = utils.parse_xid_as_float(self._headers)
        self.y = utils.parse_yid_as_float(self._headers)
        self.coordinate_system = utils.parse_coordinate_code(self._headers)
        self.file_date = utils.parse_file_date(self._headers)
        self.test_id = utils.parse_test_id(self._headers)
        self.type = utils.parse_gef_type(self._headers)

    @dataclass
    class ColumnsInfo:
        """
        Dataclass carrying the #COLUMNINFO headers
        All inputs should be sorted on increasing column-number.
        """

        column_numbers: List[int]
        units: List[str]
        descriptions: List[str]
        column_quantities: List[int]
        col_separator: str
        rec_separator: str
        column_voids: Dict[int, float]
        default_void: float = float(-9999)

        def __post_init__(self):
            self.columns_number = len(self.column_numbers)
            self.column_voids = self.fill_default_column_voids()

            self.validate()

        @property
        def description_to_void_mapping(self) -> Dict[str, float]:
            return {
                desc: self.column_voids[num]
                for num, desc in zip(self.column_numbers, self.descriptions)
            }

        def fill_default_column_voids(self) -> Dict[int, float]:
            default_column_voids = {
                num: self.default_void for num in self.column_numbers
            }
            default_column_voids.update(self.column_voids)
            return default_column_voids

        def validate(self):
            if not len(self.column_numbers) == self.column_numbers[-1]:
                raise exceptions.ParseGefError(
                    "One or more #COLUMNINFO headers are missing: We counted "
                    f"{len(self.column_numbers)} #COLUMNINFO headers, but the highest column index "
                    f"is {self.column_numbers[-1]}"
                )

            if not self.column_numbers == list(range(1, self.column_numbers[-1] + 1)):
                raise exceptions.ParseGefError(
                    "One or more #COLUMNINFO headers have duplicates in the .gef file."
                )

    @staticmethod
    def parse_data(
        data_s: str,
        col_separator: str,
        rec_separator: str,
        column_names: List[str],
    ) -> pl.DataFrame:
        """
        Parses all data in the data string, returns a pl.DataFrame

        Parameters
        ----------
        data_s: str
            A string with the measurement data, in Delimiter-separated format.
        col_separator: str
            The character that separates the columns
        rec_separator: str
            The character that separates the records/rows
        column_names: List[str]
            List of column names

        Returns
        -------
        df: pl.DataFrame
            The DataFrame with measurement data
        """

        # Remove all horizontal whitespace characters around the column separator
        new_data = re.sub(
            rf"[^\S\r\n]*{re.escape(col_separator)}[^\S\r\n]*",
            col_separator,
            data_s,
        )

        # Split string by record separator into lines
        # Remove all whitespaces and column separators at the beginning and end of lines
        # Also remove the last trailing line
        regex = rf"[\s{re.escape(col_separator)}]+"
        new_data = "\n".join(
            re.sub(f"{regex}$", "", re.sub(f"^{regex}", "", line))
            for line in new_data.split(rec_separator)
        ).rstrip()

        return pl.read_csv(
            new_data.encode(),
            separator=col_separator,
            new_columns=column_names,
            has_header=False,
            columns=list(range(0, len(column_names))),
        )


def replace_column_void(
    lf: pl.LazyFrame, col_name_to_void_mapping: Dict[str, float]
) -> pl.LazyFrame:
    return (
        # Get all values matching column_void and change them to null
        # Interpolate all null values
        lf.select(
            [
                pl.when(pl.col(col) == pl.lit(col_name_to_void_mapping[col]))
                .then(None)
                .otherwise(pl.col(col))
                .interpolate()
                .name.keep()
                for col in lf.collect_schema().names()
            ]
        )
    )


def parse_all_columns_info_from_dict(
    headers: dict, quantity_dict: dict
) -> List[Tuple[int, str, str, int]]:
    """
    Function that parses and returns all COLUMNINFO header data from a dictionary.

    :param headers:(str) String of headers.
    :param quantity_dict: (dict) Dictionary that maps quanity numbers to descriptions
    :return: (List[Tuple[int, str, str, int]]) List of Tuples with the COLUMNINFO header values
    """

    columns_info: List[Tuple[int, str, str, int]] = []

    if "COLUMNINFO" in headers:
        # Loop over all headers to find the right number
        for values in headers["COLUMNINFO"]:
            try:
                col_number = int(values[0])
                quantity = int(values[3])
            except ValueError:
                raise exceptions.ParseGefError(
                    "One or more #COLUMNINFO headers do not have integers in the first "
                    "and/or last positions, which is required."
                )

            unit = values[1]
            description = utils.get_description(quantity, values[2], quantity_dict)

            columns_info.append((col_number, unit, description, quantity))

    return columns_info


def parse_all_columns_info_from_str(
    headers: str, quantity_dict: dict
) -> List[Tuple[int, str, str, int]]:
    """
    Function that parses and returns all COLUMNINFO header data from a string.

    :param headers:(dict) Dictionary of headers.
    :param quantity_dict: (dict) Dictionary that maps quanity numbers to descriptions
    :return: (List[Tuple[int, str, str, int]]) List of Tuples with the COLUMNINFO header values
    """

    columns_info: List[Tuple[int, str, str, int]] = []

    # Find all '#COLUMNINFO= **,' strings first
    for match in re.finditer(
        r"#COLUMNINFO\s*=\s*(\d+)\s*,{1}\s*([^,]+)\s*,{1}([^,]+)\s*,{1}\s*(\d+)",
        headers,
    ):
        column_number = utils.cast_string(int, match.group(1))
        column_quantity = utils.cast_string(int, match.group(4))

        custom_description = match.group(3).strip()
        description = utils.get_description(
            column_quantity, custom_description, quantity_dict
        )

        if column_number is not None and column_quantity is not None:
            columns_info.append(
                (
                    column_number,
                    match.group(2).strip(),
                    description,
                    column_quantity,
                )
            )

    return columns_info


def parse_all_columns_info(
    headers: Union[dict, str], quantity_dict: dict
) -> Tuple[List[int], List[str], List[str], List[int]]:
    """
    Function that parses and returns all COLUMNINFO header data from a string or dictionary.

    :param headers:(Union[Dict,str]) Dictionary or string of headers.
    :param quantity_dict: (dict) Dictionary that maps quanity numbers to descriptions
    :return: Tuple with lists of column_numbers, units, descriptions and column_quantities, sorted by column_numbers
    """

    if isinstance(headers, dict):
        columns_info = parse_all_columns_info_from_dict(headers, quantity_dict)

    else:
        columns_info = parse_all_columns_info_from_str(headers, quantity_dict)

    columns_info.sort()

    column_numbers = []
    units = []
    descriptions = []
    column_quantities = []

    for col in columns_info:
        column_numbers.append(col[0])
        units.append(col[1])
        descriptions.append(col[2])
        column_quantities.append(col[3])

    return column_numbers, units, descriptions, column_quantities
