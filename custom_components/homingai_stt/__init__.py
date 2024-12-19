"""The HomingAI STT integration."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .stt import async_get_engine

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HomingAI STT component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HomingAI STT from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # 注册 STT 引擎
    engine = await async_get_engine(hass, entry, "zh-CN")
    if engine:
        hass.data[DOMAIN]["engine"] = engine

    await hass.config_entries.async_forward_entry_setups(entry, ["stt"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["stt"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok