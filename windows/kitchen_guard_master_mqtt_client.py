from paho.mqtt.client import Client as mqttClient
from paho.mqtt.client import MQTTMessage as mqtMsg  
#importing mqttClient and message

from typing import Callable, Optional   # importing callable and optional
import json                             # json en- and decoding
from heucod import HeucodEvent, HeucodEventType

TOPIC = "kg"                            #database topic


class KitchenGuardMasterMqttClient:
    #init is the initializer it takes 3 arguments:
    #host is the ip address of the web page 
    #port is the TCP port which we communicate over
    #on_message_clbk is 
    def __init__(self,                  
                 host: str,
                 port: int,
                 on_message_clbk: Callable[[Optional[HeucodEvent]], None]):
                 # and a callable heucod event
        self.host = host        
        self.port = port                                    
        #host and port are assigned
        self.__client = mqttClient()                        
        #make mqttclient
        self.__client.on_connect = self.__on_connect        
        #make connect
        self.__client.on_disconnect = self.__on_disconnect  
        #make disconnect
        self.__client.on_message = self.__on_message        
        #make on_message
        self.__on_message_clbk = on_message_clbk            
        #make msg callback
        self.connectionEstablished = False                  
        #initialise MQTT client 

    def __on_connect(self, client, userdata, flags, rc):
        print("MQTT client Connected with result code " + str(rc))      
        #connection successfully established
        self.connectionEstablished = True

    def __on_disconnect(self, client, userdata, flags, rc):
        print("MQTT client Disconnected with result code " + str(rc))   
        #disconnect
        self.connectionEstablished = False

    def start(self):
        if self.connectionEstablished:                      
        #if connected       
            return                                              
            #do nothing and return to caller
        self.__client.connect(self.host, self.port)         
        #else establish connection to 
        self.__client.loop_start()                          
        #starts a new thread that calls start at regular intervals
        self.__client.subscribe(TOPIC)                      
        #subscribe to kg 

    # Stop function #
    def stop(self):
        if not self.connectionEstablished:                  
        #if disconnected
            return                                              
            #do nothing and return to caller
        self.__client.loop_stop()                           
        #else stops the loop
        self.__client.unsubscribe(TOPIC)                    
        #unsubscribes from kg
        self.__client.disconnect()                          
        #disconnects connection

    def __on_message(self, client, userdata, msg):          
        self.__on_message_clbk(self.deserialize_json(msg))  
        #make message into heucod format and send to database

    def deserialize_json(self, msg: mqtMsg) -> HeucodEvent:
        payload = msg.payload.decode("utf-8")                   
        #make message into utf-8 string so we can desiralize it
        payload = json.loads(payload)                           
        #desiralize json file into python objects
        curr_event = HeucodEvent()                              
        #make it into heucodevent format
        curr_event.timestamp = payload["timestamp"]             
        #store timestamp
        curr_event.value = payload["value"]                     
        #store value (state) or (absence time)
        curr_event.event_type = payload["eventType"]            
        #store event type which is partially done by checking the heucod file
        curr_event.event_type_enum = payload["eventTypeEnum"]   
        #store heucod type number
        curr_event.device_model = payload["deviceModel"]        
        #store what kind of device model we are using
        curr_event.device_vendor = payload["deviceVendor"]      
        #store device vendor

        return curr_event