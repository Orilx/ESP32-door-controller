import uasyncio

from config import pub_topic
from mqtt import RCV_PINGRESP_Exception, MQTT_OFFLINE_Exception
from network_manager import wlan_manager, mqtt_client
from mi_sensor import get_temp
from gate_controller import Lock, monitor
from utils import  logger, sync_time

loop = uasyncio.get_event_loop()

s_cache = 0

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


async def reconnect():
    await uasyncio.sleep(1)
    mqtt_client.reset()
    await wlan_manager.connect()


# 在下方添加任务


@create_task(0)
async def check_connection():
    """
    检查是否连接 Wifi
    """
    if not wlan_manager.is_conn():
        logger('WLAN 未连接')
        try:
            await wlan_manager.connect()
        except OSError:
            pass
    # else:
    #     print('WLAN 已连接')


@create_task(200, 'ms')
async def check_msg():
    if wlan_manager.is_conn() and mqtt_client.isconn:
        try:
            await mqtt_client.check_msg()
        except RCV_PINGRESP_Exception:
            mqtt_client.ping_cnt -= 1
            # logger('RCV_PINGRESP', mqtt_client.ping_cnt)
        except MQTT_OFFLINE_Exception:
            logger('已与 MQTT 服务器断开连接')
            await reconnect()
        except OSError as e:
            logger('check_msg |', e)


@create_task(3)
async def door_monitor():
    if wlan_manager.is_conn() and mqtt_client.isconn:
        global s_cache
        door_status = await monitor()
        # print(status, s_cache, status ^ s_cache)
        if door_status ^ s_cache:
            await mqtt_client.publish(pub_topic+'gate/door_monitor', status='Door opened!' if door_status else 'Door closed!')
            s_cache = door_status


@create_task(30)
async def keep_alive():
    if wlan_manager.is_conn() and mqtt_client.isconn:
        try :
            await mqtt_client.ping()
        except MQTT_OFFLINE_Exception:
            logger('已与 MQTT 服务器断开连接')
            await reconnect()
        except OSError as e:
            logger('keep_alive |', e)


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

