# 微信集成指南（支持个人微信）

## 集成选项对比

| 方案 | 类型 | 星数 | 难度 | 稳定性 | 推荐度 |
|------|:----:|:----:|:----:|:------:|:------:|
| **企业微信** | 官方 API | - | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **wechaty** | 个人微信 SDK | 22.6k | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **wechatbot-webhook** | HTTP 接口 | 2.1k | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **ntchat** | PC 微信 Hook | 219 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 1. 企业微信（推荐）

适用于企业场景，官方支持，最稳定。

### 配置

```env
WECHAT_CORP_ID=your_corp_id
WECHAT_CORP_SECRET=your_corp_secret
WECHAT_AGENT_ID=your_agent_id
```

---

## 2. 个人微信 - wechatbot-webhook（推荐）

**GitHub**: https://github.com/danni-cool/wechatbot-webhook (2.1k ⭐)

### 特点
- ✅ HTTP API 接口，易于集成
- ✅ 支持 Docker 部署
- ✅ 不需要 Python 环境
- ⚠️ 需要扫码登录

### 安装

```bash
# Docker 方式
docker pull dannicool/wechatbot-webhook
docker run -d -p 3000:3000 dannicool/wechatbot-webhook
```

### HTTP API

```bash
# 发送消息
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"to": "好友昵称", "content": "你好"}'
```

---

## 3. 个人微信 - wechaty

**GitHub**: https://github.com/wechaty/wechaty (22.6k ⭐)

### 特点
- ✅ 跨平台
- ⚠️ 需要付费 token

### 安装

```bash
pip install wechaty
```

---

## 4. 个人微信 - ntchat

**GitHub**: https://github.com/billyplus/ntchat (219 ⭐)

### 特点
- ✅ 免费
- ✅ 基于 PC 微信 Hook
- ⚠️ 需要安装 PC 微信客户端

### 安装

```bash
pip install ntchat
```

---

## 推荐方案

| 场景 | 推荐 |
|------|------|
| **企业内部使用** | 企业微信 |
| **个人开发测试** | wechatbot-webhook |
| **需要稳定服务** | wechaty（付费） |
| **免费方案** | ntchat |

---

## ⚠️ 个人微信风险

- **封号风险** - 微信对自动化检测严格
- 建议使用小号测试
- 不要频繁发送消息