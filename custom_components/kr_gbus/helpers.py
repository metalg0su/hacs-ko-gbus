"""kr_gbus 공통 헬퍼."""

from __future__ import annotations

from datetime import date, time
from enum import StrEnum
from typing import TYPE_CHECKING

import holidays

if TYPE_CHECKING:
    from .api.client.bus_route_client import BusRouteInfoItem


class DayType(StrEnum):
    """요일 구분."""

    WEEKDAY = "평일"
    SATURDAY = "토요일"
    SUNDAY = "일요일"
    HOLIDAY = "공휴일"


# 모듈 로드 시점에 holidays 내부 모듈을 미리 import하여
# 이벤트 루프 안에서 blocking import_module 호출을 방지한다.
_kr_holidays: holidays.HolidayBase = holidays.KR(years=date.today().year)


def _get_kr_holidays(year: int) -> holidays.HolidayBase:
    """한국 공휴일 인스턴스를 반환한다 (연도별 캐싱)."""
    global _kr_holidays
    if year not in _kr_holidays.years:
        _kr_holidays = holidays.KR(years=_kr_holidays.years | {year})
    return _kr_holidays


def get_day_type(d: date) -> DayType:
    """날짜의 요일 구분을 반환한다."""
    if d in _get_kr_holidays(d.year):
        return DayType.HOLIDAY
    if d.weekday() == 5:
        return DayType.SATURDAY
    if d.weekday() == 6:
        return DayType.SUNDAY
    return DayType.WEEKDAY


_FIRST_TIME_FIELDS: dict[DayType, str] = {
    DayType.WEEKDAY: "up_first_time",
    DayType.SATURDAY: "sat_up_first_time",
    DayType.SUNDAY: "sun_up_first_time",
    DayType.HOLIDAY: "we_up_first_time",
}

_LAST_TIME_FIELDS: dict[DayType, str] = {
    DayType.WEEKDAY: "down_last_time",
    DayType.SATURDAY: "sat_down_last_time",
    DayType.SUNDAY: "sun_down_last_time",
    DayType.HOLIDAY: "we_down_last_time",
}


def get_schedule_times(
    info: BusRouteInfoItem, day_type: DayType
) -> tuple[time | None, time | None]:
    """해당 day_type의 (기점 첫차, 종점 막차)를 반환한다."""
    first = getattr(info, _FIRST_TIME_FIELDS[day_type], None)
    last = getattr(info, _LAST_TIME_FIELDS[day_type], None)
    return first, last


def is_operating(first: time | None, last: time | None, now: time) -> bool:
    """현재 시각이 운행 시간 내인지 판별한다.

    first 또는 last가 None이면 안전하게 True(운행 중)를 반환한다.
    last < first인 경우 자정을 넘기는 노선으로 간주한다.
    """
    if first is None or last is None:
        return True
    if last < first:
        # 자정 넘김: 첫차 이후이거나 막차 이전이면 운행 중
        return now >= first or now <= last
    return first <= now <= last
