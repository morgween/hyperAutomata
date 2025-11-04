from enum import Enum

COLOR_RED = "#FF0000"
COLOR_BLACK = "#000000"
COLOR_GREEN = "#008000"
COLOR_RT_BG = "#e0e0ff"
COLOR_DT_BG = "#f0f0f0"
COLOR_CS_BG = "#e7fff7"

IMG_SIZE = (25, 25)

PARALLEL_OFFSET = 13
STATE_RADIUS = 30

RUN_PAUSES_MS = 600

EMPTY_SETUP = "State: ???"

#logger
LOG_DIR = 'logs'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
ERROR_LOG = "error_log.log"
OTHER_LOG = "app_log.log"

#enum for application state.
class AppMode(Enum):
    DRAWING = "drawing"
    RUNNING = "running"