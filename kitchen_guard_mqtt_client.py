from paho.mqtt.client import Client as mqttClient
from paho.mqtt import publish, subscribe

from typing import Callable, Optional
import json #json en- and decoding


PIR = "0x00158d0005727f3a"
PLUG = "0xccccccfffee3d7aa"
LED = "0xbc33acfffe8b8ea8"

# TODO: HEUCOD event class
class z2mMsg:
    topic : str
    payload : str

class kitchenGuardMqttClient:
    def __init__(self, host: str, port: int, on_message_clbk: Callable[[Optional[z2mMsg]], None]):
        self.host = host
        self.port = port
        self.__client = mqttClient()
        self.__client.on_connect = self.__on_connect
        #self.__client.on_disconnect = self.__on_disconnect #Skal implementeres
        self.__client.on_message = self.__on_message #Her har du ændret højresiden af =
        self.__on_message_clbk = on_message_clbk
        self.connectionEstablished = False
        
    def __on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.connectionEstablished = True

    # TODO: Needs to be implemented 
    def __on_disconnect(self):
        pass
        
    def start(self):
        if self.connectionEstablished:
            return
        self.__client.connect(self.host, self.port)
        self.__client.loop_start()
        #subscribing to devices
        self.__client.subscribe("zigbee2mqtt/" + PIR) #PIR sensor
        self.__client.subscribe("zigbee2mqtt/" + PLUG) #power plug
        self.__client.subscribe("zigbee2mqtt/" + LED) #LED

    # TODO: Needs to be implemented
    def stop(self):
        pass
    
    # TODO: Needs to be updated to comply with HEUCOD parsing standard
    def __on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8") #decode json
        payload = json.loads(payload) #parse json into a dictionary
        currZ2mMsg = z2mMsg()
        currZ2mMsg.payload = payload
        currZ2mMsg.topic = msg.topic
        self.__on_message_clbk(currZ2mMsg)
    
    def publish_msg(self, topic:str, state:str):
        self.__client.publish(topic, f"{state}")

#L&A:
# 1) z2mMsg klassen skal implementeres endeligt således det er kompatibelt med event-formatet
# 2) High-level - funktionerne skal implementeres
# 3) Controller logikken skal implementeres j.f use-casen