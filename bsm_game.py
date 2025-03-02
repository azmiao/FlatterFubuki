import asyncio
import random
import secrets

import httpx

from api import get_client, query_lock
from pcr_client import ApiException
from utils import rebuild_async_session, logger


# 接口请求
async def query_api(api_uri: str, body: dict):
    client_clan = await get_client()
    if client_clan is None:
        raise Exception('客户端缓存为空且[tw.sonet.princessconnect.v2.playerprefs.xml]文件不存在')
    async with query_lock:
        try:
            res = await client_clan.callapi(api_uri, body)
            return res
        except ApiException:
            # 一般的请求异常 | 可尝试一次重新登录请求
            client_clan.shouldLogin = True
        except httpx.TransportError:
            # 特殊的请求异常 | 可能需要重建会话重新登录
            client_clan.shouldLogin = True
            # 重建并更新会话至客户端
            async_session = await rebuild_async_session('PcrClientClan')
            client_clan.update_async_session(async_session)
        # 如果需要登录就一直等待其进行登录
        while client_clan.shouldLogin:
            await client_clan.login()
        # 第二次请求客户端接口
        res = await client_clan.callapi(api_uri, body)
        return res


# 胜率计算 | base_power比current_power大时才走这
async def calculate_success(base_power: int, current_power: int) -> bool:
    total_power = base_power / 3 + current_power
    # 计算胜率（基础战力占总战力的比例）
    win_rate = base_power / total_power
    # 生成随机结果
    return random.random() < win_rate


# 开始战斗
async def start_flatter():
    # 进入活动本
    _ = await query_api('/event/hatsune/top', {'event_id': 10156})

    # 进入小游戏获取当前点数
    await asyncio.sleep(0.5)
    bsm_top = await query_api('/bsm/top', {'from_system_id': 6001})
    base_point = bsm_top.get('battle_point', 0)

    # 选择己方的第一支队伍
    self_machines = bsm_top.get('machines', [])
    select_machine = self_machines[0]
    machine_id = select_machine.get('machine_id', 1)
    self_power = select_machine.get('power', 0)
    logger.info(f'初始点数：{str(base_point)} | 选择己方队伍{str(machine_id)}(战力{str(self_power)})')

    # 战斗后的点数
    current_point = bsm_top.get('battle_point', 0)

    # 找到一个战力比自己低的对手
    while current_point - base_point < 800:
        power = 999999
        rival = {}
        machine = {}
        while power > self_power:
            await asyncio.sleep(0.5)
            # 查询对手列表
            battle_prepare_data = await query_api('/bsm/rival_battle_prepare', {'from_system_id': 6001})
            rivals_list = battle_prepare_data.get('rivals', [])
            rival = rivals_list[0]
            machine = rival.get('machine', {})
            power = machine.get('power', 0)

        rival_type = rival.get('type', 11)
        machine_name = machine.get('machine_name', '')
        logger.info(f'准备和{machine_name}(战力{str(power)})进行小游戏对战')

        # 对战开始
        await asyncio.sleep(0.5)
        token_hex = secrets.token_hex(8)
        data = {
            "type": rival_type,
            "enemy_viewer_id": 0,
            "machine_id": machine_id,
            "token": token_hex,
            "from_system_id": 6001
        }
        _ = await query_api('/bsm/battle_start', data)

        # 等待10秒对战结束
        await asyncio.sleep(10)

        # 计算是否失败
        is_success = await calculate_success(self_power, power)

        # 上报对战结果
        data = {
            "battle_result": 3 if is_success else 1,
            "token": token_hex,
            "from_system_id": 6001,
        }
        battle_finish = await query_api('/bsm/battle_finish', data)
        # 更新当前分数
        current_point = battle_finish.get('battle_point', 0)
        logger.info(f'对战结果：{str(is_success)} | 当前分数{str(current_point)}')

    # 先回主界面
    await asyncio.sleep(0.5)
    _ = await query_api('/bsm/top', {'from_system_id': 6001})

    # 然后收任务奖励
    await asyncio.sleep(0.5)
    await query_api('/bsm/mission_accept', {'mission_id': 60000, 'from_system_id': 6001})
    logger.info(f'已完成800分任务，成功领取一次奖励')
