from __future__ import annotations

import copy
import pprint
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import polars as pl

from pygef.broxml.mapping import MAPPING_PARAMETERS
from pygef.common import Location, depth_to_offset


@dataclass(frozen=True)
class BoreData:
    """
    The Bore dataclass holds the information from the BHRgt object.

    Attributes:
        bro_id (str | None): BRO ID of the BHRgt.
        alias  (str | None): Alias of the CPT.
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
            columns:

                - upperBoundary [m]
                - lowerBoundary [m]
                - geotechnicalSoilName
                - soilDistribution

            optional columns:

                - upperBoundaryOffset [m wrt offset]
                    see delivered_vertical_position_datum for offset
                - lowerBoundaryOffset [m wrt offset]
                    see delivered_vertical_position_datum for offset
                - lutumPercentage [%]
                - siltPercentage [%]
                - sandPercentage [%]
                - gravelPercentage [%]
                - organicMatterPercentage [%]
                - sandMedianClass
                - gravelMedianClass
                - geotechnicalSoilCode
                - color
                - remarks
                - dispersedInhomogeneity
                - organicMatterContentClass
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

    alias: str | None = field(default=None)

    def __post_init__(self):
        # post-processing of the data
        tbl = MAPPING_PARAMETERS.dist_table().lazy()
        df = (
            self.data.lazy()
            .pipe(
                _calculate_depth_with_respect_to_offset,
                self.delivered_vertical_position_offset,
            )
            .join(tbl, on="geotechnicalSoilName", how="left")
            .sort("upperBoundary", descending=False, nulls_last=False)
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
    def final_sample_depth_offset(self) -> float | None:
        """final sample depth wrt offset"""
        return depth_to_offset(
            self.final_sample_depth, offset=self.delivered_vertical_position_offset
        )

    @property
    def final_depth_offset(self) -> float | None:
        """final depth wrt offset"""
        return depth_to_offset(
            self.final_depth_offset, offset=self.delivered_vertical_position_offset
        )

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


def _calculate_depth_with_respect_to_offset(
    lf: pl.LazyFrame, offset: float | None
) -> pl.LazyFrame:
    """post-process function for CPT data creates a new column with the elevation with respect to offset"""
    if offset is None:
        return lf

    return lf.with_columns(
        (offset - pl.col("upperBoundary")).alias("upperBoundaryOffset"),
        (offset - pl.col("lowerBoundary")).alias("lowerBoundaryOffset"),
    )
