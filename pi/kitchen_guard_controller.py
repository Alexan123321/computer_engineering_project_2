from kitchen_guard_mqtt_client import KitchenGuardMqttClient, Z2mMsg
from kitchen_guard_model import KitchenGuardModel, ZigbeeDevice
from enum import Enum
import time
import threading

time_to_false = 90


class State(Enum):
    ON = "ON"
    OFF = "OFF"


class KitchenGuardController:
    kitchenGuardState: State
    alarmThreadState: State
    ctlStoveState: State
    port: str
    host: str
    devicesModel: KitchenGuardModel

    def __init__(self, input_kitchen_guard_model: KitchenGuardModel, input_port: int, input_host: str):
        self.ctlStoveState = State.OFF
        self.alarmThreadState = State.OFF
        self.devicesModel = input_kitchen_guard_model
        self.alarmThread = threading.Thread(target=self._start_preemptive_alarm)
        self.alarmThread.start()
        self.myClient = KitchenGuardMqttClient(input_host, input_port, self.devicesModel,
                                               on_message_clbk=self.ctl_on_message)

    def ctl_on_message(self, msg: Z2mMsg):
        print("Controller event received!")
        if (msg.deviceType == "pir") and (msg.deviceLocation == "kitchen") and (msg.deviceState == False) and (
                self.ctlStoveState == "ON") and (self.alarmThreadState == State.OFF):
            print("Starting preemptive alarm!")
            self.alarmThreadState = State.ON

        elif ((msg.deviceType == "pir") and (msg.deviceLocation == "kitchen") and (msg.deviceState == True) and (
                self.ctlStoveState == "ON") and (self.alarmThreadState == State.ON)):
            self.alarmThreadState = State.OFF

        if msg.deviceType == "plug":
            print("Stove state updated!")
            self.ctlStoveState = msg.deviceState
            self.myClient.publish_msg("kg", msg)
            print(self.ctlStoveState)

    def start(self):
        self.kitchenGuardState = State.ON
        self.myClient.start()

    def stop(self):
        self.kitchenGuardState = State.OFF
        self.myClient.stop()
        self.alarmThread.join()

    def _start_preemptive_alarm(self):
        while 1:
            timer_limit = 18 * 1  # change *1 to *60 to get minutes
            current_time = int(time.time())
            counter = timer_limit
            while self.alarmThreadState == State.ON:
                counter = counter - 1
                time.sleep(1)
                print(f"Turning on light in {counter}.")
                if int(time.time() >= current_time + timer_limit):
                    print("Starting alarm!")
                    self._turn_on_led()
                    self._start_alarm()
                    break
            if counter != timer_limit:
                print(f"Absence time: {time.time() - current_time + counter + time_to_false}")
                curr_z2m_msg = Z2mMsg("non", "stove_absence_event", "non",
                                      str(int(time.time()) - current_time + counter + time_to_false))
                self.myClient.publish_msg("kg", curr_z2m_msg)

    def _start_alarm(self):
        timer_limit = 5 * 1  # change *1 to *60 to get minutes
        current_time = int(time.time())
        counter = timer_limit
        while self.alarmThreadState == State.ON:
            counter = counter - 1
            time.sleep(1)
            print(f"Turning off alarm in {counter}.")
            if int(time.time() >= current_time + timer_limit):
                print("Stopping alarm")
                break
        if counter != timer_limit:
            print(f"Absence time: {time.time() - current_time + counter + 18 + time_to_false}")
            curr_z2m_msg = Z2mMsg("non", "stove_absence_event", "non",
                                  str(int(time.time()) - current_time + counter + 18 + time_to_false))
            self.myClient.publish_msg("kg", curr_z2m_msg)
        self.stop_alarm()

    def stop_alarm(self):
        if self.alarmThreadState == State.ON:
            self._turn_off_stove()
            self._turn_off_led()
            self.alarmThreadState = State.OFF
        else:
            self._turn_off_led()

    def _turn_off_stove(self):
        plug_list = self.devicesModel.get_devices("plug")
        for currDevice in plug_list:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.get_friendly_name() + "/set/state", "OFF")

    def _turn_on_led(self):
        pir_list = self.devicesModel.get_devices("pir")
        for currPir in pir_list:
            if currPir.get_state():
                print("There are people in the house!")
                led_list = self.devicesModel.get_devices("led")
                for currLed in led_list:
                    print("Turning on light at location!")
                    if currPir.get_location() == currLed.get_location():
                        self.myClient.publish_msg("zigbee2mqtt/" + currLed.get_friendly_name() + "/set/state",
                                                  "ON")  # whereby the client can unsubscribe to all the LEDs in the model
                        return
        led_list = self.devicesModel.get_devices("led")
        print("No people found in house... Turning ON all LEDs...")
        for currDevice in led_list:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.get_friendly_name() + "/set/state",
                                      "ON")  # whereby the client can unsubscribe to all the LEDs in the model

    def _turn_off_led(self):
        led_list = self.devicesModel.get_devices("led")  # a sublist of all pir sensors is computed then computed
        for currDevice in led_list:  # finally, a sublist of all leds is computed
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.get_friendly_name() + "/set/state",
                                      "OFF")  # whereby the client can unsubscribe to all the LEDs in the model
