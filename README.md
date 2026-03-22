# IM + Windows 自动化项目

这个项目允许用户通过即时通讯工具（飞书、钉钉、微信、QQ）向 AI 发送指令，AI 将解析这些指令并调用 Windows-MCP 执行相应的 Windows 系统操作，然后将执行结果返回给用户。

## 技术栈

- **Windows-MCP**: 用于控制 Windows 系统的 MCP (Model Context Protocol) 服务器
- **IM 集成**: 支持飞书、钉钉、微信、QQ 作为交互入口

## 项目架构

本项目采用模块化设计，主要包含以下组件：

1. **指令解析 Agent**: 负责理解用户在 IM 中发送的自然语言指令
2. **IM 适配器**: 为不同 IM 平台提供统一的接口
3. **Windows-MCP 客户端**: 与 Windows-MCP 服务器通信，执行系统操作

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/shangguanyongsheng/im-windows-automation.git
cd im-windows-automation
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 Windows-MCP

请参考 [Windows-MCP 配置指南](docs/windows-mcp-setup.md) 设置 Windows-MCP 服务器。

### 4. 配置 IM 集成

根据您要使用的 IM 平台，参考对应的集成文档：
- [飞书集成](docs/im-integration/feishu.md)
- [钉钉集成](docs/im-integration/dingtalk.md)
- [微信集成](docs/im-integration/wechat.md)
- [QQ 集成](docs/im-integration/qq.md)

### 5. 启动服务

```bash
python src/main.py
```

## 安全注意事项

- 本项目不存储任何敏感信息（如 API Key）
- 请确保在安全的网络环境中运行
- 建议限制可执行的 Windows 操作范围，避免安全风险

## 许可证

MIT License