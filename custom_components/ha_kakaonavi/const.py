from homeassistant.const import (
    CONF_NAME,
    CONF_API_KEY,
)

DOMAIN = "ha_kakaonavi"
CONF_APIKEY = CONF_API_KEY
CONF_ROUTES = "routes"
CONF_START = "start"
CONF_END = "end"
CONF_WAYPOINT = "waypoint"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_FUTURE_UPDATE_INTERVAL = "future_update_interval"
CONF_ROUTE_NAME = CONF_NAME
DEFAULT_UPDATE_INTERVAL = 10
DEFAULT_FUTURE_UPDATE_INTERVAL = 60
MAX_DAILY_CALLS = 5000

CONF_PRIORITY = "priority"
PRIORITY_RECOMMEND = "RECOMMEND"
PRIORITY_TIME = "TIME"
PRIORITY_DISTANCE = "DISTANCE"
PRIORITY_OPTIONS = [PRIORITY_RECOMMEND, PRIORITY_TIME, PRIORITY_DISTANCE]