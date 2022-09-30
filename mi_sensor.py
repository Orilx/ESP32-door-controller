import aioble

from utils import get_format_time
from config import MI_DEVICE_MAC, sub_topic, pub_topic
from mqtt import client


def decode_adv_data(adv_data):
    hex_str = ''

    for i in adv_data[10:14]:
        hex_str += '%02x' % i

    temp = int(hex_str[:4], 16)/10
    humi = int(hex_str[4:6], 16)
    batt = int(hex_str[6:], 16)

    return temp, humi, batt


async def get_data():
    async with aioble.scan(30000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.device.addr_hex() == MI_DEVICE_MAC and result.adv_data:
                return decode_adv_data(result.adv_data)
    return None


async def get_temp(t):
    data = await get_data()

    if data:
        msg = {
            'temp': data[0],
            'humi': data[1],
            'batt': data[2],
            'remark': '',
            'time': get_format_time(),
        }
    else:
        msg = {
            'temp': -1,
            'humi': -1,
            'batt': -1,
            'remark': '未找到设备，请稍后再试',
            'time': get_format_time(),
        }

    await client.publish(pub_topic+'gate/mi_sensor', **msg)

client.set_callback(sub_topic+'gate/scan_mi_sensor', get_temp)
