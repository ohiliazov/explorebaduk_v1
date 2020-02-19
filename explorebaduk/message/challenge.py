# Challenge name
GAME_NAME = r"GN\[(?P<name>[\w\W]+)\]"

# Game info
# GI[0R1W19H19] -> Ranked Game, Japanese Rules, board size 19x19
# GI[1R0W9H13MIN1900MAX2100]  -> Free Game, Chinese Rules, board size 9x13, allow player with rank between 1900 and 2100
# TODO: add players number for future simultaneous and rengo game types
GAME_TYPE = r"(?P<game_type>\d+)"
RULES = r"R(?P<rules>\d+)"
BOARD_SIZE = r"W(?P<width>\d+)H(?P<height>\d+)"
MIN_RATING = r"(MIN(?P<rank_lower>\d+))?"
MAX_RATING = r"(MAX(?P<rank_upper>\d+))?"

GAME_INFO = fr"GI\[{GAME_TYPE}{RULES}{BOARD_SIZE}{MIN_RATING}{MAX_RATING}\]"

# Flags
# FL[100] -> open, no undo, no pause
FLAGS = r"FL\[(?P<is_open>\d)(?P<undo>\d)(?P<pause>\d)\]"

# Time system
# TS[0]             -> no time control
# TS[1M3600]        -> Sudden Death, 1 hour
# TS[1M3600D3]      -> Sudden Death, 1 hour, delay for 3 seconds
# TS[2M3600O30P5]   -> Byo-yomi, 1 hour + 5 periods per 30 seconds
# TS[3M3600O300S10] -> Canadian, 1 hour + 5 minutes per 10 stones
# TS[3M1200B7]      -> Fischer, 30 minutes + 7 seconds per each move
TIME_CONTROL = r"(?P<time_system>\d+)"
MAIN_TIME = r"(M(?P<main_time>\d+))?"
OVERTIME = r"(O(?P<overtime>\d+))?"
PERIODS = r"(P(?P<periods>\d+))?"
STONES = r"(S(?P<stones>\d+))?"
BONUS = r"(B(?P<bonus>\d+))?"
DELAY = r"(D(?P<delay>\d+))?"

TIME_SYSTEM = fr"TS\[{TIME_CONTROL}{MAIN_TIME}{OVERTIME}{PERIODS}{STONES}{BONUS}{DELAY}\]"

# Handicap settings
# CL[auto]              -> automatic handicap, komi 0.5
# CL[even]              -> nigiri, no handicap, default komi
# CL[black]HN[3]KM[0.5] -> black, 3 stones, komi 0.5
# CL[white]HN[9]KM[0]   -> white, 9 stones, no komi (jigo is possible)
COLOR = r"CL\[(?P<color>\d)\]"
HANDICAP = r"(HN\[(?P<handicap>\d)\])?"
KOMI = r"(KM\[(?P<komi>\d+(\.5)?)\])?"

SETTINGS = fr"{COLOR}{HANDICAP}{KOMI}"

CHALLENGE_STRING = fr"{GAME_NAME}{GAME_INFO}{FLAGS}{TIME_SYSTEM}"
JOIN_CHALLENGE_STRING = fr"{SETTINGS}"
