import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTime, LENGTH_KILOMETERS
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class KakaoNaviEtaSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = "mdi:routes-clock"

    def __init__(self, coordinator, config_entry, route_name):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._route_name = route_name
        self._attr_unique_id = f"{config_entry.entry_id}_{route_name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id, route_name)},
            "name": f"Kakao Navi Route: {route_name}",
            "manufacturer": "Kakao",
        }

    @property
    def device_class(self):
        return SensorDeviceClass.DURATION

    @property
    def native_unit_of_measurement(self):
        return UnitOfTime.MINUTES

    @property
    def state(self):
        if self.coordinator.data and "current" in self.coordinator.data:
            try:
                return round(self.coordinator.data["current"]["routes"][0]["summary"]["duration"] / 60, 2)
            except (KeyError, IndexError, TypeError):
                return None
        return None

    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
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
        return {}

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.debug(f"Setting up sensor for entry {config_entry.entry_id}")
    _LOGGER.debug(f"hass.data[DOMAIN] contents: {hass.data[DOMAIN]}")

    coordinators = hass.data[DOMAIN].get(config_entry.entry_id)
    
    if not coordinators:
        _LOGGER.error(f"No coordinators found for entry {config_entry.entry_id}")
        return

    sensors = []
    for route_name, coordinator in coordinators.items():
        if coordinator.data is None:
            _LOGGER.warning(f"No data in coordinator for route: {route_name}. Skipping.")
            continue
        
        if "current" not in coordinator.data or "routes" not in coordinator.data["current"]:
            _LOGGER.warning(f"Invalid data structure in coordinator for route: {route_name}. Skipping.")
            continue
        
        sensors.append(KakaoNaviEtaSensor(coordinator, config_entry, route_name))
    
    if sensors:
        async_add_entities(sensors)
    else:
        _LOGGER.warning("No sensors were created")
