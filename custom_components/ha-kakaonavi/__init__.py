import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import (
    DOMAIN,
    CONF_APIKEY,
    CONF_START,
    CONF_END,
    CONF_WAYPOINT,
    CONF_UPDATE_INTERVAL,
    CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_FUTURE_UPDATE_INTERVAL,
)
from .coordinator import KakaoNaviDataUpdateCoordinator
from .api import KakaoNaviApiClient
import logging

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = KakaoNaviApiClient(entry.data[CONF_APIKEY])
    coordinator = KakaoNaviDataUpdateCoordinator(
        hass,
        client,
        entry.data[CONF_START],
        entry.data[CONF_END],
        entry.data.get(CONF_WAYPOINT),
        entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        entry.data.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL)
    )

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        _LOGGER.error("Failed to retrieve initial data from Kakao Navi API")
        return False

    if coordinator.data is None:
        _LOGGER.error("Coordinator data is None after initial refresh")
        return False

    _LOGGER.info(f"Coordinator data after initial refresh: {coordinator.data}")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def find_optimal_departure_time(call):
        start_time = call.data["start_time"]
        end_time = call.data["end_time"]
        interval = call.data.get("interval", 30)
        result = await hass.async_add_executor_job(
            coordinator.client.find_optimal_departure_time,
            coordinator.start,
            coordinator.end,
            coordinator.waypoint,
            start_time,
            end_time,
            interval
        )
        hass.states.async_set(f"{DOMAIN}.optimal_departure", result["optimal_departure_time"], result)

    hass.services.async_register(DOMAIN, "find_optimal_departure_time", find_optimal_departure_time)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok