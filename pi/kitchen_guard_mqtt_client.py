from kitchen_guard_model import kitchenGuardModel                               #importing the kitchenGuardModel
from heucod import HeucodEvent, HeucodEventType, HeucodEventJsonEncoder
from paho.mqtt.client import Client as mqttClient
from paho.mqtt.client import MQTTMessage as mqtMsg                               #importing mqtt client
from paho.mqtt import publish, subscribe                                        #importing publish and subscribe capabillities for the mqtt client

from typing import Callable, Optional                                           #importing callable and optional
import json #json en- and decoding
from datetime import datetime, timezone

# TODO: Needs commenting and clean-up

# Zigbee to MQTT message class #
# TODO: Needs evaluation event class
class z2mMsg:
    def __init__(self, inputdeviceFriendlyName:str, inputDeviceType:str, inputDeviceLocation:str, inputDeviceState:str):
        self.deviceFriendlyName = inputdeviceFriendlyName
        self.deviceType = inputDeviceType
        self.deviceLocation = inputDeviceLocation
        self.deviceState = inputDeviceState   

# Kitchen Guard MQTT client #
class kitchenGuardMqttClient:
    # KG MQTT client constructor #                                           
    def __init__(self,                                                          #Constructor arguments:
                    host: str,                                                  #host as string,
                    port: int,                                                  #port as int,
                    inputKitchenGuardModel:kitchenGuardModel,                   #environment model as kitchenGuardModel
                    on_message_clbk: Callable[[Optional[z2mMsg]], None]):       #callback function w. z2mMsg as argument, and return value of none
        self.host = host                                                        #client host IP
        self.port = port                                                        #client port
        self.__client = mqttClient()                                            #mqttClient instantiation
        self.__client.on_connect = self.__on_connect                            #when the client is connected, it call the __on_connect function 
        self.__client.on_disconnect = self.__on_disconnect                      #when the client is disconnected, it call the __on_disconnect function 
        self.__client.on_message = self.__on_message                            #when the client receives a message, it calls the __on_message function
        self.__on_message_clbk = on_message_clbk                                #when the callback function of the client is called, it "forwards" the call to the argument callback function
        self.connectionEstablished = False                                      #connection variable
        self.devicesModel = inputKitchenGuardModel                              #environment model   

    # __on_connect definition #    
    def __on_connect(self, client, userdata, flags, rc):                        #called when the client has connected
        print("Connected with result code " + str(rc))                          #connection result states is printed
        self.connectionEstablished = True                                       #internal connection status is updated

    # __on_disconnect definition #
    def __on_disconnect(self, client, userdata, flags, rc):                     #called when the client has disconnected
        print("Disconnected with result code " + str(rc))                       #connection result status is printed
        self.connectionEstablished = False                                      #internal connection status is updated

    # Start function #    
    def start(self):                                                            
        if self.connectionEstablished == True:                                  #if the client is already active, the function does not do anything
            return
        self.__client.connect(self.host, self.port)                             #otherwise it connects to the host on the port defined via. the call
        self.__client.loop_start()                                              #a thread which listens for messages is started
        plugList = self.devicesModel.getDevices("plug")
        for currDevice in plugList:
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.getFriendlyName())) 
        pirList = self.devicesModel.getDevices("pir")                           #a sublist of all pir sensors is computed
        for currDevice in pirList:                                             #then the client subscribes to all the PIR sensors in the model
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.getFriendlyName())) 
        ledList = self.devicesModel.getDevices("led")
        for currDevice in ledList:                                              #a sublist of all leds is computed
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.getFriendlyName())) #the client then subscribes to all the LEDs in the model

    # Stop function #
    def stop(self):
        if self.connectionEstablished == False:                                 #if the client is already inactive, the function does not do anything
            return
        self.__client.loop_stop()                                               #otherwise it stops the thread listening for messages
        self.__client.unsubscribe("zigbee2mqtt/" + (self.devicesModel.getDevices("plug")).getFriendlyName) #and unsubscribes to the power plug
        pirList = self.devicesModel.getDevices("pir")                           #a sublist of all pir sensors is computed then computed
        for currDevice in pirList:                                              #then the client unsubscribes to all the PIR sensors in the model
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.getFriendlyName) 
        ledList = self.devicesModel.getDevices("led")
        for currDevice in ledList:                                              #finally, a sublist of all leds is computed
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.getFriendlyName) #whereby the client can unsubscribe to all the LEDs in the model
        self.__client.disconnect()                                              #finally, the client disconnects from the host on the port
    
    # __on_message function #
    def __on_message(self, client, userdata, msg):                              #whenever a message is received by the mqtt client, this function is called
        if(self.devicesModel.findDevice(msg.topic)):
            currZ2mMsg = self.__parse(msg)
            self.__on_message_clbk(currZ2mMsg)                                      #finally, the __on_message_clbk function, defined in the controller,                                                                        #is called with the z2mMsg that has just been defined
        else:
            pass

    def __parse(self, msg:mqtMsg) -> z2mMsg:
        payload = msg.payload.decode("utf-8")                                   #first the payload is utf-8 decoded
        payload = json.loads(payload)                                           #then the payload is json-parsed into a dictionary
        currDevice = self.devicesModel.findDevice(msg.topic)
        if currDevice.getType() == "pir":
                currDevice.deviceState = payload["occupancy"]
        else:
            currDevice.deviceState = payload["state"]
        currZ2mMsg = z2mMsg(currDevice.getFriendlyName(),                       #a z2mMsg is instantiated
                            currDevice.getType(), 
                            currDevice.getLocation(), 
                            currDevice.getState())                                                   
        return currZ2mMsg
    
    #def serialize(self, inputMsg: z2mMsg) -> str:
    #    timestamp = datetime.now()
    #    return json.dumps({"device_id": inputMsg.deviceFriendlyName,
    #                        "device_type": inputMsg.deviceType,
    #                        "measurement": inputMsg.deviceState,
    #                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
    #                        })

    # publish_msg function # 
    def publish_msg(self, topic:str, payload:z2mMsg):                                #takes a topic as string and a state as string as input arguments
        if(topic == "kg"):
            payload = self.heucodify(payload)
            print(payload)
        self.__client.publish(topic, f"{payload}")                                #and then publishes this topic with this state                                    

    def heucodify(self, payload:z2mMsg):
        currEvent = HeucodEvent()
        if(payload.deviceType == "plug"):
            currEvent.event_type = HeucodEventType.DeviceUsageEvent
            currEvent.event_type_enum = int(HeucodEventType.DeviceUsageEvent)
            currEvent.timestamp = datetime.now(tz = timezone.utc)
            currEvent.value = payload.deviceState
            currEvent.device_vendor = "Immax"
            currEvent.device_model = "07048L"
        elif(payload.deviceType == "stove_absence_event"):
            currEvent.event_type = HeucodEventType.LowActivityWarning
            currEvent.event_type_enum = int(HeucodEventType.LowActivityWarning)
            currEvent.timestamp = datetime.now(tz = timezone.utc)
            currEvent.value = payload.deviceState
            currEvent.device_vendor = "non"
            currEvent.device_model = "non"
        return currEvent.to_json()
        
    