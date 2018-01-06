import os

# ***************** json fields ***************** #
DATE = "date"

MOVEMENT_POINTS = "movementPoints"
TOUCH_DOWN_POINTS = "touchDownPoints"
TOUCH_UP_POINTS = "touchUpPoints"
SAMPLED_POINTS = "sampledPoints"

WORD_NUMBER = "wordNumber"

TIME = "time"
COMPONENT = "component"
X = "x"
Y = "y"

SESSION_DATA = "sessionData"
NAME = "name"
SURNAME = "surname"
AGE = "age"

GENDER = "gender"
HANDWRITING = "handwriting"
ID = "id"
TOTAL_WORD_NUMBER = "totalWordNumber"

DEVICE_DATA = "deviceData"
DEVICE_FINGERPRINT = "deviceFingerPrint"
DEVICE_MODEL = "deviceModel"
HEIGHT_PIXELS = "heigthPixels"
WIDTH_PIXELS = "widthPixels"
XDPI = "xdpi"
YDPI = "ydpi"

# Json structure

JSON_FIELDS = [
    DATE,
    MOVEMENT_POINTS,
    TOUCH_DOWN_POINTS,
    TOUCH_UP_POINTS,
    SAMPLED_POINTS,
    WORD_NUMBER,
    SESSION_DATA,
]

SESSION_DATA_FIELDS = [
    NAME,
    SURNAME,
    AGE,
    GENDER,
    HANDWRITING,
    ID,
    TOTAL_WORD_NUMBER,
    DEVICE_DATA,
]

DEVICE_DATA_FIELDS = [
    DEVICE_FINGERPRINT,
    DEVICE_MODEL,
    HEIGHT_PIXELS,
    WIDTH_PIXELS,
    XDPI,
    YDPI,
]

POINTS = [
    COMPONENT,
    X,
    Y,
]

TIMED_POINTS = POINTS + [TIME]

# *********************************************** #

# other useful labels #
WORD_ID = "word_id"
USER_ID = "user_id"
WORDID_USERID_MAP = "wordid_userid_map"
USERID_USERDATA_MAP = "userid_userdata_map"

JSON_EXTENSION = ".json"
CSV_EXTENSION = ".csv"
PICKLE_EXTENSION = ".pickle"

DATAFRAME = "dataframe"
FEATURE = "features"

POINTS_WITH_WORD_ID = POINTS + [WORD_ID]
TIMED_POINTS_WITH_WORD_ID = TIMED_POINTS + [WORD_ID]

POINTS_SERIES_TYPE = [MOVEMENT_POINTS, TOUCH_DOWN_POINTS, TOUCH_UP_POINTS, SAMPLED_POINTS]
TIMED_POINTS_SERIES_TYPE = [MOVEMENT_POINTS, TOUCH_DOWN_POINTS, TOUCH_UP_POINTS]

ALL_DATAFRAMES = [WORDID_USERID_MAP, USERID_USERDATA_MAP] + POINTS_SERIES_TYPE

# files constants
BASE_FOLDER = "../res/"
BIOTOUCH_FOLDER = BASE_FOLDER + "Biotouch"

BASE_GENERATED_FOLDER = os.path.join(BASE_FOLDER, "generated/")
BASE_GENERATED_CSV_FOLDER = os.path.join(BASE_GENERATED_FOLDER, "csv/")

BUILD_PATH = lambda base, file, desc, ext: os.path.join(base, file + "_" + desc + ext)

BUILD_DATAFRAME_PICKLE_PATH = lambda file: os.path.join(BUILD_PATH(BASE_GENERATED_FOLDER, file, DATAFRAME, PICKLE_EXTENSION))
BUILD_DATAFRAME_CSV_PATH = lambda file: os.path.join(BUILD_PATH(BASE_GENERATED_FOLDER, file, DATAFRAME, CSV_EXTENSION))

BUILD_FEATURE_PICKLE_PATH = lambda file: os.path.join(BUILD_PATH(BASE_GENERATED_FOLDER, file, FEATURE, PICKLE_EXTENSION))
BUILD_FEATURE_CSV_PATH = lambda file: os.path.join(BUILD_PATH(BASE_GENERATED_FOLDER, file, FEATURE, CSV_EXTENSION))


PATHS_FUN = {DATAFRAME:
                 {PICKLE_EXTENSION: BUILD_DATAFRAME_PICKLE_PATH,
                  CSV_EXTENSION: BUILD_DATAFRAME_CSV_PATH},
             FEATURE:
                 {PICKLE_EXTENSION: BUILD_FEATURE_PICKLE_PATH,
                  CSV_EXTENSION: BUILD_FEATURE_CSV_PATH}}