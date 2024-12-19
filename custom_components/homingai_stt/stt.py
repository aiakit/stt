"""Support for HomingAI STT speech to text."""
from homeassistant.components import stt
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    SUPPORTED_LANGUAGES,
    SUPPORTED_FORMATS,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DEFAULT_URL,
)

async def async_get_engine(hass: HomeAssistant, config, language: str) -> "HomingAISTTProvider":
    """Set up HomingAI STT speech component."""
    return HomingAISTTProvider(
        hass,
        config.data[CONF_CLIENT_ID],
        config.data[CONF_CLIENT_SECRET],
        config.data.get(CONF_URL, DEFAULT_URL),
    )

class HomingAISTTProvider(stt.Provider):
    """The HomingAI STT provider."""

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[str]:
        """Return a list of supported formats."""
        return SUPPORTED_FORMATS

    def __init__(
        self,
        hass: HomeAssistant,
        client_id: str,
        client_secret: str,
        url: str,
    ) -> None:
        """Initialize the provider."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = url + "/ha/home/stt"
        self._session = async_get_clientsession(hass)

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stream):
        """Process an audio stream to text."""
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
                    raise stt.SpeechToTextError(f"API call failed with status: {response.status}")

                result = await response.json()
                if result.get("code") != 200:
                    raise stt.SpeechToTextError(f"API returned error: {result.get('msg', 'Unknown error')}")

                return stt.SpeechResult(result["msg"])

        except Exception as err:
            raise stt.SpeechToTextError(f"STT processing failed: {err}") 