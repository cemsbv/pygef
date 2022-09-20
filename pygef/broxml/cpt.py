from __future__ import annotations
from dataclasses import dataclass
import polars as pl
from enum import Enum


class QualityClass(Enum):
    Unknown = 0
    Class1 = 1
    Class2 = 2


@dataclass
class Location:
    srs_name: str
    x: float
    y: float


@dataclass
class CPTXml:
    # dispatch_document cpt
    bro_id: str | None
    research_report_date: str | None
    cpt_standard: str | None
    standardized_location: Location | None
    # conepenetrometersurvey
    dissipationtest_performed: bool | None
    quality_class: QualityClass
    predrilled_depth: float
    final_depth: float
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

    data: pl.DataFrame

    @property
    def columns(self) -> list[str]:
        return self.data.columns
