"""경기버스 API 공통 열거형.

공공데이터포털 경기도 버스 API 응답에서 공통으로 사용하는 열거형을 정의한다.
"""

from enum import IntEnum, StrEnum


class _DisplayNameMixin:
    """display_name 프로퍼티를 제공하는 mixin."""

    @property
    def display_name(self) -> str:
        """센서 표시용 이름. 기본값은 enum name."""
        return self.name


class VehicleState(_DisplayNameMixin, IntEnum):
    """차량 상태코드."""

    교차로통과 = 0
    정류소도착 = 1
    정류소출발 = 2


class CrowdedLevel(_DisplayNameMixin, IntEnum):
    """차내 혼잡도 단계.

    제공 대상: 일반형시내버스, 따복형시내버스, 일반형농어촌버스.
    """

    정보없음 = 0
    여유 = 1
    보통 = 2
    혼잡 = 3
    매우혼잡 = 4


class RouteFlag(_DisplayNameMixin, StrEnum):
    """노선 운행 상태."""

    운행중 = "RUN"
    경유운행 = "PASS"
    운행종료 = "STOP"
    회차대기 = "WAIT"

    @property
    def display_name(self) -> str:
        if self == RouteFlag.경유운행:
            return "운행중"
        return self.name


class VehicleType(_DisplayNameMixin, IntEnum):
    """특수차량 구분 코드 (lowPlate)."""

    일반버스 = 0
    저상버스 = 1
    이층버스 = 2
    전세버스 = 5
    예약버스 = 6
    트롤리 = 7


class RouteType(IntEnum):
    """노선 유형 코드."""

    CITY_EXPRESS_SEAT = 11
    """직행좌석형 시내버스."""
    CITY_SEAT = 12
    """좌석형 시내버스."""
    CITY_REGULAR = 13
    """일반형 시내버스."""
    CITY_METRO_EXPRESS = 14
    """광역급행형 시내버스."""
    CITY_TTABOK = 15
    """따복형 시내버스."""
    CITY_CIRCULAR = 16
    """경기순환버스."""
    RURAL_EXPRESS_SEAT = 21
    """직행좌석형 농어촌버스."""
    RURAL_SEAT = 22
    """좌석형 농어촌버스."""
    RURAL_REGULAR = 23
    """일반형 농어촌버스."""
    VILLAGE = 30
    """마을버스."""
    INTERCITY_EXPRESS = 41
    """고속형 시외버스."""
    INTERCITY_SEAT = 42
    """좌석형 시외버스."""
    INTERCITY_REGULAR = 43
    """일반형 시외버스."""
    AIRPORT_LIMOUSINE = 51
    """리무진 공항버스."""
    AIRPORT_SEAT = 52
    """좌석형 공항버스."""
    AIRPORT_REGULAR = 53
    """일반형 공항버스."""
