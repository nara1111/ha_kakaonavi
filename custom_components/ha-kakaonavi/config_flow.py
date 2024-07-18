import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from .const import (  # 이 줄을 수정했습니다. 'ffrom'을 'from'으로 변경
    DOMAIN,
    CONF_APIKEY,
    CONF_START,
    CONF_END,
    CONF_WAYPOINT,
    CONF_UPDATE_INTERVAL,
    CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_FUTURE_UPDATE_INTERVAL
)

class KakaoNaviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # Here you could add validation for the API key
            return self.async_create_entry(title="Kakao Navi", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_APIKEY): str,
                vol.Required(CONF_START): str,
                vol.Required(CONF_END): str,
                vol.Optional(CONF_WAYPOINT): str,
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                vol.Optional(CONF_FUTURE_UPDATE_INTERVAL, default=DEFAULT_FUTURE_UPDATE_INTERVAL): int,
            }),
            errors=errors,
        )