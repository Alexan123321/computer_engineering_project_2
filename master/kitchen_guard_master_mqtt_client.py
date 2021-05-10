from paho.mqtt.client import Client as mqttClient
from paho.mqtt.client import MQTTMessage as mqtMsg  # importing mqtt client
from paho.mqtt import publish, subscribe  # importing publish and subscribe capabillities for the mqtt client

from typing import Callable, Optional  # importing callable and optional
import json  # json en- and decoding
from datetime import datetime

TOPIC = "kg"


# TODO: Needs commenting and clean-up

# TODO: In mqtt_client implement:
# TODO:      1) Implement HEUCOD transformation of Z2MMsgs here!


class Z2MMsg:
    def __init__(self, friendly_name: str, device_type: str, device_state: str, timestamp: datetime):
        self.deviceFriendlyName = friendly_name
        self.deviceType = device_type
        #self.deviceLocation = device_location
        self.deviceState = device_state
        self.timestamp = timestamp


class KitchenGuardMasterMqttClient:
    def __init__(self,
                 host: str,
                 port: int,
                 on_message_clbk: Callable[[Optional[Z2MMsg]], None]):
        self.host = host
        self.port = port
        self.__client = mqttClient()
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.__on_message_clbk = on_message_clbk
        self.connectionEstablished = False

    def __on_connect(self, client, userdata, flags, rc):
        print("MQTT client Connected with result code " + str(rc))
        self.connectionEstablished = True

    def __on_disconnect(self, client, userdata, flags, rc):
        print("MQTT client Disconnected with result code " + str(rc))
        self.connectionEstablished = False

    def start(self):
        if self.connectionEstablished:
            return
        self.__client.connect(self.host, self.port)
        self.__client.loop_start()
        self.__client.subscribe(TOPIC)

    # Stop function #
    def stop(self):
        if not self.connectionEstablished:
            return
        self.__client.loop_stop()
        self.__client.unsubscribe(TOPIC)
        self.__client.disconnect()

    def __on_message(self, client, userdata, msg):
        self.__on_message_clbk(self.deserialize_json(msg))

    def serialize_json(self, msg: Z2MMsg) -> str:
        return json.dumps({
            "device_id": msg.deviceFriendlyName,
            "device_type": msg.deviceType,
            "measurement": msg.deviceState,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    def deserialize_json(self, msg: mqtMsg) -> Z2MMsg:
        payload = msg.payload.decode("utf-8")
        payload = json.loads(payload)
        print(payload)
        curr_z2m_msg = Z2MMsg(payload["device_id"],
                              payload["device_type"],
                              payload["measurement"],
                              payload["timestamp"])
        return curr_z2m_msg

    def publish_msg(self, topic: str, payload: str):
        self.__client.publish(topic, f"{payload}")
