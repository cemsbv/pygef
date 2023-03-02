from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

from lxml import etree

from pygef.bore import BoreData
from pygef.cpt import CPTData

T = TypeVar("T", CPTData, BoreData)


def read_xml(
    root: etree.Element,
    constructor: Callable[..., T],
    resolver_schema: dict[str, Any],
    payload_root: str,
) -> list[T]:
    namespaces = root.nsmap
    dd = root.find(payload_root, namespaces)

    out: list[T] = []

    payloads = dd.findall("./*")
    for payload in payloads:
        # kwargs of attribute: value
        resolved = dict()

        for atrib, d in resolver_schema.items():
            d = cast(dict[str, Any], d)
            el = payload.find(d["xpath"], payload.nsmap)

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
