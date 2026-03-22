"""
钉钉适配器

实现钉钉 IM 平台的集成。
"""

import os
import json
import hmac
import hashlib
import base64
from typing import Dict, Any, Optional, Callable
from urllib.parse import quote_plus
import requests
from flask import Flask, request, jsonify

from src.im.base import BaseIM


class DingTalkIM(BaseIM):
    """
    钉钉 IM 适配器
    
    实现钉钉企业内部机器人或应用的集成，支持接收和发送消息。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化钉钉适配器
        
        Args:
            config: 配置字典，必须包含以下键:
                - app_key: 钉钉应用 Key
                - app_secret: 钉钉应用密钥
                - sign_secret: 签名密钥 (用于事件订阅)
        """
        super().__init__(config)
        self.app_key = config['app_key']
        self.app_secret = config['app_secret']
        self.sign_secret = config.get('sign_secret')
        
        # 获取 access_token
        self.access_token = self._get_access_token()
        
        # 创建 Flask 应用用于处理 Webhook
        self.flask_app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """设置 Flask 路由"""
        self.flask_app.add_url_rule(
            '/webhook', 
            'webhook', 
            self._handle_webhook, 
            methods=['POST']
        )
    
    def _get_access_token(self) -> str:
        """
        获取 access_token
        
        Returns:
            str: access_token
        """
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['errcode'] != 0:
            raise Exception(f"获取 access_token 失败: {data['errmsg']}")
        
        return data['access_token']
    
    def _verify_signature(self, timestamp: str, sign: str) -> bool:
        """
        验证钉钉请求签名
        
        Args:
            timestamp: 时间戳
            sign: 签名
            
        Returns:
            bool: 签名是否有效
        """
        if not self.sign_secret:
            return True  # 如果没有设置签名密钥，则跳过签名验证
            
        string_to_sign = f"{timestamp}\n{self.sign_secret}"
        hmac_code = hmac.new(
            self.sign_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        expected_sign = base64.b64encode(hmac_code).decode('utf-8')
        return expected_sign == sign
    
    def _handle_webhook(self) -> jsonify:
        """
        处理钉钉 Webhook 请求
        """
        # 验证请求
        timestamp = request.headers.get('Timestamp')
        sign = request.headers.get('Sign')
        
        if not self._verify_signature(timestamp, sign):
            return jsonify({'status': 'error', 'message': 'Invalid signature'}), 401
        
        data = request.json
        
        # 处理消息事件
        if 'conversationId' in data and 'text' in data:
            content = data['text']['content']
            
            # 构建上下文
            context = {
                'sender_id': data['senderId'],
                'chat_id': data['conversationId'],
                'message_id': data.get('msgId', ''),
                'timestamp': data.get('createAt', '')
            }
            
            # 处理消息
            self._handle_incoming_message(content, context)
            
            return jsonify({'status': 'ok'})
        
        return jsonify({'status': 'ignored'})
    
    def start(self) -> None:
        """
        启动钉钉 Webhook 服务
        """
        host = self.config.get('host', '0.0.0.0')
        port = self.config.get('port', 8080)
        
        self._log_info(f"启动钉钉 Webhook 服务，监听 {host}:{port}")
        self.flask_app.run(host=host, port=port, debug=False)
    
    def stop(self) -> None:
        """
        停止钉钉 Webhook 服务
        """
        self._log_info("停止钉钉 Webhook 服务")
        # Flask 没有直接的停止方法，通常通过进程管理来停止
    
    def send_message(self, recipient: str, message: str, 
                    context: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送消息到钉钉
        
        Args:
            recipient: 接收者 conversationId 或 webhook URL
            message: 要发送的消息内容
            context: 上下文信息 (可选)
            
        Returns:
            bool: 是否成功发送
        """
        try:
            # 如果 recipient 是 webhook URL，则直接使用
            if recipient.startswith('http'):
                webhook_url = recipient
            else:
                # 否则使用 conversationId 发送
                url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2"
                
                payload = {
                    "agent_id": self.config.get('agent_id', 0),
                    "userid_list": recipient,  # 这里假设 recipient 是用户 ID 列表
                    "msg": {
                        "msgtype": "text",
                        "text": {
                            "content": message
                        }
                    }
                }
                
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "x-acs-dingtalk-access-token": self.access_token
                }
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    self._log_info(f"成功发送消息到 {recipient}")
                    return True
                else:
                    self._log_error(f"发送消息失败: {response.text}")
                    return False
            
        except Exception as e:
            self._log_error(f"发送消息异常: {e}")
            return False
    
    @classmethod
    def from_env(cls) -> 'DingTalkIM':
        """
        从环境变量创建钉钉适配器实例
        
        需要以下环境变量:
        - DINGTALK_APP_KEY
        - DINGTALK_APP_SECRET
        - DINGTALK_SIGN_SECRET (可选)
        - DINGTALK_AGENT_ID (可选)
        - DINGTALK_HOST (可选，默认 0.0.0.0)
        - DINGTALK_PORT (可选，默认 8080)
        
        Returns:
            DingTalkIM: 钉钉适配器实例
        """
        config = {
            'app_key': os.environ['DINGTALK_APP_KEY'],
            'app_secret': os.environ['DINGTALK_APP_SECRET'],
            'sign_secret': os.environ.get('DINGTALK_SIGN_SECRET'),
            'agent_id': os.environ.get('DINGTALK_AGENT_ID', 0),
            'host': os.environ.get('DINGTALK_HOST', '0.0.0.0'),
            'port': int(os.environ.get('DINGTALK_PORT', 8080))
        }
        
        return cls(config)


# 使用示例
if __name__ == "__main__":
    # 从环境变量创建实例并启动
    dingtalk_im = DingTalkIM.from_env()
    dingtalk_im.start()