from typing import Any, Dict
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from .api import KakaoNaviApiClient
from .const import (
    CONF_UPDATE_INTERVAL, CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL,
    CONF_ROUTE_NAME, CONF_START, CONF_END, CONF_WAYPOINT, CONF_PRIORITY,
    MAX_DAILY_CALLS
)

_LOGGER = logging.getLogger(__name__)

class KakaoNaviDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: KakaoNaviApiClient,
        route: Dict[str, Any]
    ) -> None:
        self.route = route
        self.client = client
        self._update_interval = timedelta(minutes=route.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))
        self._future_update_interval = timedelta(minutes=route.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL))
        self.last_future_update: Any = None
        self.api_calls_today = 0
        self.last_call_date = dt_util.now().date()

        super().__init__(
            hass,
            _LOGGER,
            name=f"KakaoNavi_{route.get(CONF_ROUTE_NAME, 'Unknown')}",
            update_method=self._async_update_data,
            update_interval=self._update_interval,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            now = dt_util.now()
            if now.date() != self.last_call_date:
                self.api_calls_today = 0
                self.last_call_date = now.date()

            if self.api_calls_today >= MAX_DAILY_CALLS:
                raise UpdateFailed(f"Daily API call limit ({MAX_DAILY_CALLS}) reached for route: {self.route[CONF_ROUTE_NAME]}")

            current_data = await self._get_current_data()
            future_data = await self._get_future_data()

            if current_data is None or future_data is None:
                raise UpdateFailed(f"Failed to fetch data from Kakao Navi API for route: {self.route[CONF_ROUTE_NAME]}")

            self.api_calls_today += 2  # Increment by 2 as we make two API calls

            return {"current": current_data, "future": future_data}
        except Exception as err:
            _LOGGER.error(f"Error updating data for route {self.route[CONF_ROUTE_NAME]}: {str(err)}")
            return {}

    async def _get_current_data(self) -> Dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(
                self.client.direction,
                self.route[CONF_START],
                self.route[CONF_END],
                self.route.get(CONF_WAYPOINT),
                self.route.get(CONF_PRIORITY)
            )
        except Exception as err:
            _LOGGER.error(f"Error getting current data: {str(err)}")
            return {}

    async def _get_future_data(self) -> Dict[str, Any]:
        now = dt_util.now()
        if self.last_future_update is None or (now - self.last_future_update) >= self._future_update_interval:
            try:
                future_time = now + timedelta(minutes=30)
                future_data = await self.hass.async_add_executor_job(
                    self.client.future_direction,
                    self.route[CONF_START],
                    self.route[CONF_END],
                    self.route.get(CONF_WAYPOINT),
                    future_time.strftime("%Y%m%d%H%M"),
                    self.route.get(CONF_PRIORITY)
                )
                self.last_future_update = now
                return future_data
            except Exception as err:
                _LOGGER.error(f"Error getting future data: {str(err)}")
                return {}
        else:
            return self.data.get("future", {}) if self.data else {}