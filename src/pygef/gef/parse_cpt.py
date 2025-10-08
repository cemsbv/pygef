from __future__ import annotations

from typing import List

import numpy as np
import polars as pl

from pygef.gef import utils
from pygef.gef.gef import _Gef, parse_all_columns_info, replace_column_void
from pygef.gef.mapping import MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT


class _GefCpt(_Gef):
    def __init__(self, path=None, string=None, replace_column_voids=True):
        """
        Parser of the cpt file.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.
        replace_column_voids: boolean
            If True (default) column voids will be replaced either by interpolated
            value, or by Null value. If False, then column void data is left unchanged.
        """
        super().__init__(path=path, string=string)
        if not self.type == "cpt":
            raise ValueError(
                "The selected gef file is not a cpt. "
                "Check the REPORTCODE or the PROCEDURECODE."
            )
        self.project_id = utils.parse_project_type(self._headers, "cpt")
        self.cone_id = utils.parse_cone_id(self._headers)

        self.cpt_class = utils.parse_cpt_class(self._headers)

        self.nom_surface_area_cone_tip = utils.parse_measurement_var_as_float(
            self._headers, 1
        )
        self.nom_surface_area_friction_element = utils.parse_measurement_var_as_float(
            self._headers, 2
        )
        self.net_surface_area_quotient_of_the_cone_tip = (
            utils.parse_measurement_var_as_float(self._headers, 3)
        )
        self.net_surface_area_quotient_of_the_friction_casing = (
            utils.parse_measurement_var_as_float(self._headers, 4)
        )
        self.distance_between_cone_and_centre_of_friction_casing = (
            utils.parse_measurement_var_as_float(self._headers, 5)
        )
        self.friction_present = utils.parse_measurement_var_as_float(self._headers, 6)
        self.ppt_u1_present = utils.parse_measurement_var_as_float(self._headers, 7)
        self.ppt_u2_present = utils.parse_measurement_var_as_float(self._headers, 8)
        self.ppt_u3_present = utils.parse_measurement_var_as_float(self._headers, 9)
        self.inclination_measurement_present = utils.parse_measurement_var_as_float(
            self._headers, 10
        )
        self.use_of_back_flow_compensator = utils.parse_measurement_var_as_float(
            self._headers, 11
        )
        self.type_of_cone_penetration_test = utils.parse_measurement_var_as_float(
            self._headers, 12
        )
        self.pre_excavated_depth = utils.parse_measurement_var_as_float(
            self._headers, 13
        )
        self.groundwater_level = utils.parse_measurement_var_as_float(self._headers, 14)
        self.water_depth_offshore_activities = utils.parse_measurement_var_as_float(
            self._headers, 15
        )
        self.end_depth_of_penetration_test = utils.parse_measurement_var_as_float(
            self._headers, 16
        )
        self.stop_criteria = utils.parse_measurement_var_as_float(self._headers, 17)
        self.zero_measurement_cone_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 20)
        )
        self.zero_measurement_cone_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 21)
        )
        self.zero_measurement_friction_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 22)
        )
        self.zero_measurement_friction_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 23)
        )
        self.zero_measurement_ppt_u1_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 24)
        )
        self.zero_measurement_ppt_u1_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 25)
        )
        self.zero_measurement_ppt_u2_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 26)
        )
        self.zero_measurement_ppt_u2_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 27)
        )
        self.zero_measurement_ppt_u3_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 28)
        )
        self.zero_measurement_ppt_u3_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 29)
        )
        self.zero_measurement_inclination_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 30)
        )
        self.zero_measurement_inclination_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 31)
        )
        self.zero_measurement_inclination_ns_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 32)
        )
        self.zero_measurement_inclination_ns_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 33)
        )
        self.zero_measurement_inclination_ew_before_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 34)
        )
        self.zero_measurement_inclination_ew_after_penetration_test = (
            utils.parse_measurement_var_as_float(self._headers, 35)
        )
        self.mileage = utils.parse_measurement_var_as_float(self._headers, 41)

        self.columns_info = self.ColumnsInfo(
            *parse_all_columns_info(self._headers, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT),
            col_separator=utils.get_column_separator(self._headers),
            rec_separator=utils.get_record_separator(self._headers),
            column_voids=utils.parse_column_void(self._headers),
        )

        lazy_df = self.parse_data(
            self._data,
            self.columns_info.col_separator,
            self.columns_info.rec_separator,
            self.columns_info.descriptions,
        ).lazy()

        if replace_column_voids:
            lazy_df = lazy_df.pipe(
                replace_column_void, self.columns_info.description_to_void_mapping
            )

        self.df = (
            lazy_df
            # Remove any rows with null values
            .drop_nulls()
            .with_columns(pl.col("penetrationLength").abs().alias("penetrationLength"))
            .pipe(correct_pre_excavated_depth, self.pre_excavated_depth)
            .pipe(correct_depth_with_inclination, self.columns_info.descriptions)
            .collect()
        )


def correct_pre_excavated_depth(lf: pl.LazyFrame, pre_excavated_depth) -> pl.LazyFrame:
    if pre_excavated_depth is not None and pre_excavated_depth > 0:
        return lf.filter(pl.col("penetrationLength") >= pre_excavated_depth)
    return lf


def correct_depth_with_inclination(
    lf: pl.LazyFrame, columns: List[str]
) -> pl.LazyFrame:
    """
    Return the expression needed to correct depth
    """
    if "depth" in columns:
        return lf.with_columns(pl.col("depth").abs().alias("depth"))
    elif "inclinationResultant" in columns:
        # every different in depth needs to be corrected with the angle
        correction_factor = np.cos(
            np.radians(pl.col("inclinationResultant").cast(pl.Float32).fill_null(0))
        )

        delta_height = pl.col("penetrationLength").diff()
        corrected_depth = correction_factor * delta_height

        return lf.with_columns(
            # this sets the first as depth
            pl.when(pl.arange(0, corrected_depth.len()) == 0)
            .then(pl.col("penetrationLength"))
            .otherwise(corrected_depth)
            .cum_sum()
            .alias("depth")
        )

    return lf
