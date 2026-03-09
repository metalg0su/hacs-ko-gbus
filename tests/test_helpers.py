"""helpers 모듈 테스트."""

from datetime import date, time

import pytest

from custom_components.kr_gbus.helpers import DayType, get_day_type, is_operating


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        # 2026-03-30 = 월요일
        (date(2026, 3, 30), DayType.WEEKDAY),
        # 2026-03-28 = 토요일
        (date(2026, 3, 28), DayType.SATURDAY),
        # 2026-03-29 = 일요일
        (date(2026, 3, 29), DayType.SUNDAY),
        # 2026-01-01 = 신정 (목요일이지만 공휴일)
        (date(2026, 1, 1), DayType.HOLIDAY),
        # 2026-05-05 = 어린이날 (화요일이지만 공휴일)
        (date(2026, 5, 5), DayType.HOLIDAY),
        # 2026-10-03 = 개천절 (토요일 + 공휴일 → 공휴일 우선)
        (date(2026, 10, 3), DayType.HOLIDAY),
    ],
)
def test_get_day_type(d: date, expected: DayType):
    assert get_day_type(d) == expected


class TestIsOperating:
    """is_operating 테스트."""

    def test_within_hours(self):
        assert is_operating(time(5, 30), time(23, 0), time(12, 0)) is True

    def test_before_first_bus(self):
        assert is_operating(time(5, 30), time(23, 0), time(4, 0)) is False

    def test_after_last_bus(self):
        assert is_operating(time(5, 30), time(23, 0), time(23, 30)) is False

    def test_at_first_bus(self):
        assert is_operating(time(5, 30), time(23, 0), time(5, 30)) is True

    def test_at_last_bus(self):
        assert is_operating(time(5, 30), time(23, 0), time(23, 0)) is True

    def test_cross_midnight_during_night(self):
        """자정 넘김: 첫차 22:00, 막차 01:00 → 23:30은 운행 중."""
        assert is_operating(time(22, 0), time(1, 0), time(23, 30)) is True

    def test_cross_midnight_after_last(self):
        """자정 넘김: 첫차 22:00, 막차 01:00 → 02:00은 운행 종료."""
        assert is_operating(time(22, 0), time(1, 0), time(2, 0)) is False

    def test_cross_midnight_before_first(self):
        """자정 넘김: 첫차 22:00, 막차 01:00 → 15:00은 운행 종료."""
        assert is_operating(time(22, 0), time(1, 0), time(15, 0)) is False

    def test_cross_midnight_at_midnight(self):
        """자정 넘김: 자정은 운행 중."""
        assert is_operating(time(22, 0), time(1, 0), time(0, 0)) is True

    def test_first_none_returns_true(self):
        assert is_operating(None, time(23, 0), time(12, 0)) is True

    def test_last_none_returns_true(self):
        assert is_operating(time(5, 30), None, time(12, 0)) is True

    def test_both_none_returns_true(self):
        assert is_operating(None, None, time(12, 0)) is True
