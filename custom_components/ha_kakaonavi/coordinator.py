from typing import Any, Dict
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from .api import KakaoNaviApiClient
from .const import CONF_UPDATE_INTERVAL, CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL, CONF_ROUTE_NAME

_LOGGER = logging.getLogger(__name__)

class KakaoNaviDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        client: KakaoNaviApiClient,
        route: Dict[str, Any]
    ) -> None:
        update_interval = timedelta(minutes=route.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            name=f"KakaoNavi_{route[CONF_ROUTE_NAME]}",
            update_interval=update_interval,
        )
        self.client = client
        self.route = route
        self.future_update_interval = timedelta(minutes=route.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL))
        self.last_future_update = None

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            current_data = await self.hass.async_add_executor_job(
                self.client.direction,
                self.route['start'],
                self.route['end'],
                self.route.get('waypoint'),
                self.route.get('priority')
            )

            now = dt_util.now()
            if self.last_future_update is None or (now - self.last_future_update) >= self.future_update_interval:
                future_time = now + timedelta(minutes=30)
                future_data = await self.hass.async_add_executor_job(
                    self.client.future_direction,
                    self.route['start'],
                    self.route['end'],
                    self.route.get('waypoint'),
                    future_time.strftime("%Y%m%d%H%M"),
                    self.route.get('priority')
                )
                self.last_future_update = now
            else:
                future_data = self.data["future"] if self.data else None

            if current_data is None or future_data is None:
                raise UpdateFailed(f"Failed to fetch data from Kakao Navi API for route: {self.route[CONF_ROUTE_NAME]}")

            return {"current": current_data, "future": future_data}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API for route {self.route[CONF_ROUTE_NAME]}: {err}")