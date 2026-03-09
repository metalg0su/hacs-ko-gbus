"""센서 헬퍼 함수 테스트."""

from datetime import time

from custom_components.kr_gbus.api.client.bus_route_client import BusRouteInfoItem
from custom_components.kr_gbus.helpers import DayType
from custom_components.kr_gbus.sensor.descriptions import _time_value, _time_attrs


def _make_route_info(**kwargs) -> BusRouteInfoItem:
    """테스트용 BusRouteInfoItem을 생성한다."""
    defaults = {
        "routeId": 1,
        "routeName": "테스트",
        "upFirstTime": "0530",
        "upLastTime": "2230",
        "downFirstTime": "0600",
        "downLastTime": "2300",
        "satUpFirstTime": "0600",
        "satUpLastTime": "2200",
        "satDownFirstTime": "0630",
        "satDownLastTime": "2230",
        "sunUpFirstTime": "0700",
        "sunUpLastTime": "2100",
        "sunDownFirstTime": "0730",
        "sunDownLastTime": "2130",
        "weUpFirstTime": "0700",
        "weDownFirstTime": "0730",
        "weDownLastTime": "2130",
    }
    defaults.update(kwargs)
    return BusRouteInfoItem.model_validate(defaults)


class TestTimeValue:
    """_time_value 테스트."""

    def test_weekday(self):
        info = _make_route_info()
        assert _time_value(info, DayType.WEEKDAY, "up_first_time") == time(5, 30)
        assert _time_value(info, DayType.WEEKDAY, "down_last_time") == time(23, 0)

    def test_saturday(self):
        info = _make_route_info()
        assert _time_value(info, DayType.SATURDAY, "up_first_time") == time(6, 0)
        assert _time_value(info, DayType.SATURDAY, "down_last_time") == time(22, 30)

    def test_sunday(self):
        info = _make_route_info()
        assert _time_value(info, DayType.SUNDAY, "up_first_time") == time(7, 0)

    def test_holiday(self):
        info = _make_route_info()
        assert _time_value(info, DayType.HOLIDAY, "up_first_time") == time(7, 0)
        assert _time_value(info, DayType.HOLIDAY, "down_last_time") == time(21, 30)

    def test_missing_field_returns_none(self):
        info = _make_route_info(weUpFirstTime="")
        assert _time_value(info, DayType.HOLIDAY, "up_first_time") is None


class TestTimeAttrs:
    """_time_attrs 테스트."""

    def test_returns_all_day_types(self):
        info = _make_route_info()
        attrs = _time_attrs(info, "up_first_time")
        assert attrs == {
            "평일": time(5, 30),
            "토요일": time(6, 0),
            "일요일": time(7, 0),
            "공휴일": time(7, 0),
        }

    def test_none_values(self):
        info = _make_route_info(satUpFirstTime="", sunUpFirstTime="")
        attrs = _time_attrs(info, "up_first_time")
        assert attrs["평일"] == time(5, 30)
        assert attrs["토요일"] is None
        assert attrs["일요일"] is None
