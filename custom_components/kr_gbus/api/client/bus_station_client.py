from pydantic import BaseModel, Field, field_validator

from custom_components.kr_gbus.api.client import _GBusApiClientBase
from ..models import RouteType


class BusStationItem(BaseModel):
    """정류소 기본 정보 항목."""

    center_yn: str = Field(alias="centerYn", description="중앙차로 여부")
    mobile_no: str | None = Field(None, alias="mobileNo", description="정류소 고유모바일번호")
    region_name: str = Field(alias="regionName", description="지역명")
    station_id: int = Field(alias="stationId", description="정류소 아이디")
    station_name: str = Field(alias="stationName", description="정류소명")
    x: float = Field(description="경도 (longitude)")
    y: float = Field(description="위도 (latitude)")

    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    model_config = {"populate_by_name": True}


class BusStationAroundItem(BusStationItem):
    """주변 정류소 항목 (거리 정보 포함)."""

    distance: int = Field(description="거리 (m)")


class BusStationViaRouteItem(BaseModel):
    """정류소 경유 노선 항목."""

    region_name: str = Field(alias="regionName", description="지역명")
    route_dest_id: int = Field(alias="routeDestId", description="진행방향 마지막 정류소 아이디")
    route_dest_name: str = Field(alias="routeDestName", description="진행방향 마지막 정류소명")
    route_id: int = Field(alias="routeId", description="노선 아이디")
    route_name: str = Field(alias="routeName", description="노선명")
    route_type_cd: RouteType | None = Field(None, alias="routeTypeCd", description="노선 유형 코드")
    route_type_name: str | None = Field(None, alias="routeTypeName", description="노선 유형명")
    sta_order: int = Field(alias="staOrder", description="정류소 순번")

    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    model_config = {"populate_by_name": True, "coerce_numbers_to_str": True}


class BusStationResponse(BaseModel):
    """정류소 조회 공통 응답."""

    query_time: str = Field(alias="queryTime", description="정보 요청 시간")
    result_code: int = Field(alias="resultCode", description="결과 코드")
    result_message: str = Field(alias="resultMessage", description="결과 메시지")

    model_config = {"populate_by_name": True}


class BusStationListResponse(BusStationResponse):
    """getBusStationListv2 응답."""

    bus_station_list: list[BusStationItem] | None = Field(
        None, alias="busStationList", description="정류소 목록",
    )


class BusStationAroundListResponse(BusStationResponse):
    """getBusStationAroundListv2 응답."""

    bus_station_around_list: list[BusStationAroundItem] | None = Field(
        None, alias="busStationAroundList", description="주변 정류소 목록",
    )


class BusStationViaRouteListResponse(BusStationResponse):
    """getBusStationViaRouteListv2 응답."""

    bus_route_list: list[BusStationViaRouteItem] | None = Field(
        None, alias="busRouteList", description="경유 노선 목록",
    )


class BusStationInfoResponse(BusStationResponse):
    """busStationInfov2 응답."""

    bus_station_info: BusStationItem | None = Field(
        None, alias="busStationInfo", description="정류소 상세 정보",
    )


class BusStationApiClient(_GBusApiClientBase):
    """정류소 조회 API 클라이언트. (경기도_정류소 조회)"""

    async def async_get_bus_station_list(
        self, keyword: str
    ) -> BusStationListResponse:
        """정류소 목록을 검색한다."""
        data = await self._api_wrapper(
            "/busstationservice/v2/getBusStationListv2",
            params={"keyword": keyword},
        )
        return BusStationListResponse.model_validate(data)

    async def async_get_bus_station_around_list(
        self, x: str, y: str
    ) -> BusStationAroundListResponse:
        """주변 정류소 목록을 조회한다."""
        data = await self._api_wrapper(
            "/busstationservice/v2/getBusStationAroundListv2",
            params={"x": x, "y": y},
        )
        return BusStationAroundListResponse.model_validate(data)

    async def async_get_bus_station_via_route_list(
        self, station_id: str
    ) -> BusStationViaRouteListResponse:
        """정류소 경유 노선 목록을 조회한다."""
        data = await self._api_wrapper(
            "/busstationservice/v2/getBusStationViaRouteListv2",
            params={"stationId": station_id},
        )
        return BusStationViaRouteListResponse.model_validate(data)

    async def async_get_bus_station_info(
        self, station_id: str
    ) -> BusStationInfoResponse:
        """정류소 상세 정보를 조회한다."""
        data = await self._api_wrapper(
            "/busstationservice/v2/busStationInfov2",
            params={"stationId": station_id},
        )
        return BusStationInfoResponse.model_validate(data)
