import uasyncio
from machine import PWM, Pin

from config import sub_topic, pub_topic
from utils import get_format_time, logger
from network_manager import mqtt_client


class Lock:
    pwm = PWM(Pin(8), freq=50)
    checker_pin = Pin(2, Pin.IN)

    @classmethod
    async def open_door(cls, data):
        if await cls.checker():
            logger('Opening the door...')
            cls.pwm.duty(100)
        else:
            logger('The door is already opened!')
            await mqtt_client.publish(pub_topic+'gate', msg='The door is already opened!')
            return
        while True:
            await uasyncio.sleep_ms(600)
            if not await cls.checker():
                cls.pwm.duty(0)
                break
        logger('The door opened.')
        await mqtt_client.publish(pub_topic+'gate', msg="The door opened.")
    
    @classmethod
    async def checker(cls):
        tmp = []
        for i in range(3):
            await uasyncio.sleep_ms(50)
            tmp.append(cls.checker_pin.value())
        return tmp[0] | tmp[1] | tmp[2]
        


mqtt_client.set_callback(sub_topic+'gate/open', Lock.open_door)


monitor_pin = Pin(7, Pin.IN)

async def monitor():
    tmp = []
    for i in range(3):
        await uasyncio.sleep_ms(400)
        tmp.append(monitor_pin.value())
    return tmp[0] | tmp[1] | tmp[2]

