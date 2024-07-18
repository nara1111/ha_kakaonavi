import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_APIKEY, CONF_ROUTES, CONF_UPDATE_INTERVAL, CONF_FUTURE_UPDATE_INTERVAL
from .api import KakaoNaviApiClient

class KakaoNaviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self.api_key = None
        self.routes = []

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            valid = await self.hass.async_add_executor_job(
                self._test_api_key, user_input[CONF_APIKEY]
            )
            if valid:
                self.api_key = user_input[CONF_APIKEY]
                return await self.async_step_route()
            else:
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_APIKEY): str}),
            errors=errors,
        )

    async def async_step_route(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.routes.append(user_input)
            if user_input.get("add_another", False):
                return await self.async_step_route()
            else:
                return await self.async_step_options()

        return self.async_show_form(
            step_id="route",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("start"): str,
                vol.Required("end"): str,
                vol.Optional("waypoint"): str,
                vol.Optional("add_another", default=False): bool,
            }),
            errors=errors,
        )

    async def async_step_options(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Kakao Navi",
                data={
                    CONF_APIKEY: self.api_key,
                    CONF_ROUTES: self.routes,
                    CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
                    CONF_FUTURE_UPDATE_INTERVAL: user_input[CONF_FUTURE_UPDATE_INTERVAL],
                },
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL, default=10): int,
                vol.Required(CONF_FUTURE_UPDATE_INTERVAL, default=60): int,
            }),
        )

    def _test_api_key(self, api_key):
        client = KakaoNaviApiClient(api_key)
        # API 키 유효성 검사 로직 구현
        # 예: 간단한 API 호출을 수행하고 성공 여부 확인
        return True  # 임시로 True 반환

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return KakaoNaviOptionsFlow(config_entry)

class KakaoNaviOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL, default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, 10)): int,
                vol.Required(CONF_FUTURE_UPDATE_INTERVAL, default=self.config_entry.options.get(CONF_FUTURE_UPDATE_INTERVAL, 60)): int,
            }),
        )
