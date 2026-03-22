# QQ 集成指南

## 集成选项

QQ 集成主要有以下几种方式:

### 1. QQ 机器人 (推荐)

使用官方或第三方 QQ 机器人框架。

**推荐框架:**
- **NoneBot2**: Python 异步机器人框架
- **koishi**: 跨平台机器人框架
- **oicq**: Node.js QQ 协议库

### 2. 企业 QQ

适用于企业场景，有官方 API 支持。

### 3. Webhook 方式

通过 QQ 群机器人 Webhook 接收消息（功能有限）。

## 使用 NoneBot2 集成 (推荐方案)

### 安装依赖

```bash
pip install nonebot2[all]
```

### 创建机器人应用

1. **获取 QQ 机器人凭证**
   - 在 [QQ 开放平台](https://q.qq.com/) 创建机器人应用
   - 获取 AppID 和 Token

2. **配置环境变量**

```env
QQ_APP_ID=your_app_id
QQ_TOKEN=your_token
```

3. **实现消息处理**

在 NoneBot2 中创建插件处理用户消息，并与本项目的 CommandAgent 集成。

### 示例代码结构

```python
# src/im/qq.py 中会调用 NoneBot2 的适配器
from nonebot import on_message
from nonebot.adapters.qq import MessageEvent

# 消息处理器
matcher = on_message()

@matcher.handle()
async def handle_message(event: MessageEvent):
    # 调用 CommandAgent 处理消息
    result = command_agent.process(event.get_message())
    # 发送结果
    await matcher.send(result)
```

## 安全注意事项

- 不要使用个人 QQ 号进行自动化（违反用户协议）
- 使用官方机器人账号
- 限制机器人的群聊范围
- 监控机器人行为防止滥用
- 不要在代码中硬编码敏感信息

## 测试

1. 将机器人添加到测试群聊
2. 向机器人发送测试消息
3. 检查日志确认消息接收和处理正常

## 故障排除

- **无法连接**: 检查网络和凭证
- **消息不响应**: 确认机器人有发言权限
- **认证失败**: 检查 AppID 和 Token
- **功能受限**: QQ 机器人有频率限制，注意不要触发风控

## 注意事项

- QQ 机器人有严格的消息频率限制
- 某些敏感操作可能被系统拦截
- 建议在私人群聊中使用，避免公开群聊的复杂性