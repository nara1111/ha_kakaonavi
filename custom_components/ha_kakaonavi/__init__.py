from typing import Dict
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, CONF_APIKEY, CONF_ROUTES, CONF_ROUTE_NAME
from .coordinator import KakaoNaviDataUpdateCoordinator
from .api import KakaoNaviApiClient

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    try:
        client = KakaoNaviApiClient(entry.data[CONF_APIKEY])
    except KeyError:
        raise ConfigEntryNotReady(f"API key not found in configuration")

    coordinators: Dict[str, KakaoNaviDataUpdateCoordinator] = {}
    routes = entry.options.get(CONF_ROUTES, [])

    if not routes:
        raise ConfigEntryNotReady("No routes configured. Please add routes in the integration options.")

    for route in routes:
        try:
            coordinator = KakaoNaviDataUpdateCoordinator(hass, client, route)
            await coordinator.async_config_entry_first_refresh()
            coordinators[route[CONF_ROUTE_NAME]] = coordinator
        except Exception as err:
            raise ConfigEntryNotReady(
                f"Error initializing coordinator for route {route.get(CONF_ROUTE_NAME, 'Unknown')}: {err}")

    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)