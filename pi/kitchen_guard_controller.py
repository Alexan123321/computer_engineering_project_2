# The MQTT client is the broker between the hardware devices that communicate via. Zigbee and the software
# applications that communicate via. MQTT.
# The Z2mMsg is the internal datatype used on the Pi to convert MQTT messages
# into a less extensive format. As they are both included from the kitchen_guard_mqtt_client.py, the reader is urged to
# visit this file to obtain an elaborate understanding.
from kitchen_guard_mqtt_client import KitchenGuardMqttClient, Z2mMsg
# The model, implemented in the kitchen_guard_model.py, is also imported. The model is a software abstraction of the
# physical environment. The idea here is to implement the model-view-controller pattern, but without a view, as the app-
# lication being run on the Pi does not need a presentation layer. The model contains information about all the physical
# devices, thus the controller can simply ask the model to be informed, and will be so.
from kitchen_guard_model import KitchenGuardModel
# The enumerated types library is used to make "ON" and "OFF" state types used in all state machines.
# The state machines include the KitchenGuardController and the alarmThread.
from enum import Enum
# The time library is used for the timers measuring the absence of the user.
import time
# The threading library is used for the tread that performs the logic of the alarm.
import threading

# This constant is the time that passes between the user leaving the kitchen and the PIR sensor detecting it. It is
# used in the _start_preemptive_alarm function and the _start_alarm_function.
time_to_false = 90


# This is the enumerated state class that is used to make a state machine for both the controller, but also for the
# thread upon which the alarm is being run.
class State(Enum):
    ON = "ON"
    OFF = "OFF"


# This is the controller class on the Pi. The controller class is responsible for handling all logic revolving around
# the Kitchen Guard system. The controller has three internal states: one for itself, one for the alarm thread and one
# for the stove.
class KitchenGuardController:
    # The kitchenGuardState ensures that the controller keeps being "ON" until it is turned "OFF". This seems rather
    # self-explanatory, but it is an important snippet, as it ensures that the application on the Pi is not run only
    # once but rather as long as the user has not turned it "OFF".
    kitchenGuardState: State
    # The alarmThreadState is the "ON"-"OFF" state of the thread upon which the alarm logic is handled. The reason that
    # this is on a separate thread is that it ensures that the controller can still evaluate events forwarded by the
    # kitchen_guard_mqtt_client without coming to a halt, when executing code of its own.
    alarmThreadState: State
    # The ctlStoveState is the controller's local perception of the current state of the stove. This is used to ensure
    # that the correct logic is actuated, dependent on the state of the stove.
    ctlStoveState: State
    # The devicesModel is the software abstraction of the physical environment. To ensure that the controller can
    # perceive this, it has been injected into the controller upon initialization.
    devicesModel: KitchenGuardModel

    # The init function is the initializer of the KitchenGuardController class. As can be seen, it takes three
    # arguments:
    # 1) A KitchenGuardModel / software abstraction of the physical environment.
    # 2) An int which is the port of the MQTT client.
    # 3) A string which is the host IP of the MQTT client.
    def __init__(self, input_kitchen_guard_model: KitchenGuardModel, input_port: int, input_host: str):
        # When initialized, the local perception of the stove is set to "OFF".
        self.ctlStoveState = State.OFF
        # Furthermore, the alarmThreadState is set to "OFF".
        self.alarmThreadState = State.OFF
        # The devices model injected is stored. The reason is that the controller applies many of the functions on the
        # model.
        self.devicesModel = input_kitchen_guard_model
        # The actual alarmThread is instantiated with the _start_preemptive_alarm function. As long as the
        # alarmThreadState is "OFF", this function does nothing.
        self.alarmThread = threading.Thread(target=self._start_preemptive_alarm)
        # And the alarmThread is started.
        self.alarmThread.start()
        # The MQTT client is initialized with four arguments:
        # 1) The host
        # 2) The port
        # 3) The KitchenGuardModel. The reason is that it is the responsibility of the MQTT client to update the model.
        # 4) A callback function, ctl_on_message, which is activated whenever the MQTT client receives a message from
        # one of the sensors / actuators.
        self.myClient = KitchenGuardMqttClient(input_host, input_port, self.devicesModel,
                                               on_message_clbk=self.ctl_on_message)

    # The ctl_on_message function is where most of the logic related to events is handled. As can be seen, the argument
    # is a Z2mMsg which is the datatype that the application on the Pi is structured around.
    def ctl_on_message(self, msg: Z2mMsg):
        # Whenever a Z2mMsg is received by the controller, a notification is printed to the terminal.
        print("Controller event received!")
        # If the Z2mMsg is sent from the motion sensor in the kitchen, the user is not in the kitchen, indicated by a
        # "False" state, and the alarm HAS NOT yet been started...
        if (msg.deviceType == "pir") and (msg.deviceLocation == "kitchen") and (msg.deviceState == False) and (
                self.ctlStoveState == "ON") and (self.alarmThreadState == State.OFF):
            # The preemptive alarm starts.
            print("Starting preemptive alarm!")
            # By setting the state of the alarm thread to "ON".
            self.alarmThreadState = State.ON
        # If the Z2mMsg is sent from the motion sensor in the kitchen, the user has returned to the kitchen, indicated
        # by a "True" state, and the alarm HAS already been started...
        elif ((msg.deviceType == "pir") and (msg.deviceLocation == "kitchen") and (msg.deviceState == True) and (
                self.ctlStoveState == "ON") and (self.alarmThreadState == State.ON)):
            # Thus, a notification that the preemptive alarm stops is printed to the terminal.
            print("Stopping preemptive alarm!")
            # And the alarm is stopped, but setting the state of the alarm thread to "OFF".
            self.alarmThreadState = State.OFF
        # If the Z2mMsg is sent from the power plug...
        elif msg.deviceType == "plug":
            # The local state of the stove is updated,
            print("Stove state updated!")
            # by assigning the state in the Z2mMsg to the ctlStoveState variable.
            self.ctlStoveState = msg.deviceState
            # and forwarding the message to the MQTT client with the "kg" topic that forwards it to the Windows app,
            # ensuring all stove events are storing in the database.
            self.myClient.publish_msg("kg", msg)

    # The start function is the one starting the controller.
    def start(self):
        # It changes the state of the controller to "ON".
        self.kitchenGuardState = State.ON
        # And starts the MQTT client.
        self.myClient.start()

    # The stop function is the one stopping the controller.
    def stop(self):
        # It changes the state of the controller to "OFF".
        self.kitchenGuardState = State.OFF
        # And stops the MQTT client.
        self.myClient.stop()
        # And finally joins the thread upon which the alarm is being run.
        self.alarmThread.join()

    # The _start_preemptive_alarm is the function that is being iterated on the alarm thread as long as the controller
    # is not stopped. It is on this that the preemptive alarm is being run.
    def _start_preemptive_alarm(self):
        # This loop ensures that the function is never exited, and thus just iterates for all eternity.
        while 1:
            # The timer_limit is the upper boundary for how long the user can be away from the stove. As can be seen,
            # the timer is 18 seconds times 60 seconds, thus 18 minutes.
            timer_limit = 18 * 1
            # int(time.time()) gets the current time and converts it to an int. This number is then saved in the current
            # time variable. The current_time variable is used as a baseline, for when the preemptive alarm was started.
            current_time = int(time.time())
            # A counter variable is assigned the value of the timer limit. The counter is used to make countdowns
            # in a terminal, but also to ensure that if the preemptive alarm has been started and the user returns to
            # the kitchen, then the absence time is reported to the database.
            counter = timer_limit
            # The while-loop ensures that IF the state of the alarmThread is "ON", then the preemptive alarm starts. If
            # it is not "ON", the while-loop is skipped and the function is iterated.
            while self.alarmThreadState == State.ON:
                # When the state is "ON", the counter variable is decremented by 1.
                counter = counter - 1
                # The loop then sleeps for a second.
                time.sleep(1)
                # Prints the current counter to the terminal of the Pi application.
                print(f"Turning on light in {counter}.")
                # If the time after iteration of the while-loop is greater than or equal to the baseline time, i.e the
                # time when the preemptive alarm started plus the limit, then the actual alarm starts.
                if int(time.time() >= current_time + timer_limit):
                    # Starting alarm is printed to terminal.
                    print("Starting alarm!")
                    # The LEDs are turned "ON" in all rooms, if the user is not in the house, and only in the room the
                    # user is in, if the user is at home.
                    self._turn_on_led()
                    # Afterwards, the actual alarm is started.
                    self._start_alarm()
                    # The counter is reset
                    counter = timer_limit
                    # And the while-loop breaks.
                    break
            # If the counter has been decremented, i.e the preemptive alarm has been started...
            if counter != timer_limit:
                # The time of absence is printed to the console
                print(f"Absence time: {time.time() - current_time + counter + time_to_false}")
                # A Z2mMsg MQTT with the absence time is created
                curr_z2m_msg = Z2mMsg("non", "stove_absence_event", "non",
                                      str(int(time.time()) - current_time + counter + time_to_false))
                # And forwarded to the MQTT client with with "kg" topic. This ensures that all absence timers are
                # forwarded to the database.
                self.myClient.publish_msg("kg", curr_z2m_msg)

    # This is the function that starts AFTER the preemptive alarm has passed, i.e it starts after 18 minutes has passed.
    def _start_alarm(self):
        # In this the timer_limit is set to 2 * 60 seconds, i.e 2 minutes. The reason being that the stove should be
        # turned off in 20 minutes, i.e 18 + 2.
        timer_limit = 2 * 1
        # The time when starting the alarm is stored in a variable called current_time.
        current_time = int(time.time())
        # A counter variable is then set equal to the timer limit.
        counter = timer_limit
        # The while-loop ensures that IF the state of the alarmThread is "ON", then the preemptive alarm starts. If
        # it is not "ON", the while-loop is skipped.
        while self.alarmThreadState == State.ON:
            # When the state is "ON", the counter variable is decremented by 1.
            counter = counter - 1
            # The loop then sleeps for a second.
            time.sleep(1)
            # Prints the current counter to the terminal of the Pi application.
            print(f"Turning off alarm in {counter}.")
            # If the time after iteration of the while-loop is greater than or equal to the baseline time, i.e the
            # time when the actual alarm started plus the limit, then the alarm stops.
            if int(time.time() >= current_time + timer_limit):
                # By breaking the while-loop.
                break
        # If the counter has been decremented, i.e the actual alarm was started...
        if counter != timer_limit:
            # The time of absence is printed to the console.
            print(f"Absence time: {time.time() - current_time + counter + 18 + time_to_false}")
            # A Z2mMsg MQTT with the absence time is created.
            curr_z2m_msg = Z2mMsg("non", "stove_absence_event", "non",
                                  str(int(time.time()) - current_time + counter + 18 + time_to_false))
            # And forwarded to the MQTT client with with "kg" topic. This ensures that all absence timers are
            # forwarded to the database.
            self.myClient.publish_msg("kg", curr_z2m_msg)
        print("Stopping alarm")
        # When the while-loop breaks, the alarm is stopped.
        self.stop_alarm()

    # This is the function called when the actual alarm stops. The stop function can be called in two cases:
    # 1) When the user has not entered the kitchen and 20 minutes have passed by.
    # 2) When the user enters the kitchen while the actual alarm is currently "ON", i.e the LEDs are "ON".
    def stop_alarm(self):
        # In the case that the user has not entered the kitchen, but the 20 minutes have passed, the alarmThreadState
        # is still "ON".
        if self.alarmThreadState == State.ON:
            # Thus, the stove is turned "OFF".
            self._turn_off_stove()
            # And so are the LEDs.
            self._turn_off_led()
            # Finally, the alarmThreadState is also set to "OFF", meaning the while-loop in the preemptive alarm
            # function is just iterated.
            self.alarmThreadState = State.OFF
        else:
            # If it is the case that the user has entered the kitchen, but the 20 minutes have not yet passed, the LEDs
            # just turn off, i.e the stove is still "ON".
            self._turn_off_led()

    # This function is the utility function that makes the stove turn "OFF".
    def _turn_off_stove(self):
        # It uses the get_devices function in the devices model, and asks to return a list containing all the devices
        # of the type "plug", i.e the power plug which is the abstraction for the stove.
        plug_list = self.devicesModel.get_devices("plug")
        #  Finally, the stove is turned off by publishing a set state "OFF" zigbee2mqtt message with the friendly name
        #  of the stove to the MQTT client.
        for currDevice in plug_list:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.get_friendly_name() + "/set/state", "OFF")

    # This function is the utility function that makes the LEDs turn "ON".
    def _turn_on_led(self):
        # It uses the get_devices function in the devices model, and asks to return a list containing all the devices
        # of the type "pir", i.e the motion sensor.
        pir_list = self.devicesModel.get_devices("pir")
        # The function then searches through all the PIR sensors, to see if there are people in the house, indicated by
        # a PIR sensor which has the internal state value of "True".
        for currPir in pir_list:
            # If there are people in the house,
            if currPir.get_state():
                # this is indicated by a printing to the terminal.
                print("There are people in the house!")
                # Then a list of all the LEDs is generated,
                led_list = self.devicesModel.get_devices("led")
                # which is iterated over,
                for currLed in led_list:
                    print("Turning on light at location!")
                    # and then the function matches the LED to the location in which the user(s) are. Thus, localized
                    # visual queues are implemented this way.
                    if currPir.get_location() == currLed.get_location():
                        # Finally, the LED in the room occupied by people is turned "ON", by applying the publish
                        # function defined in the client, where the topic is: zigbee2mqtt/friendly_name/set/state and
                        # the payload is "ON".
                        self.myClient.publish_msg("zigbee2mqtt/" + currLed.get_friendly_name() + "/set/state", "ON")
                        # At last, the function returns.
                        return
        # If no-one was located in the house, then all the LEDs are being turned on, by, first, making a list of all the
        # LEDs,
        led_list = self.devicesModel.get_devices("led")
        print("No people found in house... Turning ON all LEDs...")
        # then iterate over the list and apply the publish function defined in the client, where the topic is:
        # zigbee2mqtt/friendly_name/set/state and the payload is "ON".
        for currDevice in led_list:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.get_friendly_name() + "/set/state", "ON")

    # This is the utility function that turns the LEDs "OFF".
    def _turn_off_led(self):
        # It makes a list of all the LEDs in the model,
        led_list = self.devicesModel.get_devices("led")
        # And publishes an MQTT message where the topic is zigbee2mqtt/friendly_name/set/state and the payload is "OFF",
        # to all the LEDs in the model.
        for currDevice in led_list:
            self.myClient.publish_msg("zigbee2mqtt/" + currDevice.get_friendly_name() + "/set/state", "OFF")
