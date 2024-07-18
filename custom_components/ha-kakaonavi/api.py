import requests
import logging

_LOGGER = logging.getLogger(__name__)

class KakaoNaviApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"KakaoAK {api_key}"})
        self.base_url = "https://apis-navi.kakaomobility.com/v1"

    def direction(self, start, end, waypoint=None):
        _LOGGER.debug(f"Calling direction API with start: {start}, end: {end}, waypoint: {waypoint}")
        
        params = {
            "origin": start,
            "destination": end,
            "waypoints": waypoint,
            "priority": "RECOMMEND"
        }
        
        try:
            response = self.session.get(f"{self.base_url}/directions", params=params)
            response.raise_for_status()
            data = response.json()
            _LOGGER.debug(f"Direction API response: {data}")
            return data
        except requests.RequestException as e:
            _LOGGER.error(f"Error calling direction API: {e}")
            return None

    def future_direction(self, start, end, waypoint=None, departure_time=None):
        _LOGGER.debug(f"Calling future direction API with start: {start}, end: {end}, waypoint: {waypoint}, departure_time: {departure_time}")
        
        params = {
            "origin": start,
            "destination": end,
            "waypoints": waypoint,
            "priority": "RECOMMEND",
            "departure_time": departure_time
        }
        
        try:
            response = self.session.get(f"{self.base_url}/future/directions", params=params)
            response.raise_for_status()
            data = response.json()
            _LOGGER.debug(f"Future direction API response: {data}")
            return data
        except requests.RequestException as e:
            _LOGGER.error(f"Error calling future direction API: {e}")
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
