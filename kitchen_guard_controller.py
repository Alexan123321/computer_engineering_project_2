from kitchen_guard_mqtt_client import kitchenGuardMqttClient, z2mMsg
from paho.mqtt import publish, subscribe
from enum import Enum
import json                                                             #json en- and decoding

class State(Enum):
    ON = "ON"
    OFF = "OFF"

PIR = "0x00158d0005727f3a"
PLUG = "0xccccccfffee3d7aa"
LED = "0xbc33acfffe8b8ea8"


class kitchenGuardController:
    def __init__(self):
        self.occupancyState = State.OFF
        self.stoveState : State.OFF
        self.port = 1883
        self.host = "127.0.0.1"
        self.myClient = kitchenGuardMqttClient(self.host, self.port, on_message_clbk = self.ctl_on_message)
    
    # TODO: Controller-logik skal implementeres her 
    #when publish message is received from the device, then this function is run
    #def on_message(client, userdata, msg):
    def ctl_on_message(self, msg : z2mMsg):
        global occupancyState
        global stoveState
        global LEDState
        
        #if the topic is published by the PIR sensor
        if msg.topic == "zigbee2mqtt/" + PIR:
            occupancyState = msg.payload["occupancy"]
            if msg.payload["occupancy"] == True:
                self.myClient.publish_msg("zigbee2mqtt/" + LED + "/set/state", "OFF")
            else:
                self.myClient.publish_msg("zigbee2mqtt/" + LED + "/set/state", "ON")
        
        #if the topic is published by the power plug
        elif msg.topic == "zigbee2mqtt/" + PLUG:
            stoveState = msg.payload["state"]
        
        #if the topic is published by the LED
        else:
            LEDState = msg.payload["state"]

    # TODO: Skal implementeres
    def startKitchenGuard(self):
        pass

    # TODO: Skal implementeres
    def stopKitchenGuard(self):
        pass

    # TODO: Skal implementeres
    def startAlarm(self):
        pass

    # TODO: Skal implementeres
    def stopAlarm(self): 
        pass

    # TODO: Skal implementeres
    def turnOnStove(self):
        pass

     # TODO: Skal implementeres
    def turnOffStove(self):
        pass

     # TODO: Skal implementeres
    def turnOnLED(self):
        pass

     # TODO: Skal implementeres
    def turnOffLED(self):
        pass
