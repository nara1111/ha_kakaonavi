import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from .coordinator import KakaoNaviDataUpdateCoordinator
from .api import KakaoNaviApiClient
from .const import (
    DOMAIN,
    CONF_APIKEY,
    CONF_ROUTES,  # 이 줄을 추가합니다.
    CONF_ROUTE_NAME,
    CONF_START,
    CONF_END,
    CONF_WAYPOINT,
    CONF_PRIORITY,
    CONF_UPDATE_INTERVAL,
    CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_FUTURE_UPDATE_INTERVAL,
    PRIORITY_RECOMMEND,
    PLATFORMS
)

# 이 줄을 제거합니다:
# PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = KakaoNaviApiClient(entry.data[CONF_APIKEY])

    routes = entry.options.get(CONF_ROUTES, [])

    coordinators = {}
    for route in routes:
        try:
            coordinator = KakaoNaviDataUpdateCoordinator(hass, client, route)
            await coordinator.async_config_entry_first_refresh()
            coordinators[route[CONF_ROUTE_NAME]] = coordinator
        except Exception as err:
            _LOGGER.error(f"Error initializing coordinator for route {route.get(CONF_ROUTE_NAME, 'Unknown')}: {err}")
            raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    for coordinator in coordinators.values():
        coordinator.update_interval = timedelta(minutes=entry.options[CONF_UPDATE_INTERVAL])
        coordinator.future_update_interval = timedelta(minutes=entry.options[CONF_FUTURE_UPDATE_INTERVAL])
    await hass.config_entries.async_reload(entry.entry_id)
