"""
指令解析 Agent

负责解析用户在 IM 中发送的自然语言指令，将其转换为结构化的命令对象，
以便 Windows-MCP 客户端执行。
"""

import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Command:
    """结构化命令对象"""
    action: str  # 操作类型 (e.g., 'file_read', 'system_execute', 'window_focus')
    parameters: Dict[str, Any]  # 操作参数
    context: Dict[str, Any]  # 上下文信息 (e.g., user_id, conversation_id)


class CommandAgent:
    """
    指令解析 Agent
    
    负责将自然语言指令解析为结构化的 Command 对象。
    支持多种操作类型和参数提取。
    """
    
    def __init__(self):
        # 定义支持的操作类型和对应的解析规则
        self.supported_actions = {
            'file_read': {
                'patterns': [
                    r'(读取|查看|打开)文件\s+(.+)',
                    r'显示文件内容\s+(.+)',
                    r'cat\s+(.+)'
                ],
                'parameters': ['file_path']
            },
            'file_write': {
                'patterns': [
                    r'(写入|创建|保存)文件\s+(.+)\s+内容\s+(.+)',
                    r'echo\s+(.+)\s+>\s+(.+)'
                ],
                'parameters': ['file_path', 'content']
            },
            'system_execute': {
                'patterns': [
                    r'(执行|运行)命令\s+(.+)',
                    r'cmd:\s+(.+)',
                    r'\$(.+)'
                ],
                'parameters': ['command']
            },
            'window_focus': {
                'patterns': [
                    r'(聚焦|切换到|激活)窗口\s+(.+)',
                    r'focus\s+(.+)'
                ],
                'parameters': ['window_title']
            },
            'window_close': {
                'patterns': [
                    r'(关闭|退出)窗口\s+(.+)',
                    r'close\s+(.+)'
                ],
                'parameters': ['window_title']
            },
            'screenshot': {
                'patterns': [
                    r'(截图|截屏|屏幕截图)',
                    r'screenshot'
                ],
                'parameters': []
            },
            'clipboard_read': {
                'patterns': [
                    r'(读取|获取)剪贴板',
                    r'clipboard'
                ],
                'parameters': []
            },
            'clipboard_write': {
                'patterns': [
                    r'(写入|设置)剪贴板\s+(.+)',
                    r'clipboard=\s+(.+)'
                ],
                'parameters': ['content']
            }
        }
        
        # 预编译正则表达式以提高性能
        self.compiled_patterns = {}
        for action, config in self.supported_actions.items():
            self.compiled_patterns[action] = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in config['patterns']
            ]
    
    def parse(self, message: str, context: Optional[Dict[str, Any]] = None) -> Command:
        """
        解析自然语言指令
        
        Args:
            message: 用户发送的消息
            context: 上下文信息 (可选)
            
        Returns:
            Command: 结构化命令对象
            
        Raises:
            ValueError: 如果无法解析指令
        """
        if context is None:
            context = {}
            
        # 首先尝试匹配已知的操作模式
        for action, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(message)
                if match:
                    # 提取参数
                    parameters = {}
                    param_names = self.supported_actions[action]['parameters']
                    groups = match.groups()
                    
                    if len(param_names) == len(groups):
                        for i, param_name in enumerate(param_names):
                            parameters[param_name] = groups[i].strip()
                    elif len(groups) == 1 and len(param_names) > 0:
                        # 特殊处理：单个捕获组对应多个参数的情况
                        # 这里简单地将第一个参数设为捕获组内容
                        parameters[param_names[0]] = groups[0].strip()
                    
                    return Command(
                        action=action,
                        parameters=parameters,
                        context=context
                    )
        
        # 如果没有匹配到已知模式，尝试通用命令解析
        generic_command = self._parse_generic_command(message)
        if generic_command:
            return Command(
                action='system_execute',
                parameters={'command': generic_command},
                context=context
            )
        
        # 如果仍然无法解析，抛出异常
        raise ValueError(f"无法解析指令: {message}")
    
    def _parse_generic_command(self, message: str) -> Optional[str]:
        """
        尝试解析通用系统命令
        
        Args:
            message: 用户消息
            
        Returns:
            str: 命令字符串，如果无法解析则返回 None
        """
        # 移除常见的前缀
        prefixes = ['请', '帮我', '能否', '可以', '执行一下', '运行一下']
        cleaned_message = message.strip()
        
        for prefix in prefixes:
            if cleaned_message.startswith(prefix):
                cleaned_message = cleaned_message[len(prefix):].strip()
                break
        
        # 如果消息看起来像命令（包含空格且不是问句）
        if ' ' in cleaned_message and not cleaned_message.endswith('?'):
            # 简单启发式：如果包含常见命令关键字
            command_keywords = ['dir', 'ls', 'cd', 'mkdir', 'del', 'copy', 'move', 'ping', 'ipconfig']
            if any(keyword in cleaned_message.lower() for keyword in command_keywords):
                return cleaned_message
        
        return None
    
    def get_supported_actions(self) -> List[str]:
        """
        获取支持的操作列表
        
        Returns:
            List[str]: 支持的操作名称列表
        """
        return list(self.supported_actions.keys())
    
    def get_action_help(self, action: str) -> str:
        """
        获取特定操作的帮助信息
        
        Args:
            action: 操作名称
            
        Returns:
            str: 帮助信息
        """
        if action not in self.supported_actions:
            return f"未知操作: {action}"
        
        examples = []
        for pattern in self.supported_actions[action]['patterns']:
            # 将正则表达式转换为人类可读的示例
            example = pattern.pattern
            example = example.replace(r'\s+', ' ')
            example = example.replace(r'(.+)', '<参数>')
            examples.append(example)
        
        return f"操作: {action}\n示例: {'; '.join(examples)}"
    
    def get_all_help(self) -> str:
        """
        获取所有操作的帮助信息
        
        Returns:
            str: 所有操作的帮助信息
        """
        help_text = "支持的操作:\n\n"
        for action in self.supported_actions:
            help_text += self.get_action_help(action) + "\n\n"
        return help_text


# 使用示例
if __name__ == "__main__":
    agent = CommandAgent()
    
    # 测试用例
    test_messages = [
        "读取文件 C:\\test.txt",
        "执行命令 dir C:\\",
        "聚焦窗口 记事本",
        "截图",
        "请帮我查看 D:\\data.csv 文件"
    ]
    
    for message in test_messages:
        try:
            command = agent.parse(message, {'user_id': 'test_user'})
            print(f"消息: {message}")
            print(f"解析结果: {command}")
            print("-" * 40)
        except ValueError as e:
            print(f"消息: {message}")
            print(f"错误: {e}")
            print("-" * 40)