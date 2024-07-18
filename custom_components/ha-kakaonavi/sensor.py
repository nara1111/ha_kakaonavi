import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTime
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class KakaoNaviEtaSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator, config_entry, index):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{index}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"Kakao Navi Route {index}",
            "manufacturer": "Kakao",
        }
        self._index = index - 1  # 인덱스를 0부터 시작하도록 조정

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
                return round(self.coordinator.data["current"]["routes"][self._index]["summary"]["duration"] / 60, 2)
            except (KeyError, IndexError, TypeError):
                return None
        return None

    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
            try:
                current_data = self.coordinator.data["current"]["routes"][self._index]["summary"]
                future_data = self.coordinator.data["future"]["routes"][self._index]["summary"]
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    if coordinator is None:
        _LOGGER.error("Coordinator is None. Cannot set up sensors.")
        return

    if coordinator.data is None:
        _LOGGER.warning("No data in coordinator. Waiting for first refresh.")
        await coordinator.async_refresh()

    if coordinator.data is None:
        _LOGGER.error("Failed to get data from coordinator after refresh.")
        return

    sensors = []
    current_data = coordinator.data.get("current")
    if current_data is None:
        _LOGGER.warning("No 'current' data in coordinator.")
        return

    routes = current_data.get("routes", [])
    if not routes:
        _LOGGER.warning("No routes found in coordinator data.")
        return

    for i, _ in enumerate(routes, 1):
        sensors.append(KakaoNaviEtaSensor(coordinator, config_entry, i))

    async_add_entities(sensors)