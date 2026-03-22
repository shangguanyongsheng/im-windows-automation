# Windows-MCP 配置指南

## 什么是 Windows-MCP

Windows-MCP 是一个基于 Model Context Protocol (MCP) 的 Windows 系统控制服务器，允许外部程序通过标准协议控制 Windows 系统。

项目地址: [https://github.com/CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP)

## 安装步骤

### 1. 在 Windows 机器上安装 Windows-MCP

```powershell
# 克隆仓库
git clone https://github.com/CursorTouch/Windows-MCP.git
cd Windows-MCP

# 安装依赖（需要 PowerShell 7+）
Install-Module -Name Microsoft.PowerShell.SecretManagement
Install-Module -Name Microsoft.PowerShell.SecretStore
```

### 2. 配置 Windows-MCP

编辑 `config.json` 文件：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "auth_token": "your_secure_token_here"
  },
  "permissions": {
    "allow_file_operations": true,
    "allow_system_commands": true,
    "allow_window_operations": true,
    "restricted_paths": ["C:\\Windows\\System32"]
  }
}
```

**重要**: 
- 将 `auth_token` 替换为强随机令牌
- 根据安全需求调整权限设置
- 限制敏感路径访问

### 3. 启动 Windows-MCP 服务器

```powershell
# 在 Windows-MCP 目录下
.\start-server.ps1
```

服务器将在指定端口监听 MCP 请求。

## 网络配置

确保 Windows 机器的防火墙允许入站连接到 MCP 服务器端口。

如果 IM 自动化服务运行在不同机器上，需要确保网络可达性。

## 安全建议

1. **使用强认证令牌**: 不要使用默认或弱令牌
2. **限制权限**: 只开启必要的操作权限
3. **网络隔离**: 考虑在专用网络或 VPN 中运行
4. **定期更新**: 保持 Windows-MCP 为最新版本
5. **日志监控**: 启用详细日志记录可疑活动

## 故障排除

- **连接被拒绝**: 检查防火墙设置和服务器是否运行
- **认证失败**: 确认 auth_token 配置正确
- **权限不足**: 检查 permissions 配置
- **命令执行失败**: 查看 Windows-MCP 日志获取详细错误