# coordinator.py
from typing import Any, Dict
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from .api import KakaoNaviApiClient

class KakaoNaviDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        client: KakaoNaviApiClient,
        route: Dict[str, Any]
    ) -> None:
        super().__init__(
            hass,
            name=f"KakaoNavi_{route['name']}",
            update_interval=timedelta(minutes=route.get('update_interval', 10)),
        )
        self.client = client
        self.route = route

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            current_data = await self.hass.async_add_executor_job(
                self.client.direction,
                self.route['start'],
                self.route['end'],
                self.route.get('waypoint'),
                self.route.get('priority')
            )

            future_time = dt_util.now() + timedelta(minutes=30)
            future_data = await self.hass.async_add_executor_job(
                self.client.future_direction,
                self.route['start'],
                self.route['end'],
                self.route.get('waypoint'),
                future_time.strftime("%Y%m%d%H%M"),
                self.route.get('priority')
            )

            if current_data is None or future_data is None:
                raise UpdateFailed(f"Failed to fetch data from Kakao Navi API for route: {self.route['name']}")
            return {"current": current_data, "future": future_data}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API for route {self.route['name']}: {err}")
