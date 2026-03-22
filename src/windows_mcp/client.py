"""
Windows-MCP 客户端

与 Windows-MCP 服务器通信，执行 Windows 系统操作。
"""

import json
import requests
from typing import Dict, Any, Optional
from src.agent.command_agent import Command


class WindowsMCPClient:
    """
    Windows-MCP 客户端
    
    封装与 Windows-MCP 服务器的通信，提供简单易用的接口。
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080, auth_token: str = ""):
        """
        初始化 Windows-MCP 客户端
        
        Args:
            host: Windows-MCP 服务器主机地址
            port: Windows-MCP 服务器端口
            auth_token: 认证令牌
        """
        self.base_url = f"http://{host}:{port}"
        self.auth_token = auth_token
        self.session = requests.Session()
        
        # 设置默认请求头
        if self.auth_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
    
    def execute_command(self, command: Command) -> Dict[str, Any]:
        """
        执行命令
        
        Args:
            command: 要执行的命令对象
            
        Returns:
            Dict[str, Any]: 执行结果
            
        Raises:
            Exception: 如果执行失败
        """
        try:
            # 构建 MCP 请求
            mcp_request = {
                "action": command.action,
                "parameters": command.parameters
            }
            
            # 发送请求到 Windows-MCP 服务器
            response = self.session.post(
                f"{self.base_url}/execute",
                json=mcp_request,
                timeout=30  # 30秒超时
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            if result.get("success", False):
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "message": result.get("message", "Success")
                }
            else:
                error_message = result.get("error", "Unknown error")
                return {
                    "success": False,
                    "error": error_message,
                    "message": f"Execution failed: {error_message}"
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        获取 Windows-MCP 服务器支持的功能
        
        Returns:
            Dict[str, Any]: 功能列表
        """
        try:
            response = self.session.get(f"{self.base_url}/capabilities")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务器是否健康
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False


# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = WindowsMCPClient(
        host="192.168.1.100",
        port=8080,
        auth_token="your_secure_token"
    )
    
    # 检查服务器健康状态
    if client.health_check():
        print("Windows-MCP 服务器正常运行")
    else:
        print("Windows-MCP 服务器不可用")
        exit(1)
    
    # 获取功能列表
    capabilities = client.get_capabilities()
    print(f"支持的功能: {capabilities}")
    
    # 执行命令示例
    from src.agent.command_agent import Command
    command = Command(
        action="file_read",
        parameters={"file_path": "C:\\test.txt"},
        context={}
    )
    
    result = client.execute_command(command)
    print(f"执行结果: {result}")