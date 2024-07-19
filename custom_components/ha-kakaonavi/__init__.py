import logging
from datetime import datetime
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv, entity_registry
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
    CONF_PRIORITY,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_FUTURE_UPDATE_INTERVAL,
    PRIORITY_RECOMMEND,
)
from .coordinator import KakaoNaviDataUpdateCoordinator
from .api import KakaoNaviApiClient

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

SERVICE_FIND_OPTIMAL_DEPARTURE_TIME_SCHEMA = vol.Schema({
    vol.Required("sensor_name"): cv.entity_id,
    vol.Required("start_time"): cv.datetime,
    vol.Required("end_time"): cv.datetime,
    vol.Optional("interval", default=30): cv.positive_int,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug(f"Setting up entry {entry.entry_id}")
    hass.data.setdefault(DOMAIN, {})
    client = KakaoNaviApiClient(entry.data[CONF_APIKEY])
    
    coordinators = {}
    routes = entry.options.get("routes", [])
    for route in routes:
        coordinator = KakaoNaviDataUpdateCoordinator(
            hass,
            client,
            route[CONF_START],
            route[CONF_END],
            route.get(CONF_WAYPOINT),
            entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
            entry.options.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL),
            route[CONF_ROUTE_NAME],
            route.get(CONF_PRIORITY, PRIORITY_RECOMMEND)
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
        sensor_name = call.data.get("sensor_name")
        if not sensor_name:
            _LOGGER.error("No sensor_name provided in service call")
            return

        ent_reg = entity_registry.async_get(hass)
        entity = ent_reg.async_get(sensor_name)
        if not entity:
            _LOGGER.error(f"Sensor {sensor_name} not found")
            return

        route_name = entity.unique_id.split('_')[-1]
        if route_name not in coordinators:
            _LOGGER.error(f"Route for sensor {sensor_name} not found")
            return

        start_time = call.data.get("start_time")
        end_time = call.data.get("end_time")
        if not start_time or not end_time:
            _LOGGER.error("Both start_time and end_time must be provided")
            return

        # Convert datetime objects to string format if necessary
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y%m%d%H%M")
        if isinstance(end_time, datetime):
            end_time = end_time.strftime("%Y%m%d%H%M")

        interval = call.data.get("interval", 30)

        coordinator = coordinators[route_name]
        try:
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
        except Exception as e:
            _LOGGER.error(f"Error finding optimal departure time: {e}")

    hass.services.async_register(
        DOMAIN,
        "find_optimal_departure_time",
        find_optimal_departure_time,
        schema=SERVICE_FIND_OPTIMAL_DEPARTURE_TIME_SCHEMA
    )

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
