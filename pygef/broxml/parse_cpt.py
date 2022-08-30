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

    # maps keyword argument to:
    # xpath: query passed to elementree.find
    # resolver: A function that converts the string to the proper datatype
    #           Fn(str) -> Any
    attribs = {
        "bro_id": {"xpath": "brocom:broId"},
        "research_report_date": {"xpath": "./researchReportDate/brocom:date"},
        "cpt_standard": {"xpath": "cptStandard"},
    }

    cpts = dd.findall("./*")
    for cpt in cpts:

        # kwargs of attribute: value
        resolved = dict()

        for (atrib, d) in attribs.items():
            el = cpt.find(d["xpath"], cpt.nsmap)

            if el is not None:
                if "resolver" in d:
                    func = d["resolver"]
                    # ignore mypy error as it thinks we get a
                    # str from the dict
                    resolved[atrib] = func(el.text)  # type: ignore
                else:
                    resolved[atrib] = el.text

        out.append(CPTXml(**resolved))

    return out
