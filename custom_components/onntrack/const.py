DOMAIN = "onntrack"
CONF_IMEI = "imei"
CONF_VEHICLE_TYPE = "vehicle_type"

API_BASE = "https://platform.onntrack.nl/v3/new"
API_LOGIN = f"{API_BASE}/homepage/login"
API_MONITOR = f"{API_BASE}/newMonitor/getMonitorInfo"
API_LIST = f"{API_BASE}/newEquipment/queryEquipmentList"

DEFAULT_SCAN_INTERVAL = 60  # seconden

DEFAULT_VEHICLE_TYPE = "other"
VEHICLE_TYPES = ["car", "van", "truck", "motorbike", "scooter", "other"]
VEHICLE_ICONS = {
    "car": "mdi:car",
    "van": "mdi:van-utility",
    "truck": "mdi:truck",
    "motorbike": "mdi:motorbike",
    "scooter": "mdi:moped",
    "other": "mdi:map-marker",
}

# Foutcodes
CODE_SUCCESS = 10000
CODE_ALT_SUCCESS = 0
CODE_TOKEN_MISSING = 10005
CODE_TOKEN_INVALID = 10006
