from __future__ import annotations

import copy
import pprint
from dataclasses import dataclass, field
from datetime import date
from typing import Any, List

import polars as pl

from pygef.common import Location, VerticalDatumClass, depth_to_offset


@dataclass(frozen=True)
class CPTData:
    """
    The CPT dataclass holds the information from the CPT object.

    Attributes:
        bro_id (str | None): BRO ID of the CPT.
        alias  (str | None): Alias of the CPT.
        research_report_date (date): research report date
        delivered_location (Location): delivered location in `EPSG:28992 - RD new`
        standardized_location (Location | None): standardized location in `EPSG:4326 - WGS 84`
        delivered_vertical_position_offset (float | None): delivered vertical position offset
        delivered_vertical_position_datum (str): research delivered vertical position datum
        delivered_vertical_position_reference_point (str): delivered vertical position reference point
        cpt_standard (str | None): cpt standard
        dissipationtest_performed (bool | None): dissipationtest performed
        quality_class (int | None): quality class. None if the value in the source file was invalid or missing.
        predrilled_depth (float): predrilled depth
        final_depth (float): final depth
        groundwater_level (float | None): groundwater level
        cpt_description (str): cpt description
        cpt_type (str): cpt type
        cone_surface_area (int): cone_surface_area
        cone_diameter (int | None): cone_diameter
        cone_surface_quotient (float | None): cone_surface_quotient
        cone_to_friction_sleeve_distance (int | None): cone_to_friction_sleeve_distance
        cone_to_friction_sleeve_surface_area (int | None): cone_to_friction_sleeve_surface_area
        cone_to_friction_sleeve_surface_quotient (float | None): cone_to_friction_sleeve_surface_quotient
        zlm_cone_resistance_before (float): zlm_cone_resistance_before
        zlm_cone_resistance_after (float): zlm_cone_resistance_after
        zlm_inclination_ew_before (int | None): zlm_inclination_ew_before
        zlm_inclination_ew_after (int | None): zlm_inclination_ew_after
        zlm_inclination_ns_before (int | None): zlm_inclination_ns_before
        zlm_inclination_ns_after (int | None): zlm_inclination_ns_after
        zlm_inclination_resultant_before (int | None): zlm_inclination_resultant_before
        zlm_inclination_resultant_after (int | None): zlm_inclination_resultant_after
        zlm_local_friction_before (float | None): zlm_local_friction_before
        zlm_local_friction_after (float | None): zlm_local_friction_after
        zlm_pore_pressure_u1_before (float | None): zlm_pore_pressure_u1_before
        zlm_pore_pressure_u2_before (float | None): zlm_pore_pressure_u2_before
        zlm_pore_pressure_u3_before (float | None): zlm_pore_pressure_u3_before
        zlm_pore_pressure_u1_after (float | None): zlm_pore_pressure_u1_after
        zlm_pore_pressure_u2_after (float | None): zlm_pore_pressure_u2_after
        zlm_pore_pressure_u3_after (float | None): zlm_pore_pressure_u3_after
        column_void_mapping (dict | None): column_void_mapping
        data (pl.DataFrame): DataFrame
            columns:

                - penetrationLength [m]
                - coneResistance [MPa]

            optional columns:

                - depthOffset [m wrt offset]
                    see delivered_vertical_position_datum for offset
                - depth [m]
                    penetrationLength corrected for inclination
                - correctedConeResistance [MPa]
                - netConeResistance [MPa]
                - coneResistanceRatio
                - localFriction [MPa]
                - frictionRatioComputed [%]
                - frictionRatio [%]
                - porePressureU1 [MPa]
                - porePressureU2 [MPa]
                - porePressureU3 [MPa]
                - inclinationResultant [degrees]
                - inclinationNS [degrees]
                - inclinationEW [degrees]
                - elapsedTime [seconds]
                - poreRatio [MPa]
                - soilDensity
                - porePressure
                - verticalPorePressureTotal
                - verticalPorePressureEffective
                - temperature [degrees celsius]
                - inclinationX [degrees]
                - inclinationY [degrees]
                - electricalConductivity [S/m]
                - magneticFieldStrengthX [nT]
                - magneticFieldStrengthY [nT]
                - magneticFieldStrengthZ [nT]
                - magneticFieldStrengthTotal [nT]
                - magneticInclination [degrees]
                - magneticDeclination [degrees]
    """

    # dispatch_document cpt
    bro_id: str | None
    research_report_date: date
    cpt_standard: str | None
    delivered_location: Location
    standardized_location: Location | None
    # conepenetrometersurvey
    dissipationtest_performed: bool | None
    quality_class: int | None
    predrilled_depth: float
    final_depth: float
    groundwater_level: float | None
    # conepenetrometer
    cpt_description: str
    cpt_type: str
    cone_surface_area: int
    cone_diameter: int | None
    cone_surface_quotient: float | None
    cone_to_friction_sleeve_distance: int | None
    cone_to_friction_sleeve_surface_area: int | None
    cone_to_friction_sleeve_surface_quotient: float | None
    # zero-load-measurement
    zlm_cone_resistance_before: float
    zlm_cone_resistance_after: float
    zlm_inclination_ew_before: int | None
    zlm_inclination_ew_after: int | None
    zlm_inclination_ns_before: int | None
    zlm_inclination_ns_after: int | None
    zlm_inclination_resultant_before: int | None
    zlm_inclination_resultant_after: int | None
    zlm_local_friction_before: float | None
    zlm_local_friction_after: float | None
    zlm_pore_pressure_u1_before: float | None
    zlm_pore_pressure_u2_before: float | None
    zlm_pore_pressure_u3_before: float | None
    zlm_pore_pressure_u1_after: float | None
    zlm_pore_pressure_u2_after: float | None
    zlm_pore_pressure_u3_after: float | None
    delivered_vertical_position_offset: float | None
    delivered_vertical_position_datum: VerticalDatumClass
    delivered_vertical_position_reference_point: str
    column_void_mapping: dict | None
    data: pl.DataFrame

    alias: str | None = field(default=None)

    def __post_init__(self):
        # post-processing of the data
        df = (
            self.data.lazy()
            .pipe(
                _calculate_depth_with_respect_to_offset,
                self.delivered_vertical_position_offset,
                self.data.columns,
            )
            .pipe(_calculate_friction_number, self.data.columns)
            .sort("penetrationLength", descending=False, nulls_last=False)
            .collect()
        )
        # bypass FrozenInstanceError
        object.__setattr__(self, "data", df)

    @property
    def columns(self) -> list[str]:
        """Columns names for the DataFrame"""
        return self.data.columns

    @property
    def groundwater_level_offset(self) -> float | None:
        """groundwater level wrt offset"""
        return depth_to_offset(
            self.groundwater_level, offset=self.delivered_vertical_position_offset
        )

    @property
    def predrilled_depth_offset(self) -> float | None:
        """predrilled depth wrt offset"""
        return depth_to_offset(
            self.predrilled_depth, offset=self.delivered_vertical_position_offset
        )

    @property
    def final_depth_offset(self) -> float | None:
        """final depth wrt offset"""
        return depth_to_offset(
            self.final_depth_offset, offset=self.delivered_vertical_position_offset
        )

    def __str__(self):
        return f"CPTData: {self.display_attributes()}"

    def attributes(self) -> dict[str, Any]:
        """
        Get the attributes
        """
        attribs = copy.copy(self.__dict__)
        attribs["data"] = attribs["data"].shape
        return attribs

    def display_attributes(self) -> str:
        """
        Get pretty formatted string representation of `CPTData.attributes``
        """
        return pprint.pformat(self.attributes())


def _calculate_friction_number(lf: pl.LazyFrame, columns: List[str]) -> pl.LazyFrame:
    """Post-process function for CPT data, creates a new column with the computed frictionRatio"""
    if "localFriction" in columns and "coneResistance" in columns:
        return lf.with_columns(
            (
                pl.col("localFriction")
                / pl.when(pl.col("coneResistance") == 0.0)
                .then(None)
                .otherwise(pl.col("coneResistance"))
                * 100.0
            ).alias("frictionRatioComputed")
        )
    return lf


def _calculate_depth_with_respect_to_offset(
    lf: pl.LazyFrame, offset: float | None, columns: List[str]
) -> pl.LazyFrame:
    """Post-process function for CPT data creates a new column with the elevation with respect to offset"""
    if offset is None:
        return lf
    yname = "depth" if "depth" in columns else "penetrationLength"
    return lf.with_columns((offset - pl.col(yname)).alias("depthOffset"))
