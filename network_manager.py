import network
import uasyncio

from mqtt import client
from config import password, ssid, pub_topic
from utils import get_format_time, sync_time, logger


class wlan_manager:
    wlan = network.WLAN(network.STA_IF)

    @classmethod
    def is_conn(cls):
        return cls.wlan.isconnected()

    @classmethod
    async def connect(cls):
        network.WLAN(network.AP_IF).active(False)
        # 启动时先关掉 wifi, 避免一些奇奇怪怪的错误发生
        cls.wlan.active(False)
        await uasyncio.sleep(1)
        cls.wlan.active(True)
        logger('网络启动')
        cls.wlan.connect(ssid, password)

        while not cls.is_conn():
            logger("网络连接中...")
            await uasyncio.sleep_ms(500)
        logger('网络连接成功')

        # 同步时间
        await sync_time()

        # 连接 MQTT 服务器

        client.set_last_will(pub_topic+'offline', msg='Device offline.')
        await client.connect_server()
        await uasyncio.sleep(1)
        await client.subscribe()
        await client.publish(pub_topic+'online', msg='device online.', time=get_format_time())
