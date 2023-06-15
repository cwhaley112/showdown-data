# if DEBUG, then only requests data from 1 battle
DEBUG = False

# set battle format whose data you want (only supporting 1 because multiple would make too many API requests)

FORMAT = "gen9randombattle"

# set directory where data should be stored (relative path)
# directory will be created if it doesn't exist
SAVE_DIR = "battles"

# max number of battles to save per file: (use this to balance I/O throughput vs RAM usage)
BATCH_SIZE = 1000

LOG_FILENAME = "showdown.log"
