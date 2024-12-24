"""Config flow for HomingAI integration."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN,TITLE

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HomingAI"""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.code = None
        self.state = None

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        auth_url = None

        # 只在首次加载或没有code时获取授权URL
        if not hasattr(self, 'code') or not self.code:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            "https://api.homingai.com/ha/home/oauthcode",
                            json={}
                    ) as response:
                        result = await response.json()
                        if result.get("code") == 200:
                            self.code = result["data"]["code"]
                            self.state = result["data"]["state"]
                        else:
                            errors["base"] = "auth_error"
            except Exception as err:
                _LOGGER.error("Failed to get auth code: %s", err)
                errors["base"] = "auth_error"

        # 如果有code，生成auth_url
        if hasattr(self, 'code') and self.code:
            auth_url = f"https://homingai.com/oauth?code={self.code}&state={self.state}"

        # 如果用户点击了提交按钮
        if user_input is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            "https://api.homingai.com/ha/home/gettoken",
                            json={
                                "code": self.code,
                                "state": self.state
                            }
                    ) as response:
                        result = await response.json()
                        if result.get("code") == 200:
                            return self.async_create_entry(
                                title=TITLE,
                                data={
                                    "access_token": result["data"]["access_token"]
                                }
                            )
                        else:
                            errors["base"] = "auth_verify_failed"
            except Exception as err:
                _LOGGER.error("Failed to verify auth: %s", err)
                errors["base"] = "auth_verify_failed"

        risks_text = """
请注意以下风险提示：

1. 您的用户信息和设备信息将会存储在您的 Home Assistant 系统中，我们无法保证 Home Assistant 存储机制的安全性。您需要负责防止您的信息被窃取。

2. 此集成由HomingAI开发维护，可能会出现稳定性问题或其它问题，使用此集成遇到相关问题时，您应当向开源社区寻求帮助。

3. 在使用此集成前，请仔细阅读README。

4. 为了用户能够稳定地使用集成，避免接口被滥用，此集成仅允许在 Home Assistant 使用，详情请参考LICENSE。

请点击下方的提交按钮，然后在打开的网页中完成授权：
[点击此处去HomingAI官网授权]({auth_url})
"""

        return self.async_show_form(
            step_id="user",
            errors=errors,
            description_placeholders={
                "risks": risks_text.format(auth_url=auth_url) if auth_url else risks_text
            }
        )