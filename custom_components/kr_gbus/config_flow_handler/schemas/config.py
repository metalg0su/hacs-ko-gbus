"""config flow 스키마."""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.helpers import selector

from ...const import CONF_API_KEY_ARRIVAL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS

_PASSWORD_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
)


def _build_api_key_schema(
    defaults: Mapping[str, Any] | None = None,
) -> vol.Schema:
    """API 키 입력 스키마를 생성한다."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_API_KEY_ARRIVAL,
                default=defaults.get(CONF_API_KEY_ARRIVAL, vol.UNDEFINED),
            ): _PASSWORD_SELECTOR,
        },
    )


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """사용자 설정 스키마."""
    defaults = defaults or {}
    schema = _build_api_key_schema(defaults)
    return schema.extend(
        {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=30,
                    max=3600,
                    step=10,
                    unit_of_measurement="초",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
        },
    )


def get_reconfigure_schema() -> vol.Schema:
    """재설정 스키마."""
    return _build_api_key_schema()


def get_reauth_schema() -> vol.Schema:
    """재인증 스키마."""
    return _build_api_key_schema()
