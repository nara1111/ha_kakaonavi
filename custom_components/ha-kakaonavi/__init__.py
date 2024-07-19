import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from .const import (
    DOMAIN,
    CONF_APIKEY,
    CONF_ROUTES,
    CONF_START,
    CONF_END,
    CONF_WAYPOINT,
    CONF_UPDATE_INTERVAL,
    CONF_FUTURE_UPDATE_INTERVAL,
    CONF_ROUTE_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_FUTURE_UPDATE_INTERVAL,
)
from .coordinator import KakaoNaviDataUpdateCoordinator
from .api import KakaoNaviApiClient

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug(f"Setting up entry {entry.entry_id}")
    hass.data.setdefault(DOMAIN, {})
    client = KakaoNaviApiClient(entry.data[CONF_APIKEY])
    
    coordinators = {}
    for route in entry.data[CONF_ROUTES]:
        coordinator = KakaoNaviDataUpdateCoordinator(
            hass,
            client,
            route[CONF_START],
            route[CONF_END],
            route.get(CONF_WAYPOINT),
            entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
            entry.data.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL),
            route[CONF_ROUTE_NAME]
        )
        try:
            await coordinator.async_config_entry_first_refresh()
        except Exception as err:
            _LOGGER.error(f"Error refreshing coordinator for route {route[CONF_ROUTE_NAME]}: {err}")
            continue
        coordinators[route[CONF_ROUTE_NAME]] = coordinator

    if not coordinators:
        _LOGGER.error("No coordinators were successfully initialized")
        return False

    hass.data[DOMAIN][entry.entry_id] = coordinators
    _LOGGER.debug(f"Data stored in hass.data[DOMAIN]: {hass.data[DOMAIN]}")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def find_optimal_departure_time(call):
        route_name = call.data["route_name"]
        start_time = call.data["start_time"]
        end_time = call.data["end_time"]
        interval = call.data.get("interval", 30)
        if route_name not in coordinators:
            _LOGGER.error(f"Route {route_name} not found")
            return
        coordinator = coordinators[route_name]
        result = await hass.async_add_executor_job(
            coordinator.client.find_optimal_departure_time,
            coordinator.start,
            coordinator.end,
            coordinator.waypoint,
            start_time,
            end_time,
            interval
        )
        hass.states.async_set(f"{DOMAIN}.{route_name}_optimal_departure", result["optimal_departure_time"], result)

    hass.services.async_register(DOMAIN, "find_optimal_departure_time", find_optimal_departure_time)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
