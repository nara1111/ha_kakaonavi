# sensor.py
from typing import Any, Dict, Optional
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTime, LENGTH_KILOMETERS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN


class KakaoNaviEtaSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = "mdi:routes-clock"

    def __init__(self, coordinator: "KakaoNaviDataUpdateCoordinator", config_entry: ConfigEntry,
                 route_name: str) -> None:
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._route_name = route_name
        self._attr_unique_id = f"{config_entry.entry_id}_{route_name}"

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.DURATION

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfTime.MINUTES

    @property
    def state(self) -> Optional[float]:
        try:
            return round(self.coordinator.data["current"]["routes"][0]["summary"]["duration"] / 60, 2)
        except (KeyError, IndexError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        try:
            current_data = self.coordinator.data["current"]["routes"][0]["summary"]
            future_data = self.coordinator.data["future"]["routes"][0]["summary"]
            return {
                "current_ETA (min.)": round(current_data["duration"] / 60, 2),
                "future_ETA (min.)": round(future_data["duration"] / 60, 2),
                "ETA_difference (min.)": round((future_data["duration"] - current_data["duration"]) / 60, 2),
                "distance (km)": f"{round(current_data['distance'] / 1000, 2)} {LENGTH_KILOMETERS}",
                "taxi_fare (KRW)": f"{current_data['fare']['taxi']}",
                "toll_fare (KRW)": f"{current_data['fare']['toll']}",
                "priority": self.coordinator.priority,
            }
        except (KeyError, IndexError, TypeError):
            return {}


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinators = hass.data[DOMAIN].get(config_entry.entry_id)

    if not coordinators:
        raise ConfigEntryNotReady(f"No coordinators found for entry {config_entry.entry_id}")

    sensors = []
    for route_name, coordinator in coordinators.items():
        if coordinator.data is None:
            raise ConfigEntryNotReady(f"No data in coordinator for route: {route_name}")

        if "current" not in coordinator.data or "routes" not in coordinator.data["current"]:
            raise ConfigEntryNotReady(f"Invalid data structure in coordinator for route: {route_name}")

        sensors.append(KakaoNaviEtaSensor(coordinator, config_entry, route_name))

    async_add_entities(sensors)
