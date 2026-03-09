"""테스트 공통 fixtures."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    MockModule,
    MockPlatform,
    mock_config_flow,
    mock_integration,
    mock_platform,
)

from custom_components.kr_gbus.config_flow_handler.config_flow import (
    GBusConfigFlowHandler,
)
from custom_components.kr_gbus.const import (
    CONF_API_KEY_ARRIVAL,
    DOMAIN,
)

MOCK_API_KEYS = {
    CONF_API_KEY_ARRIVAL: "test_arrival_key",
}


@pytest.fixture
def mock_api_keys() -> dict[str, str]:
    """Mock API 키 데이터."""
    return dict(MOCK_API_KEYS)


@pytest.fixture(autouse=True)
def register_integration(hass: HomeAssistant):
    """kr_gbus integration을 hass에 등록한다."""
    async def _async_setup_entry(*_):
        return True

    mock_integration(hass, MockModule(DOMAIN, async_setup_entry=_async_setup_entry))
    mock_platform(hass, f"{DOMAIN}.config_flow", MockPlatform())
    with mock_config_flow(DOMAIN, GBusConfigFlowHandler):
        yield
