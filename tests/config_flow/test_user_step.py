"""async_step_user 테스트."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.kr_gbus.api.exceptions import (
    GBusApiClientAuthenticationError,
    GBusApiClientCommunicationError,
)
from custom_components.kr_gbus.const import DOMAIN

VALIDATE_API_KEY_PATH = (
    "custom_components.kr_gbus.config_flow_handler.config_flow.validate_api_key"
)


@pytest.fixture
async def user_flow(hass: HomeAssistant) -> dict:
    """user flow를 시작하고 첫 폼을 반환한다."""
    user_flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert user_flow["type"] is FlowResultType.FORM
    assert user_flow["step_id"] == config_entries.SOURCE_USER
    assert not user_flow["errors"]
    return user_flow


async def test_success_creates_entry(
        hass: HomeAssistant,
        user_flow: dict,
        mock_api_keys: dict[str, str],
) -> None:
    """유효한 API 키 입력 시 config entry가 생성된다."""
    with patch(VALIDATE_API_KEY_PATH) as mock:
        result = await hass.config_entries.flow.async_configure(
            user_flow["flow_id"],
            user_input=mock_api_keys,
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "경기버스정보"
    assert result["data"]["api_key_arrival"] == mock_api_keys["api_key_arrival"]
    mock.assert_awaited_once_with(hass, service_key=mock_api_keys["api_key_arrival"])


async def test_auth_error(
        hass: HomeAssistant,
        user_flow: dict,
        mock_api_keys: dict[str, str],
) -> None:
    """인증 실패 시 auth 에러를 보여준다."""
    with patch(
            VALIDATE_API_KEY_PATH,
            side_effect=GBusApiClientAuthenticationError,
    ):
        user_flow = await hass.config_entries.flow.async_configure(
            user_flow["flow_id"],
            user_input=mock_api_keys,
        )

    assert user_flow["type"] is FlowResultType.FORM
    assert user_flow["errors"]["base"] == "auth"


async def test_connection_error(
        hass: HomeAssistant,
        user_flow: dict,
        mock_api_keys: dict[str, str],
) -> None:
    """통신 실패 시 connection 에러를 보여준다."""
    with patch(
            VALIDATE_API_KEY_PATH,
            side_effect=GBusApiClientCommunicationError,
    ):
        user_flow = await hass.config_entries.flow.async_configure(
            user_flow["flow_id"],
            user_input=mock_api_keys,
        )

    assert user_flow["type"] is FlowResultType.FORM
    assert user_flow["errors"]["base"] == "connection"


async def test_unknown_error(
        hass: HomeAssistant,
        user_flow: dict,
        mock_api_keys: dict[str, str],
) -> None:
    """알 수 없는 예외 시 unknown 에러를 보여준다."""
    with patch(
            VALIDATE_API_KEY_PATH,
            side_effect=RuntimeError("unexpected"),
    ):
        user_flow = await hass.config_entries.flow.async_configure(
            user_flow["flow_id"],
            user_input=mock_api_keys,
        )

    assert user_flow["type"] is FlowResultType.FORM
    assert user_flow["errors"]["base"] == "unknown"
