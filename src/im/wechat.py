"""
微信适配器

实现微信 IM 平台的集成，主要支持企业微信。
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional, Callable
from urllib.parse import urlencode
import requests
from flask import Flask, request, jsonify

from src.im.base import BaseIM


class WeChatIM(BaseIM):
    """
    微信 IM 适配器
    
    实现企业微信应用的集成，支持接收和发送消息。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化微信适配器
        
        Args:
            config: 配置字典，必须包含以下键:
                - corp_id: 企业 ID
                - corp_secret: 应用密钥
                - agent_id: 应用 ID
                - token: 服务器配置 Token
                - encoding_aes_key: 消息加解密密钥 (可选)
        """
        super().__init__(config)
        self.corp_id = config['corp_id']
        self.corp_secret = config['corp_secret']
        self.agent_id = config['agent_id']
        self.token = config['token']
        self.encoding_aes_key = config.get('encoding_aes_key')
        
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
            methods=['GET', 'POST']
        )
    
    def _get_access_token(self) -> str:
        """
        获取 access_token
        
        Returns:
            str: access_token
        """
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.corp_secret
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['errcode'] != 0:
            raise Exception(f"获取 access_token 失败: {data['errmsg']}")
        
        return data['access_token']
    
    def _verify_signature(self, signature: str, timestamp: str, nonce: str, echostr: str = None) -> bool:
        """
        验证微信请求签名
        
        Args:
            signature: 签名
            timestamp: 时间戳
            nonce: 随机字符串
            echostr: 回显字符串 (用于 GET 请求验证)
            
        Returns:
            bool: 签名是否有效
        """
        tmp_list = [self.token, timestamp, nonce]
        if echostr:
            tmp_list.append(echostr)
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        sha1 = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        return sha1 == signature
    
    def _handle_webhook(self) -> jsonify:
        """
        处理微信 Webhook 请求
        """
        # 处理 GET 请求 (URL 验证)
        if request.method == 'GET':
            signature = request.args.get('msg_signature')
            timestamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echostr = request.args.get('echostr')
            
            if self._verify_signature(signature, timestamp, nonce, echostr):
                return echostr
            else:
                return 'Invalid signature', 401
        
        # 处理 POST 请求 (消息接收)
        signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        
        if not self._verify_signature(signature, timestamp, nonce):
            return 'Invalid signature', 401
        
        # 解析消息内容
        # 注意: 这里简化处理，实际需要解密消息内容
        data = request.json
        
        if 'MsgType' in data and data['MsgType'] == 'text':
            content = data['Content']
            
            # 构建上下文
            context = {
                'sender_id': data['FromUserName'],
                'chat_id': data['ToUserName'],
                'message_id': data.get('MsgId', ''),
                'timestamp': data.get('CreateTime', '')
            }
            
            # 处理消息
            self._handle_incoming_message(content, context)
            
            return 'success'
        
        return 'ignored'
    
    def start(self) -> None:
        """
        启动微信 Webhook 服务
        """
        host = self.config.get('host', '0.0.0.0')
        port = self.config.get('port', 8080)
        
        self._log_info(f"启动微信 Webhook 服务，监听 {host}:{port}")
        self.flask_app.run(host=host, port=port, debug=False)
    
    def stop(self) -> None:
        """
        停止微信 Webhook 服务
        """
        self._log_info("停止微信 Webhook 服务")
        # Flask 没有直接的停止方法，通常通过进程管理来停止
    
    def send_message(self, recipient: str, message: str, 
                    context: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送消息到企业微信
        
        Args:
            recipient: 接收者 UserID 或部门 ID
            message: 要发送的消息内容
            context: 上下文信息 (可选)
            
        Returns:
            bool: 是否成功发送
        """
        try:
            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
            params = {"access_token": self.access_token}
            
            payload = {
                "touser": recipient,
                "msgtype": "text",
                "agentid": self.agent_id,
                "text": {
                    "content": message
                },
                "safe": 0
            }
            
            response = requests.post(url, params=params, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['errcode'] == 0:
                    self._log_info(f"成功发送消息到 {recipient}")
                    return True
                else:
                    self._log_error(f"发送消息失败: {data['errmsg']}")
                    return False
            else:
                self._log_error(f"发送消息失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self._log_error(f"发送消息异常: {e}")
            return False
    
    @classmethod
    def from_env(cls) -> 'WeChatIM':
        """
        从环境变量创建微信适配器实例
        
        需要以下环境变量:
        - WECHAT_CORP_ID
        - WECHAT_CORP_SECRET
        - WECHAT_AGENT_ID
        - WECHAT_TOKEN
        - WECHAT_ENCODING_AES_KEY (可选)
        - WECHAT_HOST (可选，默认 0.0.0.0)
        - WECHAT_PORT (可选，默认 8080)
        
        Returns:
            WeChatIM: 微信适配器实例
        """
        config = {
            'corp_id': os.environ['WECHAT_CORP_ID'],
            'corp_secret': os.environ['WECHAT_CORP_SECRET'],
            'agent_id': int(os.environ['WECHAT_AGENT_ID']),
            'token': os.environ['WECHAT_TOKEN'],
            'encoding_aes_key': os.environ.get('WECHAT_ENCODING_AES_KEY'),
            'host': os.environ.get('WECHAT_HOST', '0.0.0.0'),
            'port': int(os.environ.get('WECHAT_PORT', 8080))
        }
        
        return cls(config)


# 使用示例
if __name__ == "__main__":
    # 从环境变量创建实例并启动
    wechat_im = WeChatIM.from_env()
    wechat_im.start()