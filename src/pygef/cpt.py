from __future__ import annotations

import copy
import pprint
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

import polars as pl

from pygef.common import Location


class QualityClass(Enum):
    Unknown = -1
    Class1 = 1
    Class2 = 2
    Class3 = 3
    Class4 = 4


@dataclass
class CPTData:
    """
    The CPT dataclass holds the information from the CPT object.

    Attributes:
        bro_id (str | None): BRO ID of the CPT.
        research_report_date (date): research report date
        delivered_location (Location): delivered location in `EPSG:28992 - RD new`
        standardized_location (Location | None): standardized location in `EPSG:4326 - WGS 84`
        delivered_vertical_position_offset (float | None): delivered vertical position offset
        delivered_vertical_position_datum (str): research delivered vertical position datum
        delivered_vertical_position_reference_point (str): delivered vertical position reference point
        cpt_standard (str | None): cpt standard
        dissipationtest_performed (bool | None): dissipationtest performed
        quality_class (QualityClass): quality class
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
        data (pl.DataFrame): DataFrame
    """

    # dispatch_document cpt
    bro_id: str | None
    research_report_date: date
    cpt_standard: str | None
    delivered_location: Location
    standardized_location: Location | None
    # conepenetrometersurvey
    dissipationtest_performed: bool | None
    quality_class: QualityClass
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
    delivered_vertical_position_datum: str
    delivered_vertical_position_reference_point: str

    data: pl.DataFrame

    @property
    def columns(self) -> list[str]:
        return self.data.columns

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
