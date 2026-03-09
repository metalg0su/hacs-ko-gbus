import asyncio
import socket
from typing import Any

import aiohttp

from custom_components.kr_gbus.api.client.helpers import _verify_response_or_raise
from ..exceptions import GBusApiClientError, GBusApiClientCommunicationError


class _GBusApiClientBase:
    """API 클라이언트 베이스. 각 API 그룹 클라이언트가 상속한다."""

    def __init__(
            self,
            service_key: str,
            session: aiohttp.ClientSession,
    ) -> None:
        self._service_key = service_key
        self._session = session

    async def _api_wrapper(
            self,
            path: str,
            params: dict[str, Any] | None = None,
    ) -> Any:
        """API 요청을 실행하고 에러를 처리한다."""
        request_params: dict[str, Any] = {
            "serviceKey": self._service_key,
            "format": "json",
        }
        if params:
            request_params.update(params)

        try:
            async with asyncio.timeout(10):
                response = await self._session.request(
                    method="get",
                    url=f"https://apis.data.go.kr/6410000{path}",
                    params=request_params,
                )
                _verify_response_or_raise(response)
                data = await response.json()

                # data.go.kr 응답은 {response: {comMsgHeader, msgHeader, msgBody}} 중첩 구조.
                # 원본 swagger 스펙에는 이 래퍼가 누락되어 있어 build_api.sh에서 보정한다.
                # 여기서는 msgHeader + msgBody를 병합하여 Pydantic 모델이 플랫하게 사용할 수 있게 한다.
                inner = data.get("response", data)
                return {**inner.get("msgHeader", {}), **inner.get("msgBody", {})}

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise GBusApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise GBusApiClientCommunicationError(msg) from exception
        except GBusApiClientError:
            raise
        except Exception as exception:
            msg = f"Unexpected error - {exception}"
            raise GBusApiClientError(msg) from exception
