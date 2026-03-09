from pydantic import BaseModel, Field, field_validator

from custom_components.kr_gbus.api.client import _GBusApiClientBase
from ..models import CrowdedLevel, RouteType, VehicleState, VehicleType


class BusLocationItem(BaseModel):
    """버스 위치정보 항목.

    getBusLocationListv2 응답의 개별 항목.
    """

    route_id: int = Field(alias="routeId", description="노선 아이디")
    route_type_cd: RouteType | None = Field(None, alias="routeTypeCd", description="노선 유형 코드")
    station_id: int = Field(alias="stationId", description="정류소 아이디")
    station_seq: int = Field(alias="stationSeq", description="정류소 순번")
    state_cd: VehicleState | None = Field(None, alias="stateCd", description="상태코드 (0:교차로통과, 1:도착, 2:출발)")
    veh_id: int = Field(alias="vehId", description="차량 아이디")
    plate_no: str | None = Field(None, alias="plateNo", description="차량 번호")
    low_plate: VehicleType | None = Field(None, alias="lowPlate", description="특수차량 구분")
    crowded: CrowdedLevel | None = Field(None, alias="crowded", description="차내 혼잡도")
    remain_seat_cnt: int | None = Field(None, alias="remainSeatCnt", description="빈자리 수 (-1:제공불가)")
    tagless_cd: int | None = Field(None, alias="taglessCd", description="태그리스 서비스 제공여부")

    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    model_config = {"populate_by_name": True, "coerce_numbers_to_str": True}


class BusLocationResponse(BaseModel):
    """버스위치정보 조회 공통 응답."""

    query_time: str = Field(alias="queryTime", description="정보 요청 시간")
    result_code: int = Field(alias="resultCode", description="결과 코드")
    result_message: str = Field(alias="resultMessage", description="결과 메시지")

    model_config = {"populate_by_name": True}


class BusLocationListResponse(BusLocationResponse):
    """getBusLocationListv2 응답."""

    bus_location_list: list[BusLocationItem] | None = Field(
        None,
        alias="busLocationList",
        description="버스 위치정보 목록",
    )


class BusLocationApiClient(_GBusApiClientBase):
    """버스위치정보 조회 API 클라이언트. (경기도_버스위치정보 조회)"""

    async def async_get_bus_location_list(self, route_id: str) -> BusLocationListResponse:
        """노선 버스 위치 목록을 조회한다."""
        data = await self._api_wrapper(
            "/buslocationservice/v2/getBusLocationListv2",
            params={"routeId": route_id},
        )
        return BusLocationListResponse.model_validate(data)
