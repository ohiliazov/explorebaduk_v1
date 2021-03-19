APP_NAME = "sgftree"
APP_VERSION = "1.0"
SGF_COORDINATES = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

HANDICAP_SGF_COORDINATES = [
    [],
    [],
    ["pd", "dp"],
    ["pd", "dp", "dd"],
    ["pd", "dp", "dd", "pp"],
    ["pd", "dp", "dd", "pp", "jj"],
    ["pd", "dp", "dd", "pp", "jd", "jp"],
    ["pd", "dp", "dd", "pp", "jd", "jp", "jj"],
    ["pd", "dp", "dd", "pp", "jd", "jp", "dj", "pj"],
    ["pd", "dp", "dd", "pp", "jd", "jp", "dj", "pj", "jj"],
]

HANDICAP_BOARD_COORDINATES = [
    [],
    [],
    [(15, 3), (3, 15)],
    [(15, 3), (3, 15), (3, 3)],
    [(15, 3), (3, 15), (3, 3), (15, 15)],
    [(15, 3), (3, 15), (3, 3), (15, 15), (9, 9)],
    [(15, 3), (3, 15), (3, 3), (15, 15), (3, 9), (15, 9)],
    [(15, 3), (3, 15), (3, 3), (15, 15), (3, 9), (15, 9), (9, 9)],
    [(15, 3), (3, 15), (3, 3), (15, 15), (3, 9), (15, 9), (9, 3), (9, 15)],
    [(15, 3), (3, 15), (3, 3), (15, 15), (3, 9), (15, 9), (9, 3), (9, 15), (9, 9)],
]


MOVE_PROPERTIES = ["B", "KO", "MN", "W"]
SETUP_PROPERTIES = ["AB", "AE", "AW", "PL"]
NODE_ANNOTATION_PROPERTIES = ["C", "DM", "GB", "GW", "HO", "N", "UC", "V"]
MOVE_ANNOTATION_PROPERTIES = ["BM", "DO", "IT", "TE"]
MARKUP_PROPERTIES = ["AR", "CR", "DD", "LB", "LN", "MA", "SL", "SQ", "TR"]
ROOT_PROPERTIES = ["AP", "CA", "FF", "GM", "ST", "SZ"]
GAME_INFO_PROPERTIES = [
    "AN",
    "BR",
    "BT",
    "CP",
    "DT",
    "EV",
    "GN",
    "GC",
    "ON",
    "OT",
    "PB",
    "PC",
    "PW",
    "RE",
    "RO",
    "RU",
    "SO",
    "TM",
    "US",
    "WR",
    "WT",
]
TIMING_PROPERTIES = ["BL", "OB", "OW", "WL"]
MISCELLANEOUS_PROPERTIES = ["FG", "PM", "VW"]
