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
