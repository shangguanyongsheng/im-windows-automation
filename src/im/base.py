"""
IM 基类

定义统一的 IM 接口，所有具体的 IM 适配器都应该继承此类。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from src.agent.command_agent import Command


class BaseIM(ABC):
    """
    IM 基类
    
    定义了所有 IM 适配器必须实现的接口。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 IM 适配器
        
        Args:
            config: 配置字典，包含必要的认证信息和设置
        """
        self.config = config
        self.message_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None
    
    @abstractmethod
    def start(self) -> None:
        """
        启动 IM 服务
        
        根据不同的 IM 平台，可能需要启动 Webhook 服务器、
        连接 WebSocket 或其他初始化操作。
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        停止 IM 服务
        """
        pass
    
    @abstractmethod
    def send_message(self, recipient: str, message: str, 
                    context: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送消息
        
        Args:
            recipient: 接收者标识 (用户ID、群ID等)
            message: 要发送的消息内容
            context: 上下文信息 (可选)
            
        Returns:
            bool: 是否成功发送
        """
        pass
    
    def set_message_handler(self, handler: Callable[[str, Dict[str, Any]], Any]) -> None:
        """
        设置消息处理器
        
        Args:
            handler: 处理函数，接收 (message, context) 参数
        """
        self.message_handler = handler
    
    def _handle_incoming_message(self, message: str, context: Dict[str, Any]) -> None:
        """
        处理接收到的消息
        
        这是一个内部方法，由具体的 IM 适配器在接收到消息时调用。
        它会调用已设置的消息处理器。
        
        Args:
            message: 接收到的消息内容
            context: 消息上下文 (包含发送者ID、会话ID等信息)
        """
        if self.message_handler:
            try:
                self.message_handler(message, context)
            except Exception as e:
                # 记录错误但不中断消息接收
                self._log_error(f"消息处理失败: {e}")
                # 可以选择发送错误消息给用户
                self.send_message(
                    context.get('sender_id', ''),
                    f"处理您的请求时发生错误: {str(e)}",
                    context
                )
    
    def _log_error(self, error: str) -> None:
        """
        记录错误信息
        
        子类可以重写此方法以使用特定的日志系统。
        
        Args:
            error: 错误信息
        """
        print(f"ERROR: {error}")
    
    def _log_info(self, info: str) -> None:
        """
        记录信息
        
        子类可以重写此方法以使用特定的日志系统。
        
        Args:
            info: 信息内容
        """
        print(f"INFO: {info}")
    
    @classmethod
    @abstractmethod
    def from_env(cls) -> 'BaseIM':
        """
        从环境变量创建 IM 适配器实例
        
        Returns:
            BaseIM: IM 适配器实例
        """
        pass


# 使用示例
if __name__ == "__main__":
    # 这只是一个抽象基类，不能直接实例化
    # 具体的实现应该在子类中
    pass