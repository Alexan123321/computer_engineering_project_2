from enum import Enum
from heucod import HeucodEvent
from kitchen_guard_master_model import KitchenGuardMasterModel
from kitchen_guard_master_mqtt_client import KitchenGuardMasterMqttClient


class State(Enum):  
    #states used for guards
    ON = "ON"
    OFF = "OFF"


class KitchenGuardMasterController:
    kitchen_guard_state: State  
    port: str
    host: str
    
    mqttClient: KitchenGuardMasterMqttClient
    databaseModel: KitchenGuardMasterModel
    #The kitchen guard needs a guard which is used in the main file to determine when to sleep
    #there is also a port to communicate over and an IP address which we communicate to
    def __init__(self, model: KitchenGuardMasterModel):
        self.kitchen_guard_state = State.ON
        #set guard to be on which means the main file will have to wait until it goes off 
        self.databaseModel = model
        #initiate a model 

    def start(self, port: int, host: str):
        self.port = port                    
        self.host = host                    
        self.mqttClient = KitchenGuardMasterMqttClient(self.host, self.port, on_message_clbk=self.ctl_on_message)
        self.mqttClient.start()          
        #create and start the mqtt client   

    def stop(self):
        self.kitchen_guard_state = State.OFF
        #state is now off which means that the while loop in main will break 
        self.mqttClient.stop()
        #stop mqtt client

    def ctl_on_message(self, event: HeucodEvent):
        print("Controller event received!")
        res = self.databaseModel.store(event)
        #store events on the model which then stores them on the sql database
        if res == -1:
        #if the event comes back as negative then stop storing
            self.stop()