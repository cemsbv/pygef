from __future__ import annotations

import io
from pathlib import Path
from .cpt import CPTXml

from lxml import etree


def read_cpt(file: io.BytesIO | Path | str) -> list[CPTXml]:
    tree = etree.parse(file)

    root = tree.getroot()
    namespaces = root.nsmap
    dd = root.find("dispatchDocument", namespaces)

    out: list[CPTXml] = []

    cpts = dd.findall("./*")
    for cpt in cpts:
        bro_id: str = cpt.find("brocom:broId", cpt.nsmap).text
        research_report_date: str = cpt.find(
            "./researchReportDate/brocom:date", cpt.nsmap
        ).text

        out.append(CPTXml(bro_id=bro_id, research_report_date=research_report_date))

    return out
