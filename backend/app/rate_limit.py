"""
レート制限設定
slowapi を使用して認証エンドポイント等にレート制限を適用
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# クライアントIPアドレスベースのレート制限
limiter = Limiter(key_func=get_remote_address)
