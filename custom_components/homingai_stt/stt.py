"""HomingAI STT 平台实现。"""
import logging

from homeassistant.components import stt
from homeassistant.components.stt import (
    SpeechResultState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    SUPPORTED_LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)


class SpeechToTextEntity(stt.SpeechToTextEntity):
    """HomingAI STT entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
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
        return [stt.AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[int]:
        """Return a list of supported bit rates."""
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[int]:
        """Return a list of supported sample rates."""
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[int]:
        """Return a list of supported channels."""
        return [stt.AudioChannels.CHANNEL_MONO]

    def _normalize_language(self, language: str) -> str:
        """标准化语言代码。"""
        # 处理通用中文到具体变体的映射
        if language == "zh":
            return "zh-CN"
        return language

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stream):
        """Process audio stream to text."""
        # 标准化语言代码
        normalized_language = self._normalize_language(metadata.language)
        if normalized_language not in self.supported_languages:
            raise stt.SpeechToTextError(
                f"Language '{metadata.language}' not supported"
            )

        if metadata.format not in self.supported_formats:
            raise stt.SpeechToTextError(
                f"Format '{metadata.format}' not supported"
            )

        if metadata.codec not in self.supported_codecs:
            raise stt.SpeechToTextError(
                f"Codec '{metadata.codec}' not supported"
            )

        if metadata.bit_rate not in self.supported_bit_rates:
            raise stt.SpeechToTextError(
                f"Bit rate '{metadata.bit_rate}' not supported"
            )

        if metadata.sample_rate not in self.supported_sample_rates:
            raise stt.SpeechToTextError(
                f"Sample rate '{metadata.sample_rate}' not supported"
            )

        if metadata.channel not in self.supported_channels:
            raise stt.SpeechToTextError(
                f"Channel '{metadata.channel}' not supported"
            )

        try:
            # 从异步生成器读取音频数据
            audio_chunks = []
            async for chunk in stream:
                audio_chunks.append(chunk)
            audio_data = b"".join(audio_chunks)

            # 添加 WAV 头
            wav_header = generate_wav_header(
                audio_size=len(audio_data),
                sample_rate=metadata.sample_rate,
                channels=metadata.channel,
                bits_per_sample=16
            )

            wav_data = wav_header + audio_data

            async with self._session.post(
                "https://api.homingai.com/ha/home/stt",
                headers={
                    "Authorization": f"Bearer {self._client_id}:{self._client_secret}",
                    "Content-Type": "audio/wav",
                },
                data=wav_data,
            ) as response:
                if response.status != 200:
                    _LOGGER.error("API 调用失败: %s", await response.text())
                    raise stt.SpeechToTextError(f"API 调用失败，状态码: {response.status}")

                result = await response.json()
                if result.get("code") != 200:
                    raise stt.SpeechToTextError(f"API 返回错误: {result.get('msg', '未知错误')}")

                text = result.get("msg")
                if not text:
                    raise stt.SpeechToTextError("API 返回的数据中没有识别结果")

                return stt.SpeechResult(text, SpeechResultState.SUCCESS)

        except Exception as err:
            _LOGGER.error("STT 处理失败: %s", err)
            raise stt.SpeechToTextError(f"STT 处理失败: {err}")


def generate_wav_header(audio_size: int, sample_rate: int, channels: int, bits_per_sample: int) -> bytes:
    """生成标准的 WAV 文件头."""
    # RIFF 块
    chunk_id = b'RIFF'
    chunk_size = audio_size + 36  # 文件总长度减去 8
    format_type = b'WAVE'

    # fmt 子块
    subchunk1_id = b'fmt '
    subchunk1_size = 16  # PCM 格式的大小为 16
    audio_format = 1  # PCM = 1
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8

    # data 子块
    subchunk2_id = b'data'
    subchunk2_size = audio_size

    # 按照 WAV 格式组装头部数据
    header = (
            chunk_id +
            chunk_size.to_bytes(4, 'little') +
            format_type +
            subchunk1_id +
            subchunk1_size.to_bytes(4, 'little') +
            audio_format.to_bytes(2, 'little') +
            channels.to_bytes(2, 'little') +
            sample_rate.to_bytes(4, 'little') +
            byte_rate.to_bytes(4, 'little') +
            block_align.to_bytes(2, 'little') +
            bits_per_sample.to_bytes(2, 'little') +
            subchunk2_id +
            subchunk2_size.to_bytes(4, 'little')
    )

    return header


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities,
) -> bool:
    """Set up HomingAI STT platform."""
    async_add_entities([SpeechToTextEntity(hass, config_entry)])
    return True
