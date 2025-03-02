import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bsm_game import start_flatter
from utils import logger

# 谄媚布武机，启动！
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    logger.info('开始启动定时任务，等待下一次任务执行...')
    schedule = AsyncIOScheduler(event_loop=loop)
    schedule.add_job(start_flatter, CronTrigger(minute='*/4'))
    schedule.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('定时任务已被手动停止')
        schedule.shutdown()
