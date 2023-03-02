from __future__ import annotations

from functools import lru_cache


class _MappingParameters:
    @lru_cache(1)
    def code_to_text(self) -> dict[str, str]:
        return {
            "DO": "dark ",
            "LI": "light ",
            "TBL": "blue-",
            "TBR": "brown-",
            "TGE": "yellow-",
            "TGN": "green-",
            "TGR": "gray-",
            "TOL": "olive-",
            "TOR": "orange-",
            "TPA": "violet-",
            "TRO": "red-",
            "TWI": "white-",
            "TRZ": "pink-",
            "TZW": "black-",
            "BL": "blue ",
            "BR": "brown ",
            "GE": "yellow ",
            "GN": "green ",
            "GR": "gray ",
            "OL": "olive ",
            "OR": "orange ",
            "PA": "violet ",
            "RO": "red ",
            "WI": "white ",
            "RZ": "pink ",
            "ZW": "black ",
            "ZUF": "uiterst fijn ",
            "ZZF": "zeer fijn ",
            "ZMF": "matig fijn ",
            "ZMG": "matig grof ",
            "ZZG": "zeer grof ",
            "ZUG": "uiterst grof ",
            "SZK": "zeer kleine spreiding ",
            "SMK": "matig kleine spreiding|",
            "SMG": "matig grote spreiding ",
            "SZG": "zeer grote spreiding ",
            "STW": "tweetoppige spreiding ",
            "ZZH": "sterk hoekig ",
            "ZHK": "hoekig ",
            "ZMH": "matig hoekig ",
            "ZMA": "afgerond ",
            "ZSA": "sterk afgerond ",
            "GFN": "fijn grind ",
            "GMG": "matig grof grind ",
            "GZG": "zeer grof grind ",
            "FN1": "spoor fijn grind (<1%) ",
            "FN2": "weinig fijn grind (1-25%) ",
            "FN3": "veel fijn grind (25-50%) ",
            "FN4": "zeer veel fijn grind (50-75%) ",
            "FN5": "uiterst veel fijn grind (>75%) ",
            "MG1": "spoor matig grof grind (<1%) ",
            "MG2": "weinig matig grof grind (1-25%) ",
            "MG3": "veel matig grof grind (25-50%) ",
            "MG4": "zeer veel matig grof grind (50-75%) ",
            "MG5": "uiterst veel matig grof grind(>75%) ",
            "GG1": "spoor zeer grof grind (<1%) ",
            "GG2": "weinig zeer grof grind (1-25%) ",
            "GG3": "veel zeer grof grind (25-50%) ",
            "GG4": "zeer veel zeer grof grind (50-75%) ",
            "GG5": "uiterst veel zeer grof grind (>75%) ",
            "AV1": "zwak amorf ",
            "AV2": "matig amorf ",
            "AV3": "sterk amorf ",
            "BSV": "bosveen ",
            "HEV": "heideveen ",
            "MOV": "mosveen ",
            "RIV": "rietveen ",
            "SZV": "Scheuchzeriaveen ",
            "VMV": "veenmosveen ",
            "WOV": "wollegrasveen ",
            "ZEV": "zeggeveen ",
            "KZSL": "klei zeer slap ",
            "KSLA": "klei slap ",
            "KMSL": "klei matig slap ",
            "KMST": "klei stevig ",
            "KZST": "klei zeer stevig ",
            "KHRD": "klei hard ",
            "KZHR": "klei zeer hard ",
            "LZSL": "leem zeer slap ",
            "LSLA": "leem slap ",
            "LMSL": "leem matig slap ",
            "LMST": "leem matig stevig ",
            "LSTV": "leem stevig ",
            "LZST": "leem zeer stevig ",
            "LHRD": "leem hard ",
            "LZHR": "leem zeer hard ",
            "VZSL": "veen zeer slap ",
            "VSLA": "veen slap ",
            "VMSL": "veen matig slap ",
            "VMST": "veen matig stevig ",
            "VSTV": "stevig ",
            "LOS": "los gepakt ",
            "NOR": "normaal gepakt ",
            "VAS": "vast gepakt ",
            "VGZZ": "zeer zacht ",
            "VGZA": "zacht ",
            "VGMZ": "matig zacht ",
            "VGMH": "matig hard ",
            "VGHA": "hard ",
            "VGZH": "zeer hard ",
            "VGEH": "extreem hard ",
            "SCH0": "geen schelpmateriaal 0% ",
            "SCH1": "spoor schelpmateriaal <1% ",
            "SCH2": "weinig schelpmateriaal (1-10%) ",
            "SCH3": "veel schelpmateriaal (10-30%) ",
            "CA1": "kalkloos ",
            "CA2": "kalkarm ",
            "CA3": "kalkrijk ",
            "GC0": "geen glauconiet 0% ",
            "GC1": "spoor glauconiet <1% ",
            "GC2": "weinig glauconiet (1-10%) ",
            "GC3": "veel glauconiet (10-30%) ",
            "GC4": "zeer veel glauconiet(30-50%) ",
            "GC5": "uiterst veel glauconiet (>50%) ",
            "BST1": "spoor baksteen ",
            "BST2": "weinig baksteen ",
            "BST3": "veel baksteen ",
            "PUR1": "spoor puinresten ",
            "PUR2": "weinig puinresten ",
            "PUR3": "veel puinresten ",
            "SIN1": "spoor sintels ",
            "SIN2": "weinig sintels ",
            "SIN3": "veel sintels ",
            "STO1": "spoor stortsteen ",
            "STO2": "weinig stortsteen ",
            "STO3": "veel stortsteen ",
            "VUI1": "spoor vuilnis ",
            "VUI2": "weinig vuilnis ",
            "VUI3": "veel vuilnis ",
            "AF": "afval ",
            "AS": "asfalt ",
            "BE": "beton ",
            "BI": "bitumen ",
            "BT": "ballast ",
            "BST": "baksteen ",
            "GI": "gips ",
            "GA": "glas ",
            "HK": "houtskool ",
            "HU": "huisvuil ",
            "KA": "kalk ",
            "KG": "kolengruis ",
            "KO": "kolen ",
            "KT": "krijt ",
            "ME": "metaal ",
            "MI": "mijnsteen ",
            "OE": "oer ",
            "PL": "planten ",
            "PU": "puin ",
            "SI": "sintels ",
            "SL": "slakken ",
            "WO": "wortels ",
            "YZ": "ijzer ",
            "GL": "gley ",
            "RT": "roest ",
            "SE": "silex ",
            "BIO": "bioturbatie ",
            "DWO": "doorworteling ",
            "GCM": "cm-gelaagdheid ",
            "GDM": "dm-gelaagdheid ",
            "GDU": "dubbeltjes-gelaagdheid ",
            "GMM": "mm-gelaagdheid ",
            "GRG": "graafgangen ",
            "GSC": "scheve gelaagdheid ",
            "GSP": "spekkoek-gelaagdheid ",
            "HOM": "homogeen ",
            "GE1": "zwak gelaagd ",
            "GE2": "weinig gelaagd ",
            "GE3": "sterk gelaagd ",
            "GEX": "gelaagd ",
            "STGL": "met grindlagen ",
            "STKL": "met kleilagen ",
            "STLL": "met leemlagen ",
            "STSL": "met stenenlagen ",
            "STVL": "met veenlagen ",
            "STZL": "met zandlagen ",
            "STBR": "met bruinkoollagen ",
            "STDE": "met detrituslagen ",
            "STGY": "met gyttjalagen ",
            "STSC": "met schelpenlagen ",
            "ANT": "Antropogeen ",
            "BOO": "Boomse klei ",
            "DEZ": "dekzand ",
            "KEL": "keileem ",
            "LSS": "loess ",
            "POK": "potklei ",
            "WAR": "warven ",
            "DR": "Formatie van Drente ",
            "EC": "Formatie van Echteld ",
            "KR": "Formatie van Kreftenheye ",
            "NA": "Formatie van Naaldwijk ",
            "NI": "Formatie van Nieuwkoop ",
            "TW": "Formatie van Twente ",
            "WA": "Formatie van Waalre ",
        }

    @lru_cache(1)
    def dino_to_bro(self, s: str) -> str:
        # TODO update soil_code from NEN 5104 -> NEN-EN-ISO 14688-1:2019+NEN 8990:2020
        main = s[0]

        if len(s) == 2:
            try:
                sub = s[1]
                subf = 0
            except ValueError:
                return "niet gedefinieerd"
        elif len(s) > 2:
            try:
                sub = s[1]
                subf = int(s[2])
            except ValueError:
                return "niet gedefinieerd"
        else:
            if main == "G":
                return "siltigGrind"
            if main == "Z":
                return "zand"
            if main == "L":
                return "zwakZandigSilt"
            if main == "K":
                return "klei"
            if main == "V":
                return "veen"

        # sand
        if main == "Z":
            if sub in "sk":
                if subf > 2:
                    return "sterkZandigSilt"
                else:
                    return "zwakZandigSilt"
            elif sub == "v":
                return "sterkZandigVeen"
            elif sub == "g":
                return "zand"
        # clay
        elif main == "K":
            if sub in "sz":
                if subf > 2:
                    return "sterkZandigeKlei"
                else:
                    return "zwakZandigeKlei"
            elif sub == "g":
                return "sterkZandigeKlei"
            elif sub == "v":
                return "organischKlei"
        elif main == "V":
            return "veen"
        elif main == "L":
            if sub == "z":
                if subf > 2:
                    return "sterkZandigSilt"
                else:
                    return "zwakZandigSilt"
            elif sub == "k":
                if subf > 2:
                    return "zwakZandigeKlei"
                else:
                    return "sterkZandigKlei"
            elif sub == "v":
                if subf > 1:
                    return "zwakZandigVeen"
                else:
                    return "sterkZandigVeen"
            elif sub == "g":
                return "zwakZandigSiltMetGrind"
        elif main == "G":
            if sub in "sz":
                if subf < 2:
                    return "zwakZandigGrind"
                else:
                    return "siltigGrind"
            else:
                return "grind"

        return "niet gedefinieerd"


MAPPING_PARAMETERS = _MappingParameters()
