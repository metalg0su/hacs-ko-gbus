# GBus for HA

경기도 버스도착정보 HACS 커스텀 통합

## 기능

- 정류장/노선 조합으로 모니터 등록
- 도착 예정 시각, 남은 정류장 수, 혼잡도, 잔여좌석 등 센서 제공
- 금일 기준 첫차/막차 시각 제공 (평일/토/일/공휴일 구분)
- 운행시간 외 API 갱신 자동 중단

## 설치

- HA 인스턴스에 HACS 설치
- 아래 뱃지를 눌러 HACS 커스텀 레포 등록

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=metalg0su&repository=hacs-ko-gbus&category=integration)

## 설정

### 1. API 키 발급

[공공데이터포털](https://www.data.go.kr)에서 아래 API 활용 신청.

| API | 사용처 |
|-----|--------|
| [버스도착정보 조회](https://www.data.go.kr/data/15080346/openapi.do) | 실시간 도착 정보 갱신 |
| [정류소 조회](https://www.data.go.kr/data/15080666/openapi.do) | 모니터 등록 시 정류장 검색 |
| [버스노선 조회](https://www.data.go.kr/data/15080662/openapi.do) | 첫차/막차 시각 조회 |

### 2. 통합 추가

- 설정 > 기기 및 서비스 > 통합구성요소 추가하기 > **경기버스정보** > API 키 입력
- 기본 갱신값 180초 추천. 필요에 따라 조정 (API rate limit 주의)
> 기본적으로 요일 타입을 확인하기 위한 구성요소 센서가 추가됨

### 3. 노선 모니터링 추가

- 생성된 통합구성정보 진입
- 옵션 (톱니바퀴) 눌러서 정류장 검색
- 해당 정류장의 노선 선택
- 정류장의 노선 한 개당 구성요소가 추가됨. 필요 시 반복

## 센서

각 모니터 구성요소는 아래 센서를 생성함

| 센서 | 설명 | 비고 |
|------|------|------|
| 운행상태 | 운행, 곧도착 등 | |
| 도착시간 | 첫 번째 버스 도착 예정 시각 | timestamp |
| 남은정류장 | 남은 정류장 수 | |
| 혼잡도 | 여유, 보통, 혼잡 | |
| 잔여좌석 | 좌석버스 잔여석 | |
| 차량번호 | | |
| 차량유형 | 일반, 저상 등 | |
| 도착시간 (2번째) | 두 번째 버스 | timestamp |
| 남은정류장 (2번째) | | |
| 혼잡도 (2번째) | | |
| 잔여좌석 (2번째) | | |
| 차량번호 (2번째) | | |
| 차량유형 (2번째) | | |
| 기점 첫차 | 금일 요일구분 기준 | timestamp |
| 기점 막차 | | timestamp |
| 종점 첫차 | | timestamp |
| 종점 막차 | | timestamp |
| 요일구분 | 평일, 토요일, 일요일, 공휴일 | |
