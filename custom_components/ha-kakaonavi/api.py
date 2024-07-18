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

    def _address_to_coord(self, address):
        params = {"query": address}
        try:
            response = self.session.get(self.local_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("documents"):
                x = data["documents"][0]["x"]
                y = data["documents"][0]["y"]
                return f"{x},{y}"
            else:
                _LOGGER.error(f"No coordinates found for address: {address}")
                return None
        except requests.RequestException as e:
            _LOGGER.error(f"Error converting address to coordinates: {e}")
            return None

    def direction(self, start, end, waypoint=None):
        _LOGGER.debug(f"Calling direction API with start: {start}, end: {end}, waypoint: {waypoint}")
        
        start_coord = self._address_to_coord(start)
        end_coord = self._address_to_coord(end)
        waypoint_coord = self._address_to_coord(waypoint) if waypoint else None

        if not start_coord or not end_coord:
            _LOGGER.error("Failed to convert addresses to coordinates")
            return None

        params = {
            "origin": start_coord,
            "destination": end_coord,
            "waypoints": waypoint_coord,
            "priority": "RECOMMEND"
        }
        
        try:
            response = self.session.get(f"{self.navi_base_url}/directions", params=params)
            response.raise_for_status()
            data = response.json()
            _LOGGER.debug(f"Direction API response: {data}")
            return data
        except requests.RequestException as e:
            _LOGGER.error(f"Error calling direction API: {e}")
            _LOGGER.error(f"Response content: {e.response.content if e.response else 'No response'}")
            return None

    def future_direction(self, start, end, waypoint=None, departure_time=None):
        _LOGGER.debug(f"Calling future direction API with start: {start}, end: {end}, waypoint: {waypoint}, departure_time: {departure_time}")
        
        start_coord = self._address_to_coord(start)
        end_coord = self._address_to_coord(end)
        waypoint_coord = self._address_to_coord(waypoint) if waypoint else None

        if not start_coord or not end_coord:
            _LOGGER.error("Failed to convert addresses to coordinates")
            return None

        params = {
            "origin": start_coord,
            "destination": end_coord,
            "waypoints": waypoint_coord,
            "priority": "RECOMMEND",
            "departure_time": departure_time
        }
        
        try:
            response = self.session.get(f"{self.navi_base_url}/future/directions", params=params)
            response.raise_for_status()
            data = response.json()
            _LOGGER.debug(f"Future direction API response: {data}")
            return data
        except requests.RequestException as e:
            _LOGGER.error(f"Error calling future direction API: {e}")
            _LOGGER.error(f"Response content: {e.response.content if e.response else 'No response'}")
            return None

    def find_optimal_departure_time(self, start, end, waypoint, start_time, end_time, interval):
        _LOGGER.debug(f"Finding optimal departure time from {start_time} to {end_time} with interval {interval}")
        
        # 이 메서드의 구현은 API의 실제 기능에 따라 달라질 수 있습니다.
        # 여기서는 간단한 예시만 제공합니다.
        
        best_time = start_time
        best_duration = float('inf')
        
        current_time = start_time
        while current_time <= end_time:
            result = self.future_direction(start, end, waypoint, current_time.strftime("%Y%m%d%H%M"))
            if result and 'routes' in result:
                duration = result['routes'][0]['summary']['duration']
                if duration < best_duration:
                    best_duration = duration
                    best_time = current_time
            current_time += interval
        
        _LOGGER.debug(f"Optimal departure time found: {best_time}")
        return {"optimal_departure_time": best_time.isoformat(), "duration": best_duration}
