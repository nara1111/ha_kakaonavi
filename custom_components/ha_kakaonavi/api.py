from typing import Dict, Any, Optional
import requests
from homeassistant.exceptions import HomeAssistantError
from .const import PRIORITY_RECOMMEND

BASE_NAVI_URL = "https://apis-navi.kakaomobility.com/v1"
BASE_LOCAL_URL = "https://dapi.kakao.com/v2/local/search/address.json"

class KakaoNaviApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"KakaoAK {api_key}"})

    def test_api_key(self) -> None:
        try:
            response = self.session.get(f"{BASE_NAVI_URL}/directions", params={
                "origin": "127.0,37.0",
                "destination": "127.1,37.1"
            })
            response.raise_for_status()
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to validate API key: {error}") from error

    def _address_to_coord(self, address: str) -> str:
        try:
            response = self.session.get(BASE_LOCAL_URL, params={"query": address})
            response.raise_for_status()
            result = response.json()
            if result["documents"]:
                x = result["documents"][0]["x"]
                y = result["documents"][0]["y"]
                return f"{x},{y}"
            raise ValueError(f"No coordinates found for address: {address}")
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to convert address to coordinates: {error}") from error

    def direction(self, start: str, end: str, waypoint: Optional[str] = None, priority: str = PRIORITY_RECOMMEND) -> Dict[str, Any]:
        try:
            start_coord = self._address_to_coord(start)
            end_coord = self._address_to_coord(end)
            params = {
                "origin": start_coord,
                "destination": end_coord,
                "priority": priority
            }
            if waypoint:
                params["waypoints"] = self._address_to_coord(waypoint)

            response = self.session.get(f"{BASE_NAVI_URL}/directions", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to get directions: {error}") from error

    def future_direction(self, start: str, end: str, waypoint: Optional[str] = None,
                         departure_time: Optional[str] = None, priority: str = PRIORITY_RECOMMEND) -> Dict[str, Any]:
        try:
            start_coord = self._address_to_coord(start)
            end_coord = self._address_to_coord(end)
            params = {
                "origin": start_coord,
                "destination": end_coord,
                "priority": priority
            }
            if waypoint:
                params["waypoints"] = self._address_to_coord(waypoint)
            if departure_time:
                params["departure_time"] = departure_time

            response = self.session.get(f"{BASE_NAVI_URL}/future/directions", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to get future directions: {error}") from error
