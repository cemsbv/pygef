from __future__ import annotations
from dataclasses import dataclass

import io
from pathlib import Path


@dataclass
class CPTXml:
    bro_id: str | None
    research_report_date: str | None
