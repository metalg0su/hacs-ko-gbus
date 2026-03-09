from pydantic import BaseModel, Field, field_validator

from custom_components.kr_gbus.api.client import _GBusApiClientBase
from ..models import (
    CrowdedLevel,
    RouteFlag,
    RouteType,
    VehicleState,
    VehicleType,
)


class BusArrivalItem(BaseModel):
    """버스 도착정보 항목.

    getBusArrivalListv2 / getBusArrivalItemv2 응답의 개별 항목.
    """

    flag: RouteFlag | None = Field(None, description="노선 운행 상태 (RUN/PASS/STOP/WAIT)")
    route_id: int = Field(alias="routeId", description="노선 아이디")
    route_name: str = Field(alias="routeName", description="노선명")
    route_type_cd: RouteType | None = Field(None, alias="routeTypeCd", description="노선 유형 코드")
    route_dest_id: int | None = Field(None, alias="routeDestId", description="진행방향 마지막 정류소 아이디")
    route_dest_name: str | None = Field(None, alias="routeDestName", description="진행방향 마지막 정류소명")
    sta_order: int = Field(alias="staOrder", description="정류소 순번")
    station_id: int = Field(alias="stationId", description="정류소 아이디")
    turn_seq: int | None = Field(None, alias="turnSeq", description="노선의 회차점 순번")

    # 첫번째 차량
    state_cd1: VehicleState | None = Field(None, alias="stateCd1", description="첫번째 차량 상태코드")
    predict_time1: int | None = Field(None, alias="predictTime1", description="첫번째 차량 도착예상시간 (분)")
    predict_time_sec1: int | None = Field(None, alias="predictTimeSec1", description="첫번째 차량 도착예상시간 (초)")
    location_no1: int | None = Field(None, alias="locationNo1", description="첫번째 차량 위치 (몇 번째 전 정류소)")
    plate_no1: str | None = Field(None, alias="plateNo1", description="첫번째 차량 번호")
    low_plate1: VehicleType | None = Field(None, alias="lowPlate1", description="첫번째 차량 특수차량 구분")
    crowded1: CrowdedLevel | None = Field(None, alias="crowded1", description="첫번째 차량 차내혼잡도")
    remain_seat_cnt1: int | None = Field(None, alias="remainSeatCnt1", description="첫번째 차량 빈자리 수")
    station_nm1: str | None = Field(None, alias="stationNm1", description="첫번째 차량 위치 정류소명")
    tagless_cd1: int | None = Field(None, alias="taglessCd1", description="첫번째 차량 태그리스 서비스 제공여부")
    veh_id1: int | None = Field(None, alias="vehId1", description="첫번째 차량 아이디")

    # 두번째 차량
    state_cd2: VehicleState | None = Field(None, alias="stateCd2", description="두번째 차량 상태코드")
    predict_time2: int | None = Field(None, alias="predictTime2", description="두번째 차량 도착예상시간 (분)")
    predict_time_sec2: int | None = Field(None, alias="predictTimeSec2", description="두번째 차량 도착예상시간 (초)")
    location_no2: int | None = Field(None, alias="locationNo2", description="두번째 차량 위치 (몇 번째 전 정류소)")
    plate_no2: str | None = Field(None, alias="plateNo2", description="두번째 차량 번호")
    low_plate2: VehicleType | None = Field(None, alias="lowPlate2", description="두번째 차량 특수차량 구분")
    crowded2: CrowdedLevel | None = Field(None, alias="crowded2", description="두번째 차량 차내혼잡도")
    remain_seat_cnt2: int | None = Field(None, alias="remainSeatCnt2", description="두번째 차량 빈자리 수")
    station_nm2: str | None = Field(None, alias="stationNm2", description="두번째 차량 위치 정류소명")
    tagless_cd2: int | None = Field(None, alias="taglessCd2", description="두번째 차량 태그리스 서비스 제공여부")
    veh_id2: int | None = Field(None, alias="vehId2", description="두번째 차량 아이디")

    # data.go.kr API는 값이 없는 필드에 빈 문자열("")을 반환한다.
    # int/enum 필드에서 파싱 에러가 나지 않도록 None으로 변환한다.
    @field_validator("*", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    model_config = {"populate_by_name": True, "coerce_numbers_to_str": True}


class BusArrivalResponse(BaseModel):
    """getBusArrivalListv2 / getBusArrivalItemv2 공통 응답."""

    query_time: str = Field(alias="queryTime", description="정보 요청 시간")
    result_code: int = Field(alias="resultCode", description="결과 코드")
    result_message: str = Field(alias="resultMessage", description="결과 메시지")

    model_config = {"populate_by_name": True}


class BusArrivalListResponse(BusArrivalResponse):
    """getBusArrivalListv2 응답."""

    bus_arrival_list: list[BusArrivalItem] | None = Field(
        None,
        alias="busArrivalList",
        description="버스 도착정보 목록 (단건이면 dict, 복수건이면 list)",
    )


class BusArrivalItemResponse(BusArrivalResponse):
    """getBusArrivalItemv2 응답."""

    bus_arrival_item: BusArrivalItem | None = Field(
        None,
        alias="busArrivalItem",
        description="버스 도착정보 항목",
    )


class BusArrivalApiClient(_GBusApiClientBase):
    """버스도착정보 조회 API 클라이언트. (경기도_버스도착정보 조회)
    > https://www.gbis.go.kr/gbis2014/publicService.action?cmd=mBusArrivalStation
    """

    async def async_get_bus_arrival_list(
        self, station_id: str
    ) -> BusArrivalListResponse:
        """정류소 도착 정보 목록을 조회한다."""
        data = await self._api_wrapper(
            "/busarrivalservice/v2/getBusArrivalListv2",
            params={"stationId": station_id},
        )
        return BusArrivalListResponse.model_validate(data)

    async def async_get_bus_arrival_item(
        self, station_id: str, route_id: str, sta_order: str
    ) -> BusArrivalItemResponse:
        """특정 노선 도착 정보를 조회한다."""
        data = await self._api_wrapper(
            "/busarrivalservice/v2/getBusArrivalItemv2",
            params={
                "stationId": station_id,
                "routeId": route_id,
                "staOrder": sta_order,
            },
        )
        return BusArrivalItemResponse.model_validate(data)
