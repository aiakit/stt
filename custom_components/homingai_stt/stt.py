"""HomingAI STT 平台实现。"""
from homeassistant.components import stt
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    SUPPORTED_LANGUAGES,
    SUPPORTED_FORMATS,
)

class HomingAISTTProvider(stt.Provider):
    """HomingAI STT 提供者。"""

    @property
    def supported_languages(self) -> list[str]:
        """返回支持的语言列表。"""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[str]:
        """返回支持的格式列表。"""
        return SUPPORTED_FORMATS

    @property
    def supported_codecs(self) -> list[str]:
        """返回支持的编解码器列表。"""
        return ["pcm"]

    @property
    def supported_bit_rates(self) -> list[int]:
        """返回支持的比特率列表。"""
        return [16000]

    @property
    def supported_sample_rates(self) -> list[int]:
        """返回支持的采样率列表。"""
        return [16000]

    @property
    def supported_channels(self) -> list[int]:
        """返回支持的声道数列表。"""
        return [1]

    def __init__(
        self,
        hass: HomeAssistant,
        client_id: str,
        client_secret: str,
    ) -> None:
        """初始化提供者。"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = "https://api.homingai.com/ha/home/stt"
        self._session = async_get_clientsession(hass)

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stream):
        """处理音频流转文字。"""
        try:
            audio_data = await stream.read()

            async with self._session.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.client_id}:{self.client_secret}",
                    "Content-Type": "application/octet-stream",
                },
                data=audio_data,
            ) as response:
                if response.status != 200:
                    raise stt.SpeechToTextError(f"API 调用失败，状态码: {response.status}")

                result = await response.json()
                if result.get("code") != 200:
                    raise stt.SpeechToTextError(f"API 返回错误: {result.get('msg', '未知错误')}")

                return stt.SpeechResult(result["msg"])

        except Exception as err:
            raise stt.SpeechToTextError(f"STT 处理失败: {err}")

async def async_get_engine(hass: HomeAssistant, config: ConfigEntry, language: str):
    """设置 HomingAI STT 引擎。"""
    return HomingAISTTProvider(
        hass,
        config.data[CONF_CLIENT_ID],
        config.data[CONF_CLIENT_SECRET],
    )

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> bool:
    """设置 HomingAI STT 平台。"""
    return True