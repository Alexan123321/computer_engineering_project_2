from paho.mqtt.client import Client as mqttClient
from paho.mqtt.client import MQTTMessage as mqtMsg  # importing mqtt client

from typing import Callable, Optional  # importing callable and optional
import json  # json en- and decoding
from heucod import HeucodEvent, HeucodEventType

TOPIC = "kg"


class KitchenGuardMasterMqttClient:
    def __init__(self,
                 host: str,
                 port: int,
                 on_message_clbk: Callable[[Optional[HeucodEvent]], None]):
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

    def deserialize_json(self, msg: mqtMsg) -> HeucodEvent:
        payload = msg.payload.decode("utf-8")
        payload = json.loads(payload)
        curr_event = HeucodEvent()
        curr_event.timestamp = payload["timestamp"]
        curr_event.value = payload["value"]
        curr_event.event_type = payload["eventType"]
        curr_event.event_type_enum = payload["eventTypeEnum"]
        curr_event.device_model = payload["deviceModel"]
        curr_event.device_vendor = payload["deviceVendor"]

        return curr_event