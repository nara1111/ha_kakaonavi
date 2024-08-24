from typing import Dict, Any, Optional
import requests
from homeassistant.exceptions import HomeAssistantError

class KakaoNaviApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"KakaoAK {api_key}"})
        self.navi_base_url = "https://apis-navi.kakaomobility.com/v1"
        self.local_base_url = "https://dapi.kakao.com/v2/local/search/address.json"

    def test_api_key(self) -> None:
        try:
            response = self.session.get(f"{self.navi_base_url}/directions", params={
                "origin": "127.0,37.0",
                "destination": "127.1,37.1"
            })
            response.raise_for_status()
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to validate API key: {error}") from error

    def _address_to_coord(self, address: str) -> str:
        try:
            response = self.session.get(self.local_base_url, params={"query": address})
            response.raise_for_status()
            result = response.json()
            if result["documents"]:
                x = result["documents"][0]["x"]
                y = result["documents"][0]["y"]
                return f"{x},{y}"
            else:
                raise ValueError(f"No coordinates found for address: {address}")
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to convert address to coordinates: {error}") from error

    def direction(self, start: str, end: str, waypoint: Optional[str] = None, priority: str = "RECOMMEND") -> Dict[
        str, Any]:
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

            response = self.session.get(f"{self.navi_base_url}/directions", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to get directions: {error}") from error

    def future_direction(self, start: str, end: str, waypoint: Optional[str] = None,
                         departure_time: Optional[str] = None, priority: str = "RECOMMEND") -> Dict[str, Any]:
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

            response = self.session.get(f"{self.navi_base_url}/future/directions", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            raise HomeAssistantError(f"Failed to get future directions: {error}") from error