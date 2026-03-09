import aiohttp

from ..exceptions import GBusApiClientAuthenticationError


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """응답 상태를 검증한다."""
    if response.status in (401, 403):
        msg = "Invalid API key"
        raise GBusApiClientAuthenticationError(msg)
    response.raise_for_status()
