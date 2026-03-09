from datetime import time
from typing import Any

from pydantic import BaseModel, Field, field_validator

from custom_components.kr_gbus.api.client import _GBusApiClientBase
from ..models import RouteType


def _parse_time(v: str | None) -> time | None:
    """'0530' 또는 '05:30' 형태의 문자열을 time으로 변환한다."""
    if not v:
        return None
    if ":" in v:
        parts = v.split(":")
        return time(int(parts[0]), int(parts[1]))
    return time(int(v[:2]), int(v[2:4]))


class BusRouteInfoItem(BaseModel):
    """노선 상세 정보 항목.

    getBusRouteInfoItemv2 응답의 개별 항목.
    """

    route_id: int = Field(alias="routeId", description="노선 아이디")
    route_name: str = Field(alias="routeName", description="노선명")
    route_type_cd: RouteType | None = Field(None, alias="routeTypeCd", description="노선 유형 코드")
    company_name: str | None = Field(None, alias="companyName", description="운수업체명")
    start_station_name: str | None = Field(None, alias="startStationName", description="기점 정류소명")
    end_station_name: str | None = Field(None, alias="endStationName", description="종점 정류소명")

    # 평일 첫차/막차
    up_first_time: time | None = Field(None, alias="upFirstTime", description="평일 기점 첫차시간")
    up_last_time: time | None = Field(None, alias="upLastTime", description="평일 기점 막차시간")
    down_first_time: time | None = Field(None, alias="downFirstTime", description="평일 종점 첫차시간")
    down_last_time: time | None = Field(None, alias="downLastTime", description="평일 종점 막차시간")

    # 토요일 첫차/막차
    sat_up_first_time: time | None = Field(None, alias="satUpFirstTime", description="토요일 기점 첫차시간")
    sat_up_last_time: time | None = Field(None, alias="satUpLastTime", description="토요일 기점 막차시간")
    sat_down_first_time: time | None = Field(None, alias="satDownFirstTime", description="토요일 종점 첫차시간")
    sat_down_last_time: time | None = Field(None, alias="satDownLastTime", description="토요일 종점 막차시간")

    # 일요일 첫차/막차
    sun_up_first_time: time | None = Field(None, alias="sunUpFirstTime", description="일요일 기점 첫차시간")
    sun_up_last_time: time | None = Field(None, alias="sunUpLastTime", description="일요일 기점 막차시간")
    sun_down_first_time: time | None = Field(None, alias="sunDownFirstTime", description="일요일 종점 첫차시간")
    sun_down_last_time: time | None = Field(None, alias="sunDownLastTime", description="일요일 종점 막차시간")

    # 공휴일 첫차/막차
    we_up_first_time: time | None = Field(None, alias="weUpFirstTime", description="공휴일 기점 첫차시간")
    we_up_last_time: time | None = Field(None, alias="weUpLastTime", description="공휴일 기점 막차시간")
    we_down_first_time: time | None = Field(None, alias="weDownFirstTime", description="공휴일 종점 첫차시간")
    we_down_last_time: time | None = Field(None, alias="weDownLastTime", description="공휴일 종점 막차시간")

    # 배차간격
    peek_alloc: str | None = Field(None, alias="peekAlloc", description="평일 최소 배차시간 (분)")
    n_peek_alloc: str | None = Field(None, alias="nPeekAlloc", description="평일 최대 배차시간 (분)")

    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator(
        "up_first_time", "up_last_time", "down_first_time", "down_last_time",
        "sat_up_first_time", "sat_up_last_time", "sat_down_first_time", "sat_down_last_time",
        "sun_up_first_time", "sun_up_last_time", "sun_down_first_time", "sun_down_last_time",
        "we_up_first_time", "we_up_last_time", "we_down_first_time", "we_down_last_time",
        mode="before",
    )
    @classmethod
    def _parse_time_fields(cls, v):
        if isinstance(v, str) and v:
            return _parse_time(v)
        return v

    model_config = {"populate_by_name": True, "coerce_numbers_to_str": True}


class BusRouteResponse(BaseModel):
    """노선 조회 공통 응답."""

    query_time: str = Field(alias="queryTime", description="정보 요청 시간")
    result_code: int = Field(alias="resultCode", description="결과 코드")
    result_message: str = Field(alias="resultMessage", description="결과 메시지")

    model_config = {"populate_by_name": True}


class BusRouteInfoResponse(BusRouteResponse):
    """getBusRouteInfoItemv2 응답."""

    bus_route_info_item: BusRouteInfoItem | None = Field(
        None,
        alias="busRouteInfoItem",
        description="노선 상세 정보 항목",
    )


class BusRouteApiClient(_GBusApiClientBase):
    """버스노선 조회 API 클라이언트. (경기도_버스노선 조회)"""

    async def async_get_bus_route_list(self, keyword: str) -> Any:
        """노선 목록을 검색한다."""
        return await self._api_wrapper(
            "/busrouteservice/v2/getBusRouteListv2",
            params={"keyword": keyword},
        )

    async def async_get_bus_route_info_item(self, route_id: str) -> BusRouteInfoResponse:
        """노선 상세 정보를 조회한다."""
        data = await self._api_wrapper(
            "/busrouteservice/v2/getBusRouteInfoItemv2",
            params={"routeId": route_id},
        )
        return BusRouteInfoResponse.model_validate(data)

    async def async_get_bus_route_station_list(self, route_id: str) -> Any:
        """노선 경유 정류소 목록을 조회한다."""
        return await self._api_wrapper(
            "/busrouteservice/v2/getBusRouteStationListv2",
            params={"routeId": route_id},
        )

    async def async_get_bus_route_line_list(self, route_id: str) -> Any:
        """노선 좌표 목록을 조회한다."""
        return await self._api_wrapper(
            "/busrouteservice/v2/getBusRouteLineListv2",
            params={"routeId": route_id},
        )
