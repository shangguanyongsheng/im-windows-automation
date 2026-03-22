# IM + Windows 自动化项目

通过 IM（飞书/钉钉/微信/QQ）发送消息，AI 解析指令并调用 Windows-MCP 执行 Windows 操作。

## 功能特点

- ✅ **个人微信支持** - 支持 wechaty/ntchat/wechatbot-webhook
- ✅ **无需 Python 环境** - 提供 EXE 打包方案
- ✅ **多 IM 平台** - 飞书、钉钉、微信、QQ
- ✅ **Windows 自动化** - 文件操作、应用控制、键盘鼠标模拟

## 技术栈

| 组件 | 说明 |
|------|------|
| **Windows-MCP** | Windows 系统控制 (4.8k ⭐) |
| **wechaty** | 个人微信 SDK (22.6k ⭐) |
| **wechatbot-webhook** | HTTP 接口微信机器人 (2.1k ⭐) |

## 快速开始

### 方式一：直接使用（需要 Python）

```bash
git clone https://github.com/shangguanyongsheng/im-windows-automation.git
cd im-windows-automation
pip install -r requirements.txt
python src/main.py
```

### 方式二：EXE 运行（无需 Python）

1. 下载 `IM-Windows-Automation.exe`
2. 配置 `config/.env` 填入 API Key
3. 双击运行

### 打包成 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --name "IM-Windows-Automation" src/main.py
```

详见：[EXE 打包指南](docs/packaging.md)

## 支持的 IM 平台

| 平台 | 方案 | 难度 | 说明 |
|------|------|:----:|------|
| **个人微信** | wechatbot-webhook | ⭐ | HTTP API，推荐 |
| **个人微信** | wechaty | ⭐⭐ | 付费 token |
| **个人微信** | ntchat | ⭐⭐ | 免费，需 PC 微信 |
| **企业微信** | 官方 API | ⭐ | 最稳定 |
| **飞书** | 开放平台 API | ⭐ | 官方支持 |
| **钉钉** | 开放平台 API | ⭐ | 官方支持 |
| **QQ** | go-cqhttp | ⭐⭐ | 第三方方案 |

## 配置文档

- [Windows-MCP 配置](docs/windows-mcp-setup.md)
- [个人微信集成](docs/im-integration/wechat.md)
- [飞书集成](docs/im-integration/feishu.md)
- [钉钉集成](docs/im-integration/dingtalk.md)
- [EXE 打包](docs/packaging.md)

## 使用示例

在微信/飞书/钉钉发消息：

```
打开记事本
截图
列出桌面文件
搜索文件 report.docx
```

AI 会自动解析并执行对应的 Windows 操作。

## 安全注意事项

- ⚠️ 个人微信有封号风险，建议用小号测试
- 不要频繁发送消息
- 不要在代码中硬编码 API Key
- 建议限制可执行的操作范围

## 许可证

MIT License