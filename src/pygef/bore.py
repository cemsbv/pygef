from __future__ import annotations

import copy
import pprint
from dataclasses import dataclass
from datetime import date
from typing import Any

import polars as pl

from pygef.common import Location


@dataclass
class BoreData:
    """
    The Bore dataclass holds the information from the BHRgt object.

    Attributes:
        bro_id (str | None): BRO ID of the BHRgt.
        research_report_date (date): research report date
        delivered_location (Location): delivered location in EPSG:28992 - RD new
        groundwater_level (float | None): groundwater level
        standardized_location (Location | None): standardized location in EPSG:4326 - WGS 84
        delivered_vertical_position_offset (float | None): delivered vertical position offset
        delivered_vertical_position_datum (str): research delivered vertical position datum
        delivered_vertical_position_reference_point (str): delivered vertical position reference point
        bore_rock_reached (bool): bore rock reached
        final_bore_depth (float): final bore depth
        data (pl.DataFrame): DataFrame
    """

    # dispatch_document bhrgt
    bro_id: str | None
    research_report_date: date
    description_procedure: str
    delivered_location: Location
    groundwater_level: float | None
    standardized_location: Location | None
    delivered_vertical_position_offset: float | None
    delivered_vertical_position_datum: str
    delivered_vertical_position_reference_point: str
    bore_rock_reached: bool
    final_bore_depth: float
    final_sample_depth: float | None
    bore_hole_completed: bool
    data: pl.DataFrame

    @property
    def columns(self) -> list[str]:
        return self.data.columns

    def __str__(self):
        return f"BoreData: {self.display_attributes()}"

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
