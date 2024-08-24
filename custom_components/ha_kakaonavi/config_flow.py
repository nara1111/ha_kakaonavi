import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    DOMAIN, CONF_APIKEY, CONF_ROUTE_NAME, CONF_START, CONF_END,
    CONF_WAYPOINT, CONF_PRIORITY, PRIORITY_OPTIONS, PRIORITY_RECOMMEND
)
from .api import KakaoNaviApiClient

class KakaoNaviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                client = KakaoNaviApiClient(user_input[CONF_APIKEY], session)
                await self.hass.async_add_executor_job(client.test_api_key)
                await self.async_set_unique_id(user_input[CONF_APIKEY])
                self._abort_if_unique_id_configured()

                route = {
                    CONF_ROUTE_NAME: user_input[CONF_ROUTE_NAME],
                    CONF_START: user_input[CONF_START],
                    CONF_END: user_input[CONF_END],
                    CONF_WAYPOINT: user_input.get(CONF_WAYPOINT),
                    CONF_PRIORITY: user_input.get(CONF_PRIORITY, PRIORITY_RECOMMEND)
                }

                return self.async_create_entry(
                    title=self.hass.config.location_name,
                    data={CONF_APIKEY: user_input[CONF_APIKEY]},
                    options={"routes": [route]}
                )
            except Exception:
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_APIKEY): str,
                vol.Required(CONF_ROUTE_NAME): str,
                vol.Required(CONF_START): str,
                vol.Required(CONF_END): str,
                vol.Optional(CONF_WAYPOINT): str,
                vol.Optional(CONF_PRIORITY, default=PRIORITY_RECOMMEND): vol.In(PRIORITY_OPTIONS),
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
            return self.async_create_entry(title="", data=user_input)

        routes = self.config_entry.options.get("routes", [])
        if not routes:
            return await self.async_step_add_route()

        return self.async_show_menu(
            step_id="init",
            menu_options={
                "edit_route": self.hass.translator.translate(
                    "options.step.init.menu_options.edit_route"
                ),
                "add_route": self.hass.translator.translate(
                    "options.step.init.menu_options.add_route"
                ),
            }
        )

    async def async_step_edit_route(self, user_input=None):
        errors = {}
        routes = self.config_entry.options.get("routes", [])

        if user_input is not None:
            route_index = next(i for i, route in enumerate(routes) if route[CONF_ROUTE_NAME] == user_input["route_to_edit"])
            edited_route = {
                CONF_ROUTE_NAME: user_input[CONF_ROUTE_NAME],
                CONF_START: user_input[CONF_START],
                CONF_END: user_input[CONF_END],
                CONF_WAYPOINT: user_input.get(CONF_WAYPOINT),
                CONF_PRIORITY: user_input.get(CONF_PRIORITY, PRIORITY_RECOMMEND)
            }
            routes[route_index] = edited_route
            new_options = dict(self.config_entry.options)
            new_options["routes"] = routes
            return self.async_create_entry(title="", data=new_options)

        route_names = [route[CONF_ROUTE_NAME] for route in routes]
        return self.async_show_form(
            step_id="edit_route",
            data_schema=vol.Schema({
                vol.Required("route_to_edit"): vol.In(route_names),
                vol.Required(CONF_ROUTE_NAME): str,
                vol.Required(CONF_START): str,
                vol.Required(CONF_END): str,
                vol.Optional(CONF_WAYPOINT): str,
                vol.Optional(CONF_PRIORITY, default=PRIORITY_RECOMMEND): vol.In(PRIORITY_OPTIONS),
            }),
            errors=errors,
            description_placeholders={"route_names": ", ".join(route_names)}
        )

    async def async_step_add_route(self, user_input=None):
        errors = {}
        if user_input is not None:
            routes = list(self.config_entry.options.get("routes", []))
            routes.append(user_input)
            new_options = dict(self.config_entry.options)
            new_options["routes"] = routes
            return self.async_create_entry(title="", data=new_options)

        return self.async_show_form(
            step_id="add_route",
            data_schema=vol.Schema({
                vol.Required(CONF_ROUTE_NAME): str,
                vol.Required(CONF_START): str,
                vol.Required(CONF_END): str,
                vol.Optional(CONF_WAYPOINT): str,
                vol.Optional(CONF_PRIORITY, default=PRIORITY_RECOMMEND): vol.In(PRIORITY_OPTIONS),
            }),
            errors=errors,
        )