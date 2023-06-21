# if DEBUG, then only requests data from 1 battle
DEBUG = False

# set battle formats whose data you want
FORMATS = [
    "gen9randombattle",
    "gen9ou",
    "gen9randombattleblitz",
    "gen9unratedrandombattle",
    "gen9ubers",
    "gen9uu",
    "gen9ru",
    "gen9nu",
    "gen9monotype",
]

# set directory where data should be stored (relative path)
# directory will be created if it doesn't exist
SAVE_DIR = "battles"

# max number of battles to save per file: (use this to balance I/O throughput vs RAM usage)
BATCH_SIZE = 10000

LOG_FILENAME = "showdown.log"
