from kitchen_guard_model import KitchenGuardModel   # importing the KitchenGuardModel
from heucod import HeucodEvent, HeucodEventType     # importing Heucod events and the event types
from paho.mqtt.client import Client as mqttClient   # importing the mqtt client as Client
from paho.mqtt.client import MQTTMessage as mqtMsg  # importing mqtt message as mqtMsg

from typing import Callable, Optional               # importing callable and optional
import json                                         # importing json en- and decoding
from datetime import datetime, timezone             # importing datetime and timezone


# Zigbee to MQTT message class #
class Z2mMsg:
    def __init__(self, input_device_friendly_name: str, input_device_type: str, input_device_location: str,
                 input_device_state: str):
        self.deviceFriendlyName = input_device_friendly_name
        self.deviceType = input_device_type
        self.deviceLocation = input_device_location
        self.deviceState = input_device_state


# Kitchen Guard MQTT client #
class KitchenGuardMqttClient:
    # KG MQTT client constructor #                                           
    def __init__(self, host: str, port: int, input_kitchen_guard_model: KitchenGuardModel,  #environment model as KitchenGuardModel
                 on_message_clbk: Callable[[Optional[Z2mMsg]], None]):       #callback function w. Z2mMsg as argument, and return value of none
        self.host = host                                                        #client host IP
        self.port = port                                                        #client port
        self.__client = mqttClient()                                            #mqttClient instantiation
        self.__client.on_connect = self.__on_connect                            #when the client is connected, it call the __on_connect function 
        self.__client.on_disconnect = self.__on_disconnect                      #when the client is disconnected, it call the __on_disconnect function 
        self.__client.on_message = self.__on_message                            #when the client receives a message, it calls the __on_message function
        self.__on_message_clbk = on_message_clbk                                #when the callback function of the client is called, it "forwards" the call to the argument callback function
        self.connection_established = False                                      #connection variable
        self.devicesModel = input_kitchen_guard_model                           #environment model

    # __on_connect definition #    
    def __on_connect(self, client, userdata, flags, rc):                        #called when the client has connected
        print("Connected with result code " + str(rc))                          #connection result states is printed
        self.connection_established = True                                       #internal connection status is updated

    # __on_disconnect definition #
    def __on_disconnect(self, client, userdata, flags, rc):                     #called when the client has disconnected
        print("Disconnected with result code " + str(rc))                       #connection result status is printed
        self.connection_established = False                                      #internal connection status is updated

    # Start function #    
    def start(self):                                                            
        if self.connection_established:                                         #if the client is already active, the function does not do anything
            return
        self.__client.connect(self.host, self.port)                             #otherwise it connects to the host on the port defined via. the call
        self.__client.loop_start()                                              #a thread which listens for messages is started
        plug_list = self.devicesModel.get_devices("plug")
        for currDevice in plug_list:
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.get_friendly_name()))
        pir_list = self.devicesModel.get_devices("pir")                           #a sublist of all pir sensors is computed
        for currDevice in pir_list:                                             #then the client subscribes to all the PIR sensors in the model
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.get_friendly_name()))
        led_list = self.devicesModel.get_devices("led")
        for currDevice in led_list:                                              #a sublist of all leds is computed
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.get_friendly_name())) #the client then subscribes to all the LEDs in the model

    # Stop function #
    def stop(self):
        if self.connection_established:                                 #if the client is already inactive, the function does not do anything
            return
        self.__client.loop_stop()                                               #otherwise it stops the thread listening for messages
        self.__client.unsubscribe("zigbee2mqtt/" + (self.devicesModel.get_devices("plug")).get_friendly_name) #and unsubscribes to the power plug
        pir_list = self.devicesModel.get_devices("pir")                           #a sublist of all pir sensors is computed then computed
        for currDevice in pir_list:                                              #then the client unsubscribes to all the PIR sensors in the model
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.get_friendly_name)
        led_list = self.devicesModel.get_devices("led")
        for currDevice in led_list:                                              #finally, a sublist of all leds is computed
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.get_friendly_name) #whereby the client can unsubscribe to all the LEDs in the model
        self.__client.disconnect()                                              #finally, the client disconnects from the host on the port
    
    # __on_message function #
    def __on_message(self, client, userdata, msg):                              #whenever a message is received by the mqtt client, this function is called
        if self.devicesModel.find_device(msg.topic):
            curr_z2m_msg = self.__parse(msg)
            self.__on_message_clbk(curr_z2m_msg)                                      #finally, the __on_message_clbk function, defined in the controller,                                                                        #is called with the Z2mMsg that has just been defined
        else:
            pass

    def __parse(self, msg:mqtMsg) -> Z2mMsg:
        payload = msg.payload.decode("utf-8")                                   #first the payload is utf-8 decoded
        payload = json.loads(payload)                                           #then the payload is json-parsed into a dictionary
        curr_device = self.devicesModel.find_device(msg.topic)
        if curr_device.get_type() == "pir":
            curr_device.deviceState = payload["occupancy"]
        else:
            curr_device.deviceState = payload["state"]
        curr_z2m_msg = Z2mMsg(curr_device.get_friendly_name(), curr_device.get_type(), curr_device.get_location(),
                              curr_device.get_state())
        return curr_z2m_msg

    # publish_msg function # 
    def publish_msg(self, topic: str, payload: Z2mMsg):                                #takes a topic as string and a state as string as input arguments
        if topic == "kg":
            payload = self.heucodify(payload)
            print(payload)
        self.__client.publish(topic, f"{payload}")                                #and then publishes this topic with this state                                    

    @staticmethod
    def heucodify(payload: Z2mMsg):
        curr_event = HeucodEvent()
        if payload.deviceType == "plug":
            curr_event.event_type = HeucodEventType.DeviceUsageEvent
            curr_event.event_type_enum = int(HeucodEventType.DeviceUsageEvent)
            curr_event.timestamp = datetime.now(tz=timezone.utc)
            curr_event.value = payload.deviceState
            curr_event.device_vendor = "Immax"
            curr_event.device_model = "07048L"
        elif payload.deviceType == "stove_absence_event":
            curr_event.event_type = HeucodEventType.LowActivityWarning
            curr_event.event_type_enum = int(HeucodEventType.LowActivityWarning)
            curr_event.timestamp = datetime.now(tz=timezone.utc)
            curr_event.value = payload.deviceState
            curr_event.device_vendor = "non"
            curr_event.device_model = "non"
        return curr_event.to_json()
