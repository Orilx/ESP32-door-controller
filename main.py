import uasyncio

from config import pub_topic
from mqtt import client
from network_manager import wlan_manager
from mi_sensor import get_temp
from gate_controller import Lock, monitor
from utils import  logger, sync_time

loop = uasyncio.get_event_loop()


def create_task(cycle, mode='s'):
    """
    创建周期任务
    mode: 设定周期模式,默认值为 's'
          当为 's' 时按秒计时，为 'ms' 时按毫秒计时 
    """
    def inner(func):
        async def wrapper():
            while True:
                if mode == 'ms':
                    await uasyncio.sleep_ms(cycle)
                else:
                    await uasyncio.sleep(cycle)
                await func()
        loop.create_task(wrapper())
        return wrapper
    return inner


# 在下方添加任务


@create_task(0)
async def check_connection():
    """
    检查是否连接网络
    """
    if not wlan_manager.is_conn():
        logger('网络未连接')
        await wlan_manager.connect()
    # else:
    #     print('网络已连接')


@create_task(200, 'ms')
async def check_msg():
    if wlan_manager.is_conn() and client.isconn:
        await client.check_msg()


s_cache = 0


@create_task(3)
async def door_monitor():
    if wlan_manager.is_conn() and client.isconn:
        global s_cache
        status = await monitor()
        # print(status, s_cache, status ^ s_cache)
        if status ^ s_cache:
            await client.publish(pub_topic+'gate/door_monitor', status='Door opened!' if status else 'Door closed!')
            s_cache = status


@create_task(30)
async def keep_alive():
    if wlan_manager.is_conn():
        await client.ping()


@create_task(600)
async def sync():
    """
    十分钟同步一次时间
    """
    if wlan_manager.is_conn():
        await sync_time()
 

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()

