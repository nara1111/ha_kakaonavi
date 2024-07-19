import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN, CONF_APIKEY, CONF_START, CONF_END, CONF_WAYPOINT,
    CONF_UPDATE_INTERVAL, CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL,
    CONF_ROUTE_NAME, CONF_PRIORITY, PRIORITY_OPTIONS, PRIORITY_RECOMMEND
)
from .api import KakaoNaviApiClient

class KakaoNaviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                client = KakaoNaviApiClient(user_input[CONF_APIKEY])
                await self.hass.async_add_executor_job(client.test_api_key)
                await self.async_set_unique_id(user_input[CONF_APIKEY])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Kakao Navi", data=user_input)
            except Exception as e:
                _LOGGER.error(f"Error validating API key: {e}")
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_APIKEY): str,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return KakaoNaviOptionsFlow(config_entry)

class KakaoNaviOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            if user_input.get("add_route", False):
                return await self.async_step_route()
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Required(CONF_UPDATE_INTERVAL, default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
            vol.Required(CONF_FUTURE_UPDATE_INTERVAL, default=self.config_entry.options.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL)): int,
            vol.Optional("add_route", default=False): bool,
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))

    async def async_step_route(self, user_input=None):
        errors = {}
        if user_input is not None:
            routes = list(self.config_entry.options.get("routes", []))
            routes.append(user_input)
            new_options = dict(self.config_entry.options)
            new_options["routes"] = routes
            return self.async_create_entry(title="", data=new_options)

        return self.async_show_form(
            step_id="route",
            data_schema=vol.Schema({
                vol.Required(CONF_ROUTE_NAME): str,
                vol.Required(CONF_START): str,
                vol.Required(CONF_END): str,
                vol.Optional(CONF_WAYPOINT): str,
                vol.Optional(CONF_PRIORITY, default=PRIORITY_RECOMMEND): vol.In(PRIORITY_OPTIONS),
            }),
            errors=errors,
        )
