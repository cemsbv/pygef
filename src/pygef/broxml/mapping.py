from __future__ import annotations

from functools import lru_cache

import polars as pl


class _MappingParameters:
    @lru_cache(1)
    def dist_table(self) -> pl.DataFrame:
        mapping = self.bro_to_dict()
        return pl.DataFrame(
            {
                "geotechnicalSoilName": list(mapping.keys()),
                "soilDistribution": list(mapping.values()),
            }
        ).sort("geotechnicalSoilName")

    @lru_cache(1)
    def bro_to_dict(self) -> dict[str, pl.Series]:
        # SoilNameISO14688
        # > https://publiek.broservices.nl/bro/refcodes/v1/codes?domain=urn%3Abro%3Abhrgt%3AGeotechnicalSoilName&version=latest
        # SoilNameNEN5104
        # > https://publiek.broservices.nl/bro/refcodes/v1/codes?domain=urn%3Abro%3Abhrgt%3ASoilNameNEN5104&version=latest
        # ["rocks", "gravel", "sand", "silt, "clay", "peat"]
        BRO_TO_DIST = {
            "blokken": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # SoilNameNEN5104
            "keien": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "keienNietGespecificeerd": [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],  # SoilNameNEN5104
            "keienMetGrind": [0.7, 0.3, 0.0, 0.0, 0.0, 0.0],
            "keienMetZand": [0.7, 0.0, 0.3, 0.0, 0.0, 0.0],
            "keienMetSilt": [0.7, 0.0, 0.0, 0.3, 0.0, 0.0],
            "keienMetKlei": [0.7, 0.0, 0.0, 0.0, 0.3, 0.0],
            "keitjes": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "keitjesNietGespecificeerd": [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],  # SoilNameNEN5104
            "keitjesMetGrind": [0.7, 0.3, 0.0, 0.0, 0.0, 0.0],
            "keitjesMetZand": [0.7, 0.0, 0.3, 0.0, 0.0, 0.0],
            "keitjesMetSilt": [0.7, 0.0, 0.0, 0.3, 0.0, 0.0],
            "keitjesMetKlei": [0.7, 0.0, 0.0, 0.0, 0.3, 0.0],
            "grind": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            "grindMetKeien": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
            "grindMetKeitjes": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
            "zwakZandigGrind": [0.0, 0.8, 0.2, 0.0, 0.0, 0.0],
            "matigZandigGrind": [0.0, 0.7, 0.3, 0.0, 0.0, 0.0],  # SoilNameNEN5104
            "sterkZandigGrind": [0.0, 0.6, 0.4, 0.0, 0.0, 0.0],
            "uiterstZandigGrind": [0.0, 0.5, 0.5, 0.0, 0.0, 0.0],  # SoilNameNEN5104
            "siltigGrind": [0.0, 0.7, 0.0, 0.3, 0.0, 0.0],
            "keiigGrind": [0.3, 0.7, 0.0, 0.0, 0.0, 0.0],
            "zand": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            "zandMetKeien": [0.3, 0.0, 0.7, 0.0, 0.0, 0.0],
            "zandMetKeitjes": [0.3, 0.0, 0.7, 0.0, 0.0, 0.0],
            "zwakGrindigZand": [0.0, 0.2, 0.8, 0.0, 0.0, 0.0],
            "sterkGrindigZand": [0.0, 0.4, 0.6, 0.0, 0.0, 0.0],
            "siltigZand": [0.0, 0.0, 0.7, 0.3, 0.0, 0.0],
            "zwakSiltigZand": [0.0, 0.0, 0.8, 0.2, 0.0, 0.0],  # SoilNameNEN5104
            "matigSiltigZand": [0.0, 0.0, 0.7, 0.3, 0.0, 0.0],  # SoilNameNEN5104
            "sterkSiltigZand": [0.0, 0.0, 0.6, 0.4, 0.0, 0.0],  # SoilNameNEN5104
            "uiterstSiltigZand": [0.0, 0.0, 0.5, 0.5, 0.0, 0.0],  # SoilNameNEN5104
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
            "matigZandigeKlei": [0.0, 0.0, 0.3, 0.0, 0.7, 0.0],  # SoilNameNEN5104
            "zwakZandigeKleiMetGrind": [0.0, 0.1, 0.1, 0.0, 0.8, 0.0],
            "sterkZandigeKlei": [0.0, 0.0, 0.4, 0.0, 0.6, 0.0],
            "sterkZandigeKleiMetGrind": [0.0, 0.2, 0.2, 0.0, 0.6, 0.0],
            "organischKlei": [0.0, 0.0, 0.0, 0.0, 0.6, 0.4],
            "matigSiltigeKlei": [0.0, 0.0, 0.0, 0.2, 0.8, 0.0],  # SoilNameNEN5104
            "uiterstSiltigeKlei": [0.0, 0.0, 0.0, 0.5, 0.5, 0.0],  # SoilNameNEN5104
            "sterkSiltigeKlei": [0.0, 0.0, 0.0, 0.3, 0.7, 0.0],  # SoilNameNEN5104
            "zwakSiltigeKlei": [0.0, 0.0, 0.0, 0.1, 0.9, 0.0],  # SoilNameNEN5104
            "sterkZandigeLeem": [0.1, 0.25, 0.1, 0.45, 0.05, 0.05],  # SoilNameNEN5104
            "zwakZandigeLeem": [0.1, 0.15, 0.1, 0.45, 0.1, 0.1],  # SoilNameNEN5104
            "detritus": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "detritusNietGespecificeerd": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],  # SoilNameNEN5104
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
            "kleiigVeen": [0.0, 0.0, 0.0, 0.0, 0.2, 0.8],
            "zwakKleiigVeen": [0.0, 0.0, 0.0, 0.0, 0.1, 0.9],  # SoilNameNEN5104
            "sterkKleiigVeen": [0.0, 0.0, 0.0, 0.0, 0.3, 0.7],  # SoilNameNEN5104
            "mineraalarmVeen": [0.0, 0.0, 0.0, 0.2, 0.0, 0.8],  # SoilNameNEN5104
            "gyttja": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "gyttjaNietGespecificeerd": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],  # SoilNameNEN5104
            "dy": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # SoilNameNEN5104
            "bruinkool": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "bruinkoolNietGespecificeerd": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],  # SoilNameNEN5104
            "niet gedefinieerd": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "unknown": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        }
        return {k: pl.Series(v) for k, v in BRO_TO_DIST.items()}


MAPPING_PARAMETERS = _MappingParameters()
