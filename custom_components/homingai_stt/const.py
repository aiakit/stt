"""Constants for HomingAI STT integration."""

DOMAIN = "homingai_stt"
DEFAULT_NAME = "HomingAI STT"

# Configuration
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

# API Endpoints
DEFAULT_URL = "https://api.homingai.com"  # 替换为您的实际API端点

# Supported audio formats and languages
SUPPORTED_FORMATS = ["wav", "mp3"]  # 添加您支持的格式
SUPPORTED_LANGUAGES = ["zh-CN", "en-US"]  # 添加您支持的语言
