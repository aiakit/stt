"""HomingAI STT 平台实现。"""
import logging
from homeassistant.components import stt
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    SUPPORTED_LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)

class SpeechToTextEntity(stt.SpeechToTextEntity):
    """HomingAI STT entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        super().__init__()
        
        self.hass = hass
        self._attr_unique_id = f"{entry.entry_id}_stt"
        self._attr_name = "HomingAI STT"
        self._entry = entry
        self._client_id = entry.data[CONF_CLIENT_ID]
        self._client_secret = entry.data[CONF_CLIENT_SECRET]
        self._session = async_get_clientsession(hass)

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        """Return a list of supported formats."""
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[str]:
        """Return a list of supported codecs."""
        return ["pcm"]

    @property
    def supported_bit_rates(self) -> list[int]:
        """Return a list of supported bit rates."""
        return [16000]

    @property
    def supported_sample_rates(self) -> list[int]:
        """Return a list of supported sample rates."""
        return [16000]

    @property
    def supported_channels(self) -> list[int]:
        """Return a list of supported channels."""
        return [1]

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stream):
        """Process audio stream to text."""
        try:
            audio_data = await stream.read()

            async with self._session.post(
                "https://api.homingai.com/ha/home/stt",
                headers={
                    "Authorization": f"Bearer {self._client_id}:{self._client_secret}",
                    "Content-Type": "audio/wav",
                },
                data=audio_data,
            ) as response:
                if response.status != 200:
                    _LOGGER.error("API 调用失败: %s", await response.text())
                    raise stt.SpeechToTextError(f"API 调用失败，状态码: {response.status}")

                result = await response.json()
                if result.get("code") != 200:
                    raise stt.SpeechToTextError(f"API 返回错误: {result.get('msg', '未知错误')}")

                return stt.SpeechResult(result["data"]["text"])

        except Exception as err:
            _LOGGER.error("STT 处理失败: %s", err)
            raise stt.SpeechToTextError(f"STT 处理失败: {err}")

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> bool:
    """Set up HomingAI STT platform."""
    async_add_entities([SpeechToTextEntity(hass, config_entry)])
    return True