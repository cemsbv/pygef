from __future__ import annotations

import logging
import math
from typing import List

import polars as pl

from pygef.gef import utils
from pygef.gef.gef import _Gef, parse_all_columns_info, replace_column_void
from pygef.gef.mapping import MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT

logger = logging.getLogger(__name__)


def parse_removed_layers(
    headers: dict[str, list[list[str]]], predrilled_depth: float | None
) -> pl.DataFrame:
    """Read SPECIMENVAR fields without deriving unrecorded layer boundaries."""
    records: list[dict[str, int | float | str | None]] = []
    previous_top: float | None = None
    entries = headers.get("SPECIMENVAR", [])
    valid_depth = (
        predrilled_depth is not None
        and math.isfinite(predrilled_depth)
        and predrilled_depth > 0
    )
    if entries and not valid_depth:
        logger.warning(
            "SPECIMENVAR records have a missing or invalid predrilled depth: %r",
            predrilled_depth,
        )

    for entry in entries:
        fields: list[str] = []
        for value in entry:
            value = value.strip()
            if fields and fields[-1].endswith("\\"):
                fields[-1] = fields[-1][:-1] + ", " + value
            else:
                fields.append(value)

        if len(fields) < 4:
            logger.warning("Incomplete SPECIMENVAR record: %r", entry)

        record: dict[str, int | float | str | None] = {}
        if fields:
            try:
                number = int(fields[0])
                if not -(2**63) <= number < 2**63:
                    raise ValueError("outside Int64 range")
                record["sequence_number"] = number
            except ValueError:
                logger.warning("Invalid SPECIMENVAR sequence number: %r", fields[0])
                record["sequence_number"] = None
                record["sequence_number_raw"] = fields[0]

        if len(fields) > 1:
            try:
                upper = float(fields[1])
                if not math.isfinite(upper):
                    raise ValueError("not finite")
                record["upper_boundary"] = upper
            except ValueError:
                logger.warning("Invalid SPECIMENVAR upper boundary: %r", fields[1])
                record["upper_boundary"] = None
                record["upper_boundary_raw"] = fields[1]

        if len(fields) > 2:
            unit = fields[2]
            record["vertical_unit"] = unit
            if unit != "m":
                logger.warning("Unexpected SPECIMENVAR vertical unit: %r", unit)
        if len(fields) > 3:
            record["description"] = fields[3]
        for index, value in enumerate(fields[4:], start=1):
            record[f"extra_{index}"] = value
        if len(fields) > 4:
            logger.warning("Unknown extra SPECIMENVAR fields: %r", fields[4:])

        top = record.get("upper_boundary")
        if isinstance(top, float) and record.get("vertical_unit") == "m":
            if (
                top < 0
                or (previous_top is not None and top <= previous_top)
                or (
                    valid_depth
                    and predrilled_depth is not None
                    and top >= predrilled_depth
                )
            ):
                logger.warning(
                    "Inconsistent SPECIMENVAR upper boundary %s (previous: %s, "
                    "predrilled depth: %s)",
                    top,
                    previous_top,
                    predrilled_depth,
                )
            previous_top = top
        else:
            previous_top = None
        records.append(record)

    return pl.DataFrame(
        records,
        infer_schema_length=None,
        schema_overrides={
            "sequence_number": pl.Int64,
            "upper_boundary": pl.Float64,
            "vertical_unit": pl.String,
            "description": pl.String,
        },
    )


class _GefCpt(_Gef):
    def __init__(
        self,
        path=None,
        string=None,
        replace_column_voids=True,
        remove_pre_excavated_rows=True,
    ):
        """
        Parser of the cpt file.

        Parameters
        ----------
        path: str
            Path to the *.gef file.
        string: str
            String version of the *.gef file.
        :param replace_column_voids: boolean, default True.
            If True (default) column voids will be replaced either by interpolated
            value, or by Null value. If False, then column void data is left unchanged.
        :param remove_pre_excavated_rows: boolean, default True.
            How to handle pre-excavated row values. If true, drop rows above pre-excavated depth; else retain.
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
        self.replace_column_voids = replace_column_voids
        self.remove_pre_excavated_rows = remove_pre_excavated_rows

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
        self.removed_layers = parse_removed_layers(
            self._headers, self.pre_excavated_depth
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

        pipeline = (
            lazy_df
            # Remove any rows with null values
            .drop_nulls().with_columns(
                pl.col("penetrationLength").abs().alias("penetrationLength")
            )
        )

        if self.remove_pre_excavated_rows:
            pipeline = pipeline.pipe(
                correct_pre_excavated_depth, self.pre_excavated_depth
            )

        pipeline = pipeline.pipe(
            correct_depth_with_inclination, self.columns_info.descriptions
        )
        self.df = pipeline.collect()


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
        correction_factor = (
            pl.col("inclinationResultant").cast(pl.Float32).fill_null(0).radians().cos()
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
