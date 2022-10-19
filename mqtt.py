import json
from umqtt_async import MQTTClient, RCV_PINGRESP_Exception, MQTT_OFFLINE_Exception
from utils import get_format_time, logger

class NETWORK_ERROR_Exception(Exception):
    pass

class Mqtt:
    def __init__(self, client_id, user, passwd, host, port, sub_topic, pub_topic):
        self.CLIENT_ID = client_id
        self.user = user
        self.password = passwd
        self.host = host
        self.host_port = port  
        self.sub_topic = sub_topic+'#'  # 订阅 TOPIC ID
        self.pub_topic = pub_topic    # 发布 TOPIC ID
        self.client = MQTTClient(
            client_id, host, port, user, passwd, keepalive=60)
        self.client.set_callback(self.mqtt_callback)
        self.isconn = False
        self.topics = {}
        self.ping_cnt = 0

    async def connect_server(self):
        try:
            await self.client.connect()
        except OSError as e:
            logger('connect_server |', e)
            raise NETWORK_ERROR_Exception
        else:
            logger(f'Connected to {self.host}')
            self.isconn = True

    async def mqtt_callback(self, topic, msg):
        topic = topic.decode('utf-8')
        msg = msg.decode('utf-8')
        logger(f'RCV MSG | topic: {topic}, msg: {msg}')
        data = json.loads(msg)
        callback = self.topics.get(topic)
        if callback:
            await callback(data)
    
    async def subscribe(self):
        try :
            await self.client.subscribe(self.sub_topic)
        except Exception as e:
            logger('subscribe |', e)
            raise NETWORK_ERROR_Exception
        else:
            logger(f'subscribed to {self.sub_topic} topic')
        

    async def ping(self):
        await self.client.ping()
        self.ping_cnt += 1
        # logger('ping...', self.ping_cnt)
        if self.ping_cnt > 3:
            raise MQTT_OFFLINE_Exception

    async def check_msg(self):
        try:
            await self.client.check_msg()
        except OSError as e:
            raise MQTT_OFFLINE_Exception

    async def publish(self, topic=None, **payloads):
        pub_topic = topic if topic else self.pub_topic
        try:
            await self.client.publish(pub_topic, json.dumps(payloads))
        except Exception as e:
            logger('publish |', e)
    
    def set_callback(self, topic:str, callback):
        logger('Set topic: ' + topic)
        self.topics[topic] = callback

    def set_last_will(self, topic, **msg):
        self.client.set_last_will(topic, json.dumps(msg))
        
    def reset(self):
        self.ping_cnt = 0
        self.isconn = False


