import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTime
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class KakaoNaviEtaSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = None

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
                    "current_eta": round(current_data["duration"] / 60, 2),
                    "future_eta": round(future_data["duration"] / 60, 2),
                    "eta_difference": round((future_data["duration"] - current_data["duration"]) / 60, 2),
                    "distance": current_data["distance"],
                    "taxi_fare": current_data["fare"]["taxi"],
                    "toll_fare": current_data["fare"]["toll"],
                }
            except (KeyError, IndexError, TypeError):
                return {}
        return {}

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinators = hass.data[DOMAIN].get(config_entry.entry_id)
    
    if not coordinators:
        _LOGGER.error(f"No coordinators found for entry {config_entry.entry_id}")
        return

    sensors = []
    for route_name, coordinator in coordinators.items():
        if coordinator.data is None:
            _LOGGER.warning(f"No data in coordinator for route: {route_name}. Waiting for first refresh.")
            await coordinator.async_refresh()
        
        if coordinator.data is None:
            _LOGGER.error(f"Failed to get data from coordinator after refresh for route: {route_name}")
            continue
        
        if "current" not in coordinator.data or "routes" not in coordinator.data["current"]:
            _LOGGER.warning(f"Invalid data structure in coordinator for route: {route_name}")
            continue
        
        sensors.append(KakaoNaviEtaSensor(coordinator, config_entry, route_name))
    
    async_add_entities(sensors)
