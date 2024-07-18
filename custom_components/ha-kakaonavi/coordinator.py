from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from .const import DOMAIN, MAX_DAILY_CALLS

_LOGGER = logging.getLogger(__name__)

class KakaoNaviDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: KakaoNaviApiClient, start: str, end: str, waypoint: str, update_interval: int, future_update_interval: int):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )
        self.client = client
        self.start = start
        self.end = end
        self.waypoint = waypoint
        self.future_update_interval = timedelta(minutes=future_update_interval)
        self.last_future_update = None
        self.daily_calls = 0
        self.last_call_date = dt_util.now().date()

    async def _async_update_data(self):
        current_date = dt_util.now().date()
        if current_date > self.last_call_date:
            self.daily_calls = 0
            self.last_call_date = current_date

        if self.daily_calls >= MAX_DAILY_CALLS:
            _LOGGER.warning("Daily API call limit reached. Skipping update.")
            return self.data

        try:
            self.daily_calls += 1
            current_data = await self.hass.async_add_executor_job(
                self.client.direction, self.start, self.end, self.waypoint
            )

            future_data = self.data.get("future") if self.data else None
            if not self.last_future_update or dt_util.now() - self.last_future_update >= self.future_update_interval:
                self.daily_calls += 1
                future_time = dt_util.now() + timedelta(minutes=30)
                future_data = await self.hass.async_add_executor_job(
                    self.client.future_direction,
                    self.start,
                    self.end,
                    self.waypoint,
                    future_time.strftime("%Y%m%d%H%M")
                )
                self.last_future_update = dt_util.now()

            return {"current": current_data, "future": future_data}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")