from kitchen_guard_mqtt_client import kitchenGuardMqttClient, z2mMsg    #importing the kitchenGuardMQTTClient and the z2mMsg declared in the kitchen_guard_mqtt_client.py file
from kitchen_guard_model import kitchenGuardModel, zigbeeDevice
from enum import Enum                                                   #importing enumerated types
import time
import threading

time_to_false = 90

# TODO: Needs commenting and CLEANUP
# TODO: zigbeeTopic = "zigbee2mqtt/" i.e definér konstanter

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
        print("Controller event received!")
        if((msg.deviceType == "pir") and (msg.deviceLocation == "kitchen") and (msg.deviceState == False) and (self.ctlStoveState == "ON") and (self.alarmThreadState == State.OFF)):
            print("Starting preemptive alarm!")
            self.alarmThreadState = State.ON

        elif((msg.deviceType == "pir") and (msg.deviceLocation == "kitchen") and (msg.deviceState == True) and (self.ctlStoveState == "ON") and (self.alarmThreadState == State.ON)): 
            self.alarmThreadState = State.OFF

        if(msg.deviceType == "plug"):
            print("Stove state updated!")
            self.ctlStoveState = msg.deviceState
            #TODO: Here must the current state of the stove be forwarded to the mqtt_client, which forwards it to the web_client
            self.myClient.publish_msg("kg", msg)
            #self.myClient.publish_msg("kg", self.myClient.serialize(msg)) #Being tested once database is running
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
            counter = timerLimit
            while(self.alarmThreadState == State.ON):
                counter = counter - 1
                time.sleep(1)
                print(f"Turning on light in {counter}.")
                if(int(time.time() >= currentTime + timerLimit)):
                    print("Starting alarm!")
                    self._turnOnLED()
                    self._startAlarm()
                    break
            if(counter != timerLimit):
                print(f"Absence time: {time.time() - currentTime + counter + time_to_false}")
                currZ2mMsg = z2mMsg("non",                       #a z2mMsg is instantiated
                                    "stove_absence_event", 
                                    "non", 
                                    str(int(time.time()) - currentTime + counter + time_to_false))
                #self.myClient.publish_msg("kg", self.myClient.serialize(currZ2mMsg)) #Being tested once database is running
                self.myClient.publish_msg("kg", currZ2mMsg)        

    def _startAlarm(self):
        timerLimit = 5 * 1 #change *1 to *60 to get minutes
        currentTime = int(time.time())
        counter = timerLimit
        while(self.alarmThreadState == State.ON):
            counter = counter - 1
            time.sleep(1)
            print(f"Turning off alarm in {counter}.")
            if(int(time.time() >= currentTime + timerLimit)):
                print("Stopping alarm")      
                break
        if(counter != timerLimit):
            print(f"Absence time: {time.time() - currentTime + counter + 18 + time_to_false}")
            currZ2mMsg = z2mMsg("non",                       #a z2mMsg is instantiated
                                "stove_absence_event", 
                                "non", 
                                str(int(time.time()) - currentTime + counter + 18 + time_to_false))
            #self.myClient.publish_msg("kg", self.myClient.serialize(currZ2mMsg)) #Being tested once database is running
            self.myClient.publish_msg("kg", currZ2mMsg)   
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
        pirList = self.devicesModel.getDevices("pir")                           #a sublist of all pir sensors is computed then computed
        for currPir in pirList:                                              #finally, a sublist of all leds is computed
            if(currPir.getState() == True):
                print("There are people in the house!")
                ledList = self.devicesModel.getDevices("led")
                for currLed in ledList:
                    print("Turning on light at location!")
                    if currPir.getLocation() == currLed.getLocation():
                        self.myClient.publish_msg("zigbee2mqtt/" + currLed.getFriendlyName() + "/set/state", "ON") #whereby the client can unsubscribe to all the LEDs in the model
                        return
        ledList = self.devicesModel.getDevices("led")
        print("No people found in house... Turning ON all LEDs...")
        for currDevice in ledList:
                self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "ON") #whereby the client can unsubscribe to all the LEDs in the model

    def _turnOffLED(self):
        ledList = self.devicesModel.getDevices("led")                           #a sublist of all pir sensors is computed then computed
        for currDevice in ledList:                                              #finally, a sublist of all leds is computed
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.getFriendlyName() + "/set/state", "OFF") #whereby the client can unsubscribe to all the LEDs in the model

