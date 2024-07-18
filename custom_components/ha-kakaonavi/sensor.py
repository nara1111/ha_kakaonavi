from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class KakaoNaviEtaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}"
        self._attr_name = f"Kakao Navi ETA: {config_entry.data['start']} to {config_entry.data['end']}"

    @property
    def state(self):
        if self.coordinator.data:
            return round(self.coordinator.data["current"]["routes"][0]["summary"]["duration"] / 60, 2)
        return None

    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
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
        return {}

    @property
    def unit_of_measurement(self):
        return "min"

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([KakaoNaviEtaSensor(coordinator, config_entry)])