from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from pygef.broxml import Location
import polars as pl


@dataclass
class BoreData:
    research_report_date: date
    description_procedure: str
    delivered_location: Location
    delivered_vertical_position_offset: float | None
    delivered_vertical_position_datum: str
    delivered_vertical_position_reference_point: str
    bore_rock_reached: bool
    final_bore_depth: float
    final_sample_depth: float | None
    bore_hole_completed: bool
    data: pl.DataFrame
