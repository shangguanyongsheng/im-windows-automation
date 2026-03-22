"""
飞书适配器

实现飞书 IM 平台的集成。
"""

import os
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, Callable
from urllib.parse import urlencode
import requests
from flask import Flask, request, jsonify

from src.im.base import BaseIM


class FeishuIM(BaseIM):
    """
    飞书 IM 适配器
    
    实现飞书企业自建应用的集成，支持接收和发送消息。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化飞书适配器
        
        Args:
            config: 配置字典，必须包含以下键:
                - app_id: 飞书应用 ID
                - app_secret: 飞书应用密钥
                - verification_token: 事件订阅验证令牌
                - encrypt_key: 加密密钥 (可选)
        """
        super().__init__(config)
        self.app_id = config['app_id']
        self.app_secret = config['app_secret']
        self.verification_token = config['verification_token']
        self.encrypt_key = config.get('encrypt_key')
        
        # 获取 tenant_access_token
        self.tenant_access_token = self._get_tenant_access_token()
        
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
    
    def _get_tenant_access_token(self) -> str:
        """
        获取 tenant_access_token
        
        Returns:
            str: tenant_access_token
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data['code'] != 0:
            raise Exception(f"获取 tenant_access_token 失败: {data['msg']}")
        
        return data['tenant_access_token']
    
    def _verify_signature(self, timestamp: str, nonce: str, body: str, signature: str) -> bool:
        """
        验证飞书请求签名
        
        Args:
            timestamp: 时间戳
            nonce: 随机字符串
            body: 请求体
            signature: 签名
            
        Returns:
            bool: 签名是否有效
        """
        if not self.encrypt_key:
            return True  # 如果没有设置加密密钥，则跳过签名验证
            
        string_to_sign = f"{timestamp}\n{nonce}\n{body}"
        hmac_code = hmac.new(
            self.encrypt_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac_code == signature
    
    def _handle_webhook(self) -> jsonify:
        """
        处理飞书 Webhook 请求
        """
        # 验证请求
        timestamp = request.headers.get('X-Lark-Timestamp')
        nonce = request.headers.get('X-Lark-Nonce')
        signature = request.headers.get('X-Lark-Signature')
        
        if not self._verify_signature(timestamp, nonce, request.get_data(as_text=True), signature):
            return jsonify({'challenge': ''}), 401
        
        data = request.json
        
        # 处理 URL 验证
        if 'type' in data and data['type'] == 'url_verification':
            return jsonify({'challenge': data['challenge']})
        
        # 处理消息事件
        if 'header' in data and data['header']['event_type'] == 'im.message.receive_v1':
            event = data['event']
            message = event['message']
            
            # 提取消息内容
            if message['message_type'] == 'text':
                content = json.loads(message['content'])['text']
            else:
                content = f"[{message['message_type']} 消息]"
            
            # 构建上下文
            context = {
                'sender_id': event['sender']['sender_id']['open_id'],
                'chat_id': event['message']['chat_id'],
                'message_id': event['message']['message_id'],
                'timestamp': event['message']['create_time']
            }
            
            # 处理消息
            self._handle_incoming_message(content, context)
            
            return jsonify({'status': 'ok'})
        
        return jsonify({'status': 'ignored'})
    
    def start(self) -> None:
        """
        启动飞书 Webhook 服务
        """
        host = self.config.get('host', '0.0.0.0')
        port = self.config.get('port', 8080)
        
        self._log_info(f"启动飞书 Webhook 服务，监听 {host}:{port}")
        self.flask_app.run(host=host, port=port, debug=False)
    
    def stop(self) -> None:
        """
        停止飞书 Webhook 服务
        
        注意: Flask 的 run() 方法是阻塞的，所以这个方法可能不会被调用。
        在实际部署中，可能需要使用其他方式来停止服务。
        """
        self._log_info("停止飞书 Webhook 服务")
        # Flask 没有直接的停止方法，通常通过进程管理来停止
    
    def send_message(self, recipient: str, message: str, 
                    context: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送消息到飞书
        
        Args:
            recipient: 接收者 chat_id
            message: 要发送的消息内容
            context: 上下文信息 (可选)
            
        Returns:
            bool: 是否成功发送
        """
        try:
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            
            params = {
                "receive_id_type": "chat_id"
            }
            
            payload = {
                "receive_id": recipient,
                "msg_type": "text",
                "content": json.dumps({"text": message})
            }
            
            headers = {
                "Authorization": f"Bearer {self.tenant_access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = requests.post(
                url + "?" + urlencode(params),
                json=payload,
                headers=headers
            )
            
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
    def from_env(cls) -> 'FeishuIM':
        """
        从环境变量创建飞书适配器实例
        
        需要以下环境变量:
        - FEISHU_APP_ID
        - FEISHU_APP_SECRET
        - FEISHU_VERIFICATION_TOKEN
        - FEISHU_ENCRYPT_KEY (可选)
        - FEISHU_HOST (可选，默认 0.0.0.0)
        - FEISHU_PORT (可选，默认 8080)
        
        Returns:
            FeishuIM: 飞书适配器实例
        """
        config = {
            'app_id': os.environ['FEISHU_APP_ID'],
            'app_secret': os.environ['FEISHU_APP_SECRET'],
            'verification_token': os.environ['FEISHU_VERIFICATION_TOKEN'],
            'encrypt_key': os.environ.get('FEISHU_ENCRYPT_KEY'),
            'host': os.environ.get('FEISHU_HOST', '0.0.0.0'),
            'port': int(os.environ.get('FEISHU_PORT', 8080))
        }
        
        return cls(config)


# 使用示例
if __name__ == "__main__":
    # 从环境变量创建实例并启动
    feishu_im = FeishuIM.from_env()
    feishu_im.start()