from typing import Dict
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from .coordinator import KakaoNaviDataUpdateCoordinator
from .api import KakaoNaviApiClient
from .const import (
    DOMAIN,
    CONF_APIKEY,
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


PLATFORMS = [Platform.SENSOR]


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = KakaoNaviApiClient(entry.data[CONF_APIKEY])

    routes = entry.options.get(CONF_ROUTES, [])

    if not routes:
        # 초기 설정 시 data에서 route 정보를 가져옵니다.
        initial_route = {
            CONF_ROUTE_NAME: entry.data.get(CONF_ROUTE_NAME, "Default Route"),
            CONF_START: entry.data.get(CONF_START, ""),
            CONF_END: entry.data.get(CONF_END, ""),
            CONF_WAYPOINT: entry.data.get(CONF_WAYPOINT),
            CONF_PRIORITY: entry.data.get(CONF_PRIORITY, PRIORITY_RECOMMEND)
        }
        routes = [initial_route]

        # options에 routes 정보를 추가합니다.
        new_options = dict(entry.options)
        new_options[CONF_ROUTES] = routes
        hass.config_entries.async_update_entry(entry, options=new_options)

    coordinators = {}
    for route in routes:
        try:
            coordinator = KakaoNaviDataUpdateCoordinator(hass, client, route)
            await coordinator.async_config_entry_first_refresh()
            coordinators[route[CONF_ROUTE_NAME]] = coordinator
        except Exception as err:
            _LOGGER.error(f"Error initializing coordinator for route {route.get(CONF_ROUTE_NAME, 'Unknown')}: {err}")

    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
