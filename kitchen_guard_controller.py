from kitchen_guard_mqtt_client import kitchenGuardMqttClient, z2mMsg    #importing the kitchenGuardMQTTClient and the z2mMsg declared in the kitchen_guard_mqtt_client.py file
from kitchen_guard_model import kitchenGuardModel, zigbeeDevice
from enum import Enum                                                   #importing enumerated types
import time
import threading

# TODO: Needs commenting and CLEANUP

# Enumerated state type #
class State(Enum):
    ON = "ON"
    OFF = "OFF"

class kitchenGuardController:
    kitchenGuardState:State
    alarmThreadState:State
    ctlStoveState:State
    port:str
    host:str

    devicesModel:kitchenGuardModel

    def __init__(self, inputKitchenGuardModel:kitchenGuardModel):
        self.kitchenGuardState = State.ON
        self.ctlStoveState = State.OFF
        self.alarmThreadState = State.OFF
        self.devicesModel = inputKitchenGuardModel
        self.alarmThread = threading.Thread(target = self._startPreemptiveAlarm)
        self.alarmThread.start()
    
    def ctl_on_message(self, msg:z2mMsg):
        currDevice = self.devicesModel.findDevice(msg.topic)
        print("Controller event received!")
        if((currDevice.getType() == "pir") and (currDevice.getLocation() == "kitchen") and (msg.payload["occupancy"] == False) and (self.ctlStoveState == "ON") and (self.alarmThreadState == State.OFF)):
            print("Beder om at starte alarm!")
            self.alarmThreadState = State.ON

        elif((currDevice.getType() == "pir") and (currDevice.getLocation() == "kitchen") and (msg.payload["occupancy"] == True) and (self.ctlStoveState == "ON") and (self.alarmThreadState == State.ON)): 
            self.alarmThreadState = State.OFF

        if(currDevice.getType() == "plug"):
            print("Stove state updated!")
            self.ctlStoveState = msg.payload["state"]
            print(self.ctlStoveState)

    def start(self, inputPort:int, inputHost:str):
        self.port = inputPort
        self.host = inputHost
        self.myClient = kitchenGuardMqttClient(self.host, self.port, self.devicesModel, on_message_clbk = self.ctl_on_message)
        self.myClient.start()

    def stopKitchenGuard(self):
        self.kitchenGuardState = State.OFF
        self.myClient.stop()

    def _startPreemptiveAlarm(self):
        while(1):
            #preemptive alarm
            timerLimit = 18 * 1 #change *1 to *60 to get minutes
            currentTime = int(time.time())
            while(self.alarmThreadState == State.ON):
                time.sleep(1)
                print("Lyset tændes snart!")
                if(int(time.time() >= currentTime + timerLimit)):
                    print("Tænder lys!")
                    self._turnOnLED()
                    self._startAlarm()
                    break

    def _startAlarm(self):
        timerLimit = 30 * 1 #change *1 to *60 to get minutes
        currentTime = int(time.time())
        while(self.alarmThreadState == State.ON):
            time.sleep(1)
            if(int(time.time() >= currentTime + timerLimit)):
                print("Stopper alarm")      
                break
        self.stopAlarm()
        

    def stopAlarm(self):
        if(self.alarmThreadState == State.ON):
            self._turnOffStove()
            self._turnOffLED()
            self.alarmThreadState = State.OFF
        else:
            self._turnOffLED()

    def _turnOffStove(self):
        plugList = self.devicesModel.getDevices("plug")
        for currDevice in plugList:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "OFF")

    def _turnOnLED(self):
        ledList = self.devicesModel.getDevices("led")                           #a sublist of all pir sensors is computed then computed
        for currDevice in ledList:                                              #finally, a sublist of all leds is computed
            if(currDevice.getState() == "True"):
                self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "ON") #whereby the client can unsubscribe to all the LEDs in the model
                return
        for currDevice in ledList:
                self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "ON") #whereby the client can unsubscribe to all the LEDs in the model

    def _turnOffLED(self):
        ledList = self.devicesModel.getDevices("led")                           #a sublist of all pir sensors is computed then computed
        for currDevice in ledList:                                              #finally, a sublist of all leds is computed
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "OFF") #whereby the client can unsubscribe to all the LEDs in the model

