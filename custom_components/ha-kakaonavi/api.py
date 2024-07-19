import requests
import logging

_LOGGER = logging.getLogger(__name__)

class KakaoNaviApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"KakaoAK {api_key}"})
        self.navi_base_url = "https://apis-navi.kakaomobility.com/v1"
        self.local_base_url = "https://dapi.kakao.com/v2/local/search/address.json"

    def test_api_key(self):
        response = self.session.get(f"{self.navi_base_url}/directions", params={
            "origin": "127.0,37.0",
            "destination": "127.1,37.1"
        })
        response.raise_for_status()

    def _address_to_coord(self, address):
        response = self.session.get(self.local_base_url, params={"query": address})
        response.raise_for_status()
        result = response.json()
        if result["documents"]:
            x = result["documents"][0]["x"]
            y = result["documents"][0]["y"]
            return f"{x},{y}"
        else:
            raise ValueError(f"Unable to find coordinates for address: {address}")

    def direction(self, start, end, waypoint=None, priority="RECOMMEND"):
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

    def future_direction(self, start, end, waypoint=None, departure_time=None, priority="RECOMMEND"):
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

    def find_optimal_departure_time(self, start, end, waypoint, start_time, end_time, interval):
        start_coord = self._address_to_coord(start)
        end_coord = self._address_to_coord(end)
        params = {
            "origin": start_coord,
            "destination": end_coord,
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval
        }
        if waypoint:
            params["waypoints"] = self._address_to_coord(waypoint)
        
        response = self.session.get(f"{self.navi_base_url}/optimal-departure", params=params)
        response.raise_for_status()
        return response.json()
