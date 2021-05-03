from kitchen_guard_mqtt_client import kitchenGuardMqttClient, z2mMsg    #importing the kitchenGuardMQTTClient and the z2mMsg declared in the kitchen_guard_mqtt_client.py file
from kitchen_guard_model import kitchenGuardModel, zigbeeDevice
from enum import Enum                                                   #importing enumerated types
import time
import threading

# TODO: Needs commenting and CLEANUP
# TODO: Needs correct implementation of controller logic on _start_alarm function
# TODO: Needs correct thread implementation - alarmThreadState cannot be accessed from the start alarm function?

# Enumerated state type #
class State(Enum):
    ON = "ON"
    OFF = "OFF"

class kitchenGuardController:
    kitchenGuardState:State
    ctlStoveState:State
    alarmThreadState:int
    port:str
    host:str

    devicesModel:kitchenGuardModel

    def __init__(self, inputKitchenGuardModel:kitchenGuardModel):
        self.devicesModel = inputKitchenGuardModel
        self.alarmThread = threading.Thread(target = self._startAlarm)
        self.alarmThread.start()
    
    #when publish message is received from the device, then this function is run
    #def on_message(client, userdata, msg):
    def ctl_on_message(self, msg:z2mMsg):
        #Kitchen is empty and stove is on
        currDevice = self.devicesModel.findDevice(msg.topic)
        print("Controller event received!")
        #Occupancy status skal lige byttes rundt nedenstående
        if((currDevice.getType() == "pir") and (currDevice.getLocation() == "kitchen") and (msg.payload["occupancy"] == True) and (self.ctlStoveState == "ON") and (self.alarmThreadState == 0)):
            print("Beder om at starte alarm!")
            self.alarmThreadState = 1

        #Kitchen is no longer empty, but stove is on
        elif((currDevice.getType() == "pir") and (currDevice.getLocation() == "kitchen") and (msg.payload["occupancy"] == False) and (self.ctlStoveState == "ON") and (self.alarmThreadState == 1)): #Missing:  and (self.alarmThreadState == "ON")
            print("Beder alarm om at stoppe")
            alarmThreadState = 0

        if(currDevice.getType() == "plug"):
            print("Stove state updated!")
            self.ctlStoveState = msg.payload["state"]
            print(self.ctlStoveState)

    def start(self, inputPort:int, inputHost:str):
        self.kitchenGuardState = State.ON
        self.ctlStoveState = State.OFF
        self.alarmThreadState = 0
        self.port = inputPort
        self.host = inputHost
        self.myClient = kitchenGuardMqttClient(self.host, self.port, self.devicesModel, on_message_clbk = self.ctl_on_message)
        self.myClient.start()
        pass

    def stopKitchenGuard(self):
        self.kitchenGuardState = State.OFF
        self.myClient.stop()
        pass

    def _startAlarm(self):
        #preemptive alarm
        timerLimit = 18 * 1 #change *1 to *60 to get minutes
        currentTime = int(time.time())
        while(self.alarmThreadState == 1):
            time.sleep(1)
            if(int(time.time() >= currentTime + timerLimit)):
                break
        print("Tænder lys!")
        self._turnOnLED()

        #postemptive alarm
        timerLimit = 2 * 1 #change *1 to *60 to get minutes
        currentTime = int(time.time())
        while(self.alarmThreadState == 1):
            time.sleep(1)
            if(int(time.time() >= currentTime + timerLimit)):
                break
        print("Stopper alarm")      
        self.stopAlarm()

    def stopAlarm(self):
        self._turnOffStove()
        self._turnOffLED()
        self.alarmThreadState = 0
        self.alarmThread.join()

    def _turnOffStove(self):
        plugList = self.devicesModel.getDevices("plug")
        for currDevice in plugList:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "OFF")

    def _turnOnLED(self):
        ledList = self.devicesModel.getDevices("led")                           #a sublist of all pir sensors is computed then computed
        for currDevice in ledList:                                              #finally, a sublist of all leds is computed
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "ON") #whereby the client can unsubscribe to all the LEDs in the model

    def _turnOffLED(self):
        ledList = self.devicesModel.getDevices("led")                           #a sublist of all pir sensors is computed then computed
        for currDevice in ledList:                                              #finally, a sublist of all leds is computed
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "OFF") #whereby the client can unsubscribe to all the LEDs in the model

