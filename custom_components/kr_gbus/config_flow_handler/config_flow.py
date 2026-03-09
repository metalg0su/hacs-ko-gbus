"""kr_gbus config flow 핸들러."""

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import callback

from .options_flow import GBusOptionsFlowHandler
from .schemas import (
    get_user_schema,
)
from .validators import validate_api_key
from ..const import CONF_API_KEY_ARRIVAL, DOMAIN, LOGGER

ERROR_MAP = {
    "GBusApiClientAuthenticationError": "auth",
    "GBusApiClientCommunicationError": "connection",
}


class GBusConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """kr_gbus 설정 플로우."""

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """옵션 플로우 핸들러를 반환한다."""
        return GBusOptionsFlowHandler(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """사용자 설정 단계."""
        errors: dict[str, str] = {}

        if not user_input:
            return self.async_show_form(
                step_id="user",
                data_schema=get_user_schema(user_input),
                errors=errors,
            )

        try:
            await validate_api_key(
                self.hass,
                service_key=user_input[CONF_API_KEY_ARRIVAL],
            )
        except Exception as exception:  # noqa: BLE001
            errors["base"] = self._map_exception_to_error(exception)
        else:
            await self.async_set_unique_id(
                user_input[CONF_API_KEY_ARRIVAL][:8]
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="경기버스정보",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
        )

    def _map_exception_to_error(self, exception: Exception) -> str:
        """예외를 에러 키로 변환한다."""
        LOGGER.warning("Config flow 에러: %s", exception)
        return ERROR_MAP.get(type(exception).__name__, "unknown")
