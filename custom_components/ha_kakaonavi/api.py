# api.py
from typing import Dict, Any, Optional
import requests


class KakaoNaviApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"KakaoAK {api_key}"})
        self.navi_base_url = "https://apis-navi.kakaomobility.com/v1"
        self.local_base_url = "https://dapi.kakao.com/v2/local/search/address.json"

    def test_api_key(self) -> None:
        response = self.session.get(f"{self.navi_base_url}/directions", params={
            "origin": "127.0,37.0",
            "destination": "127.1,37.1"
        })
        response.raise_for_status()

    def _address_to_coord(self, address: str) -> str:
        response = self.session.get(self.local_base_url, params={"query": address})
        response.raise_for_status()
        result = response.json()
        if result["documents"]:
            x = result["documents"][0]["x"]
            y = result["documents"][0]["y"]
            return f"{x},{y}"
        else:
            raise ValueError(f"Unable to find coordinates for address: {address}")

    def direction(self, start: str, end: str, waypoint: Optional[str] = None, priority: str = "RECOMMEND") -> Dict[
        str, Any]:
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

    def future_direction(self, start: str, end: str, waypoint: Optional[str] = None,
                         departure_time: Optional[str] = None, priority: str = "RECOMMEND") -> Dict[str, Any]:
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
