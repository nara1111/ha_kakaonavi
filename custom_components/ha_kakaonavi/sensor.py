from typing import Any, Dict, Optional
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    DOMAIN, CONF_ROUTE_NAME, UNIT_OF_TIME, UNIT_OF_DISTANCE,
    CONF_PRIORITY
)
from .coordinator import KakaoNaviDataUpdateCoordinator

class KakaoNaviEtaSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:routes-clock"

    def __init__(self, coordinator: KakaoNaviDataUpdateCoordinator, config_entry: ConfigEntry,
                 route_name: str) -> None:
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._route_name = route_name
        self._attr_unique_id = f"{config_entry.entry_id}_{route_name}"
        self._attr_name = f"Kakao Navi ETA - {route_name}"
        self._attr_translation_key = "kakaonavi_eta"

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.DURATION

    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        return UNIT_OF_TIME

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
                "current_eta": round(current_data["duration"] / 60, 2),
                "future_eta": round(future_data["duration"] / 60, 2),
                "eta_difference": round((future_data["duration"] - current_data["duration"]) / 60, 2),
                "distance": f"{round(current_data['distance'] / 1000, 2)} {UNIT_OF_DISTANCE}",
                "taxi_fare": f"{current_data['fare']['taxi']:,}",
                "toll_fare": f"{current_data['fare']['toll']:,}",
                "priority": self.coordinator.route.get(CONF_PRIORITY),
            }
        except (KeyError, IndexError, TypeError):
            return {}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    if coordinator.data is None or "current" not in coordinator.data or "routes" not in coordinator.data["current"]:
        return

    sensor = KakaoNaviEtaSensor(coordinator, entry)
    async_add_entities([sensor])
