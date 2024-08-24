import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN, CONF_APIKEY, CONF_ROUTE_NAME, CONF_START, CONF_END, CONF_WAYPOINT,
    CONF_PRIORITY, PRIORITY_OPTIONS, PRIORITY_RECOMMEND,
    CONF_UPDATE_INTERVAL, CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL
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

                unique_id = f"{user_input[CONF_APIKEY]}_{user_input[CONF_ROUTE_NAME]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                route = {
                    CONF_ROUTE_NAME: user_input[CONF_ROUTE_NAME],
                    CONF_START: user_input[CONF_START],
                    CONF_END: user_input[CONF_END],
                    CONF_WAYPOINT: user_input.get(CONF_WAYPOINT),
                    CONF_PRIORITY: user_input.get(CONF_PRIORITY, PRIORITY_RECOMMEND)
                }

                return self.async_create_entry(
                    title=f"{user_input[CONF_ROUTE_NAME]}",
                    data={CONF_APIKEY: user_input[CONF_APIKEY], **route},
                    options={
                        CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL,
                        CONF_FUTURE_UPDATE_INTERVAL: DEFAULT_FUTURE_UPDATE_INTERVAL,
                    }
                )
            except Exception as e:
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
                "edit_route": "Edit existing route",
                "add_route": "Add new route"
            }
        )

    async def async_step_edit_route(self, user_input=None):
        errors = {}
        routes = self.config_entry.options.get("routes", [])

        if user_input is not None:
            route_to_edit = user_input.pop("route_to_edit")
            route_index = next(i for i, route in enumerate(routes) if route[CONF_ROUTE_NAME] == route_to_edit)
            routes[route_index] = user_input
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