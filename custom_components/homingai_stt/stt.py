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
        self._access_token = entry.data.get('access_token', '')
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
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "audio/wav",
                },
                data=wav_data,
            ) as response:
                if response.status != 200:
                    return stt.SpeechResult("服务器开小差了~", SpeechResultState.ERROR)

                result = await response.json()
                if result.get("code") != 200:
                    return stt.SpeechResult("识别失败", SpeechResultState.ERROR)

                text = result.get("msg")
                if not text:
                    return stt.SpeechResult("你好像没有说话哦~", SpeechResultState.ERROR)

                return stt.SpeechResult(text, SpeechResultState.SUCCESS)

        except Exception as err:
            _LOGGER.error("STT 处理失败: %s", err)
            return stt.SpeechResult("STT 处理失败~", SpeechResultState.ERROR)



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
