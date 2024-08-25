# ha-kakaonavi
카카오모빌리티 디벨로퍼스의 길찾기 API (https://developers.kakaomobility.com/docs/navi-api/start/) 를 사용하여, HomeAssistant에서 출발지와 경유지, 목적지까지의 예상 도착시간을 알 수 있다.

### 제공기능
![스크린샷 2024-08-25 093926](https://github.com/user-attachments/assets/016af431-848d-44a6-8893-5c525944f8e1)
1. 현재 ETA
2. 미래 ETA (30분 후 출발시)
3. 현재와 미래 ETA 차이
4. 거리, 택시 요금, 통행료 정보
5. 현재 정보 및 미래 정보 조회 주기 설정 (길찾기는 10분, 미래 정보는 1시간 단위 업데이트라 참고 정도 해야합니다. 이렇게 하는 이유는 미래 정보 호출이 일 5천건으로 제한이 있기 때문입니다.)

#### 설정방법
##### 최초 등록시
![스크린샷 2024-08-25 094312](https://github.com/user-attachments/assets/9af6aad7-14f2-4a41-9a5d-580157bb26f9)
1. API키 (필수)
2. 경로명 (필수)
3. 출발지 주소 (필수)
4. 도착지 주소 (필수)
5. 경유지 (선택)
6. 선호 탐색 알고리즘 (기본 카카오내비의 '추천')

##### 수정시
구성 선택시 '경로 편집' 및 '업데이트 주기' 설정 가능
![스크린샷 2024-08-25 093855](https://github.com/user-attachments/assets/1ca6b81c-f7e5-426b-8263-6d8db3437513)
![스크린샷 2024-08-25 093905](https://github.com/user-attachments/assets/c6ec7e37-691f-41b4-8163-e333dfb00c60)


### Special Thanks to
네이버 HA카페 IOT광신도 님의 초기 센서를 기반으로 통합구성요소화 하였습니다. (https://cafe.naver.com/koreassistant/17616)
