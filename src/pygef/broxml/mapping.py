from __future__ import annotations

from functools import lru_cache

import polars as pl


class _MappingParameters:
    @lru_cache(1)
    def dist_table(self) -> pl.DataFrame:
        mapping = self.bro_to_dict()
        return pl.DataFrame(
            {
                "geotechnical_soil_name": list(mapping.keys()),
                "soil_dist": list(mapping.values()),
            }
        ).sort("geotechnical_soil_name")

    @lru_cache(1)
    def bro_to_dict(self) -> dict[str, pl.Series]:
        # ["rocks", "gravel", "sand", "silt, "clay", "peat"]
        BRO_TO_DIST = {
            "keien": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "keienMetGrind": [0.7, 0.3, 0.0, 0.0, 0.0, 0.0],
            "keienMetZand": [0.7, 0.0, 0.3, 0.0, 0.0, 0.0],
            "keienMetSilt": [0.7, 0.0, 0.0, 0.3, 0.0, 0.0],
            "keienMetKlei": [0.7, 0.0, 0.0, 0.0, 0.3, 0.0],
            "keitjes": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "keitjesMetGrind": [0.7, 0.3, 0.0, 0.0, 0.0, 0.0],
            "keitjesMetZand": [0.7, 0.0, 0.3, 0.0, 0.0, 0.0],
            "keitjesMetSilt": [0.7, 0.0, 0.0, 0.3, 0.0, 0.0],
            "keitjesMetKlei": [0.7, 0.0, 0.0, 0.0, 0.3, 0.0],
            "grind": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            "grindMetKeien": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
            "grindMetKeitjes": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
            "zwakZandigGrid": [0.0, 0.8, 0.2, 0.0, 0.0, 0.0],
            "sterkZandigGrid": [0.0, 0.6, 0.4, 0.0, 0.0, 0.0],
            "siltigGrind": [0.0, 0.7, 0.0, 0.3, 0.0, 0.0],
            "keiigGrind": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
            "zand": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            "zandMetKeien": [0.3, 0.0, 0.7, 0.0, 0.0, 0.0],
            "zandMetKeitjes": [0.3, 0.0, 0.7, 0.0, 0.0, 0.0],
            "zwakGrindigZand": [0.2, 0.0, 0.8, 0.0, 0.0, 0.0],
            "sterkGrindigZand": [0.4, 0.0, 0.6, 0.0, 0.0, 0.0],
            "siltigZand": [0.0, 0.0, 0.7, 0.3, 0.0, 0.0],
            "siltigZandMetGrind": [0.0, 0.15, 0.7, 0.15, 0.0, 0.0],
            "kleiigZand": [0.0, 0.0, 0.7, 0.0, 0.3, 0.0],
            "kleiigZandMetGrind": [0.0, 0.15, 0.7, 0.0, 0.15, 0.0],
            "silt": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "siltMetKeien": [0.3, 0.0, 0.0, 0.7, 0.0, 0.0],
            "siltMetKeitjes": [0.3, 0.0, 0.0, 0.7, 0.0, 0.0],
            "zwakGrindigSilt": [0.0, 0.2, 0.0, 0.8, 0.0, 0.0],
            "sterkGrindigSilt": [0.0, 0.4, 0.0, 0.6, 0.0, 0.0],
            "zwakZandigSilt": [0.0, 0.0, 0.2, 0.8, 0.0, 0.0],
            "zwakZandigSiltMetGrind": [0.0, 0.1, 0.1, 0.8, 0.0, 0.0],
            "sterkZandigSilt": [0.0, 0.0, 0.4, 0.6, 0.0, 0.0],
            "sterkZandigSiltMetGrind": [0.0, 0.2, 0.2, 0.6, 0.0, 0.0],
            "klei": [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "kleiMetKeien": [0.3, 0.0, 0.0, 0.0, 0.7, 0.0],
            "kleiMetKeitjes": [0.3, 0.0, 0.0, 0.0, 0.7, 0.0],
            "zwakGrindigeKlei": [0.0, 0.2, 0.0, 0.0, 0.8, 0.0],
            "sterkGrindigeKlei": [0.0, 0.4, 0.0, 0.0, 0.6, 0.0],
            "zwakZandigeKlei": [0.0, 0.0, 0.2, 0.0, 0.8, 0.0],
            "zwakZandigeKleiMetGrind": [0.0, 0.1, 0.1, 0.0, 0.8, 0.0],
            "sterkZandigeKlei": [0.0, 0.0, 0.4, 0.0, 0.6, 0.0],
            "sterkZandigeKleiMetGrind": [0.0, 0.2, 0.2, 0.0, 0.6, 0.0],
            "organischKlei": [0.0, 0.0, 0.0, 0.0, 0.6, 0.4],
            "detritus": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "zwakZandigeDetritus": [0.0, 0.0, 0.2, 0.0, 0.0, 0.8],
            "sterkZandigeDetritus": [0.0, 0.0, 0.4, 0.0, 0.0, 0.6],
            "siltigeDetritus": [0.0, 0.0, 0.0, 0.2, 0.0, 0.8],
            "kleiigeDetritus": [0.0, 0.0, 0.0, 0.0, 0.2, 0.8],
            "humus": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "zwakZandigeHumus": [0.0, 0.0, 0.2, 0.0, 0.0, 0.8],
            "sterkZandigeHumus": [0.0, 0.0, 0.4, 0.0, 0.0, 0.6],
            "siltigeHumus": [0.0, 0.0, 0.0, 0.2, 0.0, 0.8],
            "kleiigeHumus": [0.0, 0.0, 0.0, 0.0, 0.2, 0.8],
            "veen": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "zwakZandigVeen": [0.0, 0.0, 0.2, 0.0, 0.0, 0.8],
            "sterkZandigVeen": [0.0, 0.0, 0.4, 0.0, 0.0, 0.6],
            "siltigVeen": [0.0, 0.0, 0.0, 0.2, 0.0, 0.8],
            "kleiigVeen": [0.0, 0.0, 0.0, 0.2, 0.0, 0.8],
            "gyttja": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "bruinkool": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "niet gedefinieerd": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        }
        return {k: pl.Series(v) for k, v in BRO_TO_DIST.items()}


MAPPING_PARAMETERS = _MappingParameters()
