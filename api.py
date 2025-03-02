from asyncio import Lock

from pcr_client import PcrClient
from player_pref import decrypt_xml
from utils import *

# 全局缓存的client登陆
client_cache = None
# 查询异步锁
query_lock: Lock = Lock()


# 查询PCR客户端配置
async def get_client_config() -> Optional[str]:
    cx_path = os.path.join(current_path, f'tw.sonet.princessconnect.v2.playerprefs.xml')
    return cx_path if os.path.isfile(cx_path) else None


# 获取PCR客户端
async def get_client() -> Optional[PcrClient]:
    global client_cache

    if client_cache is None and await get_client_config():
        ac_info = decrypt_xml(await get_client_config())
        _async_session = get_session_or_create('PcrClient', PROXY)
        client_cache = PcrClient(
            ac_info['UDID'],
            ac_info['SHORT_UDID'],
            ac_info['VIEWER_ID'],
            ac_info['TW_SERVER_ID'],
            _async_session
        )

    return client_cache