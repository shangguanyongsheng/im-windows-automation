# 飞书集成指南

## 准备工作

1. **创建飞书企业自建应用**
   - 登录 [飞书开放平台](https://open.feishu.cn/)
   - 进入「开发者后台」→「企业自建应用」
   - 点击「创建企业自建应用」

2. **配置应用基本信息**
   - 应用名称: `Windows 自动化助手`
   - 应用头像: 选择合适的图标
   - 应用描述: `通过自然语言控制 Windows 系统`

3. **配置权限范围**
   - 添加以下权限:
     - `im:message` (读取和发送消息)
     - `contact:user.email:readonly` (获取用户信息)

4. **配置事件订阅**
   - 开启「事件订阅」
   - 设置接收事件的服务器地址 (Webhook URL)
   - 设置验证令牌 (Verification Token)
   - 设置加密密钥 (Encrypt Key)

## 配置环境变量

在项目根目录创建 `.env` 文件:

```env
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_VERIFICATION_TOKEN=your_verification_token
FEISHU_ENCRYPT_KEY=your_encrypt_key
```

## 部署 Webhook 服务

确保您的服务器可以被飞书访问，并正确处理以下事件:

- `message.receive`: 接收用户消息
- `url_verification`: 验证 Webhook URL

## 安全注意事项

- 不要在代码中硬编码敏感信息
- 使用环境变量或安全的密钥管理服务
- 限制应用可见范围，仅对必要人员开放
- 定期轮换密钥

## 测试

1. 在飞书工作区安装应用
2. 向应用发送测试消息
3. 检查日志确认消息接收和处理正常

## 故障排除

- **无法接收消息**: 检查 Webhook URL 是否可访问，验证令牌是否正确
- **认证失败**: 检查 App ID 和 App Secret
- **权限不足**: 确认已申请并获得所需权限
- **消息格式错误**: 参考飞书官方文档检查消息格式