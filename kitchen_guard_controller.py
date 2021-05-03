from kitchen_guard_mqtt_client import kitchenGuardMqttClient, z2mMsg    #importing the kitchenGuardMQTTClient and the z2mMsg declared in the kitchen_guard_mqtt_client.py file
from enum import Enum                                                   #importing enumerated types

# Enumerated state type #
class State(Enum):
    ON = "ON"
    OFF = "OFF"

# TODO: friendlyName logic must be transferred to instantiations in main and objects in the model
# Friendly name declarations #
PIR = "0x00158d0005727f3a"
PLUG = "0xccccccfffee3d7aa"
LED = "0xbc33acfffe8b8ea8"

class kitchenGuardController:
    kitchenGuardState:State
    occupancyState:State
    stoveState:State
    LEDState:State
    port:str
    host:str

    def __init__(self):
        pass
    
    # TODO: Controller-logik skal implementeres her 
    #when publish message is received from the device, then this function is run
    #def on_message(client, userdata, msg):
    def ctl_on_message(self, msg : z2mMsg):        
        #if the topic is published by the PIR sensor
        if msg.topic == "zigbee2mqtt/" + PIR:
            self.occupancyState = msg.payload["occupancy"]
            if msg.payload["occupancy"] == True:
                self.myClient.publish_msg("zigbee2mqtt/" + LED + "/set/state", "OFF")
            else:
                self.myClient.publish_msg("zigbee2mqtt/" + LED + "/set/state", "ON")
        
        #if the topic is published by the power plug
        elif msg.topic == "zigbee2mqtt/" + PLUG:
            self.stoveState = msg.payload["state"]
        
        #if the topic is published by the LED
        else:
            self.LEDState = msg.payload["state"]

    def start(self, inputPort:int, inputHost:str):
        self.kitchenGuardState = State.ON
        self.occupancyState = State.OFF
        self.stoveState : State.OFF
        self.port = inputPort
        self.host = inputHost
        self.myClient = kitchenGuardMqttClient(self.host, self.port, on_message_clbk = self.ctl_on_message)
        self.myClient.start()
        pass

    def stopKitchenGuard(self):
        self.kitchenGuardState = State.OFF
        self.myClient.stop()
        pass

    # TODO: Skal implementeres - her ligger "timerlogikken"
    def _startAlarm(self):
        pass

    # TODO: Skal implementeres
    def stopAlarm(self):
        self._turnOffLED()
        pass

     # TODO: Skal implementeres
    def _turnOffStove(self):
        self.myClient.publish_msg("zigbee2mqtt/" + PLUG + "/set/state", "OFF")

    #TODO: When model is implemented, this function must turn ALL LEDs on
    def _turnOnLED(self):
        self.myClient.publish_msg("zigbee2mqtt/" + LED + "/set/state", "ON")

    #TODO: When model is implemented, this function must turn ALL LEDs off
    def _turnOffLED(self):
        self.myClient.publish_msg("zigbee2mqtt/" + LED + "/set/state", "OFF")
