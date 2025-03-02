import json
import logging
import os
import sys
from typing import Optional

import httpx
from httpx import Client, AsyncClient, Timeout


# 封装的会话对象缓存
class SessionCache:

    def __init__(self,
                 name: Optional[str],
                 session: Optional[Client | AsyncClient],
                 proxy: Optional[str] = None,
                 timeout: Optional[Timeout] = None):
        # 会话名
        self.name = name
        # 会话
        self.session = session
        # 代理
        self.proxy = proxy
        # 超时时间
        self.timeout = timeout

    @classmethod
    def create_empty(cls):
        return cls(None, None)


# 日志
_formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
_default_handler = logging.StreamHandler(sys.stdout)
_default_handler.setFormatter(_formatter)
logger = logging.getLogger('FlatterFubuki')
logger.addHandler(_default_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# 当前目录
current_path: str = os.path.dirname(__file__)
# 会话缓存
_async_session_map: dict[str, SessionCache] = {}
# 代理配置
with open(os.path.join(os.path.dirname(__file__), 'proxy.json'), 'r', encoding='utf-8') as _config:
    _data = json.load(_config)
PROXY: Optional[str] = _data.get('PROXY', None)


# 获取缓存的session | create_if_none: 是否要在不存在的时候创建
def get_session_or_create(
        name: str,
        proxy: Optional[str] = None,
        create_if_none: bool = True
) -> AsyncClient:
    # 获取缓存中的会话
    session: Optional[Client | AsyncClient] = _async_session_map.get(name, SessionCache.create_empty()).session

    if session:
        return session
    if create_if_none:
        return create_async_session(name, True, proxy)

    raise Exception(f'找不到 AsyncClient [{name}]')


# 重建已有的异步会话
async def rebuild_async_session(name: str) -> AsyncClient:
    if name not in _async_session_map:
        raise Exception(f'找不到 AsyncClient [{name}]')
    session_cache = _async_session_map.get(name, SessionCache.create_empty())
    await session_cache.session.aclose()
    _async_session_map.pop(name)
    return create_async_session(name, True, session_cache.proxy, session_cache.timeout)


# 手动关闭异步会话
async def close_async_session(name: str, session: AsyncClient):
    if isinstance(session, AsyncClient):
        await session.aclose()
        _async_session_map.pop(name)
    else:
        pass


# 创建异步session | is_save: 是要保存至缓存 还是 一次性
def create_async_session(name: str, is_save: bool = False, proxy: Optional[str] = None, timeout: Optional[Timeout] = None) -> AsyncClient:
    if name in _async_session_map:
        raise Exception(f'AsyncSession [{name}] 已经存在')
    # 设置默认超时时间
    timeout = timeout if timeout else Timeout(10, read=10)
    # 创建客户端
    async_session = httpx.AsyncClient(proxy=proxy, verify=False, timeout=timeout)
    if is_save:
        _save_session(name, async_session, proxy, timeout)
    return async_session


# 保存session至缓存
def _save_session(name: str, session: Client | AsyncClient, proxy: Optional[str] = None, timeout: Optional[Timeout] = None):
    if isinstance(session, AsyncClient):
        _async_session_map[name] = SessionCache(name, session, proxy, timeout)
    else:
        raise Exception('不支持的 Session 类型，只支持 [ClientSession]')