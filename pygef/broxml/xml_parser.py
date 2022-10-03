from __future__ import annotations

import io
from pathlib import Path
from typing import TypeVar, cast, Any, Callable
from lxml import etree

from pygef.cpt import CPTData
from pygef.bore import BoreData

T = TypeVar("T", CPTData, BoreData)


def read_xml(
    file: io.BytesIO | Path | str,
    constructor: Callable[..., T],
    resolver_schema: dict[str, Any],
) -> list[T]:
    tree = etree.parse(file)

    root = tree.getroot()
    namespaces = root.nsmap
    dd = root.find("dispatchDocument", namespaces)

    out: list[T] = []

    cpts = dd.findall("./*")
    for cpt in cpts:

        # kwargs of attribute: value
        resolved = dict()

        for (atrib, d) in resolver_schema.items():
            d = cast(dict[str, Any], d)
            el = cpt.find(d["xpath"], cpt.nsmap)

            if el is not None:
                if "resolver" in d:
                    func = d["resolver"]

                    if "el-attr" in d:
                        el = getattr(el, d["el-attr"])

                    # ignore mypy error as it thinks we get a
                    # str from the dict
                    resolved[atrib] = func(el, namespaces=namespaces)
                else:
                    resolved[atrib] = el.text
            else:
                resolved[atrib] = None
        out.append(constructor(**resolved))

    return out
