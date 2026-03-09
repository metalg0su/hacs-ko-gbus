"""kr_gbus API 클라이언트."""

from typing import Any

from .base import _GBusApiClientBase
from .bus_location_client import BusLocationApiClient


class BaseInfoApiClient(_GBusApiClientBase):
    """기반정보 관리 API 클라이언트. (경기도_기반정보 관리)"""

    async def async_get_base_info_item(self) -> Any:
        """기반 정보를 조회한다."""
        return await self._api_wrapper(
            "/baseinfoservice/v2/getBaseInfoItemv2",
        )

    async def async_get_data(self) -> Any:
        """코디네이터가 호출하는 데이터 갱신 메서드."""
        return await self.async_get_base_info_item()
