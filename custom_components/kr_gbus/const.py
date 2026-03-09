"""kr_gbus 상수."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "kr_gbus"

CONF_API_KEY_ARRIVAL = "api_key_arrival"

CONF_MONITORS = "monitors"
CONF_MONITOR_STATION_ID = "station_id"
CONF_MONITOR_ROUTE_ID = "route_id"
CONF_MONITOR_STA_ORDER = "sta_order"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL_SECONDS = 180