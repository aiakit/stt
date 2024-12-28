# HomingAI STT for Home Assistant

HomingAI STT 是一个 Home Assistant 自定义组件，提供高精度的语音识别服务，支持将语音转换为文字，让您的智能家居系统更好地理解语音指令。

## ✨ 功能特点

- 🎯 高精度识别：采用先进的语音识别技术，准确率高
- 🇨🇳 中文支持：完美支持中文语音识别
- 🎤 实时转换：快速的语音转文字处理
- 📱 多场景适配：支持各类智能家居语音交互场景
- 🔒 安全可靠：使用授权方式确保数据安全

## 📦 安装方法

### HACS 安装（推荐）

1. 确保已经安装了 [HACS](https://hacs.xyz/)
2. HACS > 集成 > 右上角菜单 > Custom repositories
3. 添加仓库：`https://github.com/aiakit/stt`
4. 类别选择：Integration
5. 在 HACS 集成页面搜索 "HomingAI STT"
6. 点击下载
7. 重启 Home Assistant

### 手动安装

1. 下载此仓库的最新版本
2. 将 `custom_components/homingai_stt` 文件夹复制到您的 `custom_components` 目录
3. 重启 Home Assistant

## ⚙️ 配置说明

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=homingai_stt)

1. 在 Home Assistant 的配置页面中添加集成
2. 搜索 "HomingAI STT"
3. 完成HomingAi的授权
4. 点击“提交”完成配置

> 提示：点击上方按钮可以快速跳转到配置页面

## 🎯 支持格式

- 音频格式：WAV
- 采样率：16kHz
- 声道：单声道
- 语言支持：中文 (zh-CN)等等

## ⚠️ 注意事项

- 确保音频文件格式符合要求
- 保持网络连接稳定
- 正确配置 Client ID 和 Secret

## 🔧 故障排除

如果遇到问题，请先检查：

1. 音频格式是否符合要求
2. 网络连接是否正常
3. 授权信息是否正确
4. 查看 Home Assistant 日志中是否有错误信息

## 📝 问题反馈

如果您遇到任何问题或有改进建议，欢迎通过以下方式反馈：

- [提交 Issue](https://github.com/your-username/homingai-stt/issues)
- [技术支持](https://homingai.com)

## 📄 许可证

本项目采用 Apache License 2.0 许可证，详见 [LICENSE](LICENSE) 文件。

## 🔄 更新日志

### v1.0.0 (2024-03-15)
- ✨ 初始版本发布
- 🎯 支持中文语音识别
- 🔧 优化识别准确率
- 📦 完善配置界面

## 🤝 贡献指南

欢迎提交 Pull Request 或者建立 Issue。

---

Made with ❤️ by HomingAI Team