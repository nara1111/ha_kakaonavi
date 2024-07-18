from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
import logging

from .api import KakaoNaviApiClient

_LOGGER = logging.getLogger(__name__)

class KakaoNaviDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        client: KakaoNaviApiClient,
        start: str,
        end: str,
        waypoint: str,
        update_interval: int,
        future_update_interval: int
    ):
        super().__init__(
            hass,
            _LOGGER,
            name="KakaoNavi",
            update_interval=timedelta(minutes=update_interval),
        )
        self.client = client
        self.start = start
        self.end = end
        self.waypoint = waypoint
        self.future_update_interval = timedelta(minutes=future_update_interval)

    async def _async_update_data(self):
        try:
            current_data = await self.hass.async_add_executor_job(
                self.client.direction, self.start, self.end, self.waypoint
            )
            future_time = dt_util.now() + timedelta(minutes=30)
            future_data = await self.hass.async_add_executor_job(
                self.client.future_direction,
                self.start,
                self.end,
                self.waypoint,
                future_time.strftime("%Y%m%d%H%M")
            )
            if current_data is None or future_data is None:
                _LOGGER.error("Failed to fetch data from Kakao Navi API")
                return None
            return {"current": current_data, "future": future_data}
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")