# ha-kakaonavi
카카오모빌리티 디벨로퍼스의 길찾기 API (https://developers.kakaomobility.com/docs/navi-api/start/) 를 사용하여, HomeAssistant에서 출발지와 경유지, 목적지까지의 예상 도착시간을 알 수 있다.

### 제공기능
1. 현재 ETA
2. 30분 후 ETA
3. 현재와 미래 ETA 차이
4. 거리, 택시 요금, 통행료 정보
5. 최적 출발 시간 찾기 서비스 (HA의 '개발자 도구' 내 서비스에서 조회 가능)
6. 현재 정보 및 미래 정보 조회 주기 설정 (현재 현재 정보는 일 1만건, 미래 정보는 일 5천건까지 조회 무료)

### Special Thanks to
네이버 HA카페 IOT광신도 님의 초기 센서를 기반으로 통합구성요소화 하였습니다. (https://cafe.naver.com/koreassistant/17616)
