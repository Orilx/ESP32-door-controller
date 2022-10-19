import network
import uasyncio

from mqtt import Mqtt, NETWORK_ERROR_Exception
from config import password, ssid, pub_topic
from utils import get_format_time, sync_time, logger
from config import client_id, host_ip, passwd, port, pub_topic, sub_topic, user

mqtt_client = Mqtt(client_id, user, passwd, host_ip,
              port, sub_topic, pub_topic)

class wlan_manager:
    wlan = network.WLAN(network.STA_IF)

    @classmethod
    def is_conn(cls):
        return cls.wlan.isconnected()

    @classmethod
    async def connect(cls):
        network.WLAN(network.AP_IF).active(False)
        # 重启 wifi, 避免一些奇奇怪怪的错误发生
        cls.wlan.active(False)
        await uasyncio.sleep(3)
        cls.wlan.active(True)
        logger('WLAN 启动')
        cls.wlan.connect(ssid, password)

        while not cls.is_conn():
            logger("WLAN 连接中...")
            await uasyncio.sleep_ms(500)
        logger('WLAN 连接成功')

        # 同步时间
        await sync_time()

        # 连接 MQTT 服务器
        try:
            mqtt_client.set_last_will(pub_topic+'offline', msg='Device_test offline.')
            await mqtt_client.connect_server()
            await uasyncio.sleep(1)
            await mqtt_client.subscribe()
        except NETWORK_ERROR_Exception:
            logger('无法连接到 MQTT 服务器...')
        else:
            await mqtt_client.publish(pub_topic+'online', msg='Device_test online.', time=get_format_time())
