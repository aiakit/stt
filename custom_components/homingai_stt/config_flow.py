"""Config flow for HomingAI STT integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): str,
        vol.Required(CONF_CLIENT_SECRET): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """验证用户输入的配置。"""
    session = async_get_clientsession(hass)

    try:
        async with session.post(
                "https://api.homingai.com/ha/home/validate",
                json={
                    "client_id": data[CONF_CLIENT_ID],
                    "client_secret": data[CONF_CLIENT_SECRET],
                },
        ) as response:
            if response.status != 200:
                raise InvalidAuth

            result = await response.json()
            # 检查返回的 code 字段
            if result.get("code") != 200:
                raise InvalidAuth

    except aiohttp.ClientError as err:
        _LOGGER.error("连接到 HomingAI STT API 失败: %s", err)
        raise CannotConnect from err


class HomingAISTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HomingAI STT."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # 创建唯一ID，防止重复配置
                await self.async_set_unique_id(user_input[CONF_CLIENT_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="HomingAI STT",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle reauthorization."""
        return await self.async_step_user()


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
