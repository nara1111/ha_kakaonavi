from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from datetime import timedelta
from .const import (
    DOMAIN, CONF_APIKEY, CONF_ROUTE_NAME, CONF_START, CONF_END, CONF_WAYPOINT,
    CONF_PRIORITY, PRIORITY_OPTIONS, PRIORITY_RECOMMEND,
    CONF_UPDATE_INTERVAL, CONF_FUTURE_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL, CONF_ROUTES
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
                await self.async_set_unique_id(f"{user_input[CONF_APIKEY]}_{user_input[CONF_ROUTE_NAME]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_ROUTE_NAME],
                    data={
                        CONF_APIKEY: user_input[CONF_APIKEY],
                    },
                    options={
                        CONF_ROUTES: [{
                            CONF_ROUTE_NAME: user_input[CONF_ROUTE_NAME],
                            CONF_START: user_input[CONF_START],
                            CONF_END: user_input[CONF_END],
                            CONF_WAYPOINT: user_input.get(CONF_WAYPOINT),
                            CONF_PRIORITY: user_input.get(CONF_PRIORITY, PRIORITY_RECOMMEND)
                        }],
                        CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL,
                        CONF_FUTURE_UPDATE_INTERVAL: DEFAULT_FUTURE_UPDATE_INTERVAL,
                    }
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
            if user_input.get("next_step") == "edit_route":
                return await self.async_step_edit_route()
            elif user_input.get("next_step") == "update_intervals":
                return await self.async_step_update_intervals()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("next_step"): vol.In({
                    "edit_route": "Edit Route",
                    "update_intervals": "Update Intervals"
                })
            })
        )

    async def async_step_update_intervals(self, user_input=None):
        if user_input is not None:
            new_options = dict(self.config_entry.options)
            new_options[CONF_UPDATE_INTERVAL] = user_input[CONF_UPDATE_INTERVAL]
            new_options[CONF_FUTURE_UPDATE_INTERVAL] = user_input[CONF_FUTURE_UPDATE_INTERVAL]

            # Update the coordinator
            hass = self.hass
            entry = self.config_entry
            coordinators = hass.data[DOMAIN][entry.entry_id]

            for coordinator in coordinators.values():
                coordinator.set_update_interval(user_input[CONF_UPDATE_INTERVAL])
                coordinator.set_future_update_interval(user_input[CONF_FUTURE_UPDATE_INTERVAL])

            return self.async_create_entry(title="", data=new_options)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="update_intervals",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL,
                             default=options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): vol.All(
                    vol.Coerce(int), vol.Range(min=1)),
                vol.Required(CONF_FUTURE_UPDATE_INTERVAL,
                             default=options.get(CONF_FUTURE_UPDATE_INTERVAL, DEFAULT_FUTURE_UPDATE_INTERVAL)): vol.All(
                    vol.Coerce(int), vol.Range(min=1)),
            }),
        )

    async def async_step_edit_route(self, user_input=None):
        errors = {}
        routes = self.config_entry.options.get(CONF_ROUTES, [])

        if user_input is not None:
            if "route_to_edit" in user_input:
                route_to_edit = user_input.pop("route_to_edit")
                route_index = next((i for i, route in enumerate(routes) if route[CONF_ROUTE_NAME] == route_to_edit),
                                   None)
                if route_index is not None:
                    routes[route_index] = user_input
                else:
                    routes.append(user_input)
            else:
                routes.append(user_input)

            new_options = dict(self.config_entry.options)
            new_options[CONF_ROUTES] = routes
            return self.async_create_entry(title="", data=new_options)

        route_names = [route[CONF_ROUTE_NAME] for route in routes]
        route_names.append("Add new route")

        if not routes:
            return self.async_show_form(
                step_id="edit_route",
                data_schema=vol.Schema({
                    vol.Required(CONF_ROUTE_NAME): str,
                    vol.Required(CONF_START): str,
                    vol.Required(CONF_END): str,
                    vol.Optional(CONF_WAYPOINT): str,
                    vol.Optional(CONF_PRIORITY, default=PRIORITY_RECOMMEND): vol.In(PRIORITY_OPTIONS),
                }),
                errors=errors,
            )

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
        )