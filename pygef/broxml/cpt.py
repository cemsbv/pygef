from __future__ import annotations
from dataclasses import dataclass
import polars as pl


@dataclass
class Location:
    srs_name: str
    x: float
    y: float


@dataclass
class CPTXml:
    bro_id: str | None
    research_report_date: str | None
    cpt_standard: str | None
    standardized_location: Location | None
    dissipationtest_performed: bool | None
    quality_class: str | None
    data: pl.DataFrame | None
