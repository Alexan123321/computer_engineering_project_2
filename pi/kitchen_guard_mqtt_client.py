# The model, implemented in the kitchen_guard_model.py, is imported. The model is a software abstraction of the
# physical environment. The idea here is to implement the model-view-controller pattern, but without a view, as the app-
# lication being run on the Pi does not need a presentation layer. The model contains information about all the physical
# devices, however, the states in the model are maintained by the MQTT client, thus implemented here.
from kitchen_guard_model import KitchenGuardModel
# Heucod is an event standard used in this client to convert Z2mMsgs to Heucod events, so that ANY database model may
# be connected to this backend application, and still work.
from heucod import HeucodEvent, HeucodEventType
# From the paho library is imported both the MQTT client.
from paho.mqtt.client import Client as mqttClient
# And the MQT message.
from paho.mqtt.client import MQTTMessage as mqtMsg

# Callable returns true, if the object given as argument is callable. This is used for the __on_message function.
# Optional is an argument with a default value. It basically means that if a value is not specified for this argument,
# the default value will be used. This is also used in the __on_message function.

from typing import Callable, Optional
# The json library is used for json en- and decoding.
import json
# From the datetime library, datetime and timezone is imported. These are used in the heucodify function to generate
# timestamps.
from datetime import datetime, timezone             # importing datetime and timezone


# The Z2mMsg is the internal datatype used on the Pi to convert MQTT messages
# into a less extensive format. As they are both included from the kitchen_guard_mqtt_client.py, the reader is urged to
# visit this file to obtain an elaborate understanding.

# The Z2mMsg is the data type used throughout the application running on the Pi. It is used to convert MQTT messages to
# a less extensive format with only four string parameters, which are also the input parameters of the initializer:
# 1) The friendly name of the device publishing the event
# 2) The type of the device publishing the event
# 3) The location of the device publishing the event
# 4) The state of the device
class Z2mMsg:
    def __init__(self, input_device_friendly_name: str, input_device_type: str, input_device_location: str,
                 input_device_state: str):
        self.deviceFriendlyName = input_device_friendly_name
        self.deviceType = input_device_type
        self.deviceLocation = input_device_location
        self.deviceState = input_device_state


# The KitchenGuardMqttClient is the class responsible for connecting the hardware, namely the Zigbee-controller, to the
# software, namely the controller and the model. Thus, this client is basically like a gateway for MQTT messages to be
# converted into the Z2mMsg format and to a Heucod event, if it needs to be forwarded to the Windows application.
class KitchenGuardMqttClient:
    # The initializer takes multiple arguments, namely:
    # 1) A host as string. This is the host upon which the MQTT-client should be instantiated, i.e localhost.
    # 2) A port as int. This is the port upon which the MQTT-client should be instantiated, i.e 1883 which is the MQTT
    # TCP port.
    # 3) A KitchenGuardModel, which is the physical abstraction of the collection of Zigbee-devices, i.e the
    # environment. The reason that needs to be included is that it is the responsibility of the MQTT client to update
    # the model.
    # 4) A function that must be called, whenever this client receives an MQTT event. In this case, it is the function
    # of the controller. The reason is that it is the responsibility of the controller to actuate logic on the Z2mMsgs
    # once converted by the client.
    def __init__(self, host: str, port: int, input_kitchen_guard_model: KitchenGuardModel,
                 on_message_clbk: Callable[[Optional[Z2mMsg]], None]):
        self.host = host
        self.port = port
        self.__client = mqttClient()
        # Here the functions of the MQTT client are defined. For example, when the on_connect function of the client is
        # called, it is "redirected" to the __on_connect function defined a bit later. Same goes for the on_disconnect,
        # the on_message and the callback functions.
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.__on_message_clbk = on_message_clbk
        # Upon initialization the connection variable is set to "False"
        self.connection_established = False
        # And the model is saved in the MQTT client. Again, the reason is that it is the responsibility of the client to
        # update the model.
        self.devicesModel = input_kitchen_guard_model

    # When the MQTT client connects, this function is called.
    def __on_connect(self, client, userdata, flags, rc):
        # Which prints a status code to the terminal,
        print("Connected with result code " + str(rc))
        # and updates its connection variable to "True"
        self.connection_established = True

    # When the MQTT client disconnects, this function is called.
    def __on_disconnect(self, client, userdata, flags):
        # Which prints the status code to the terminal,
        print("MQTT Client disconnected")
        # and updates the connection variable to "False"
        self.connection_established = False

    # The start function is the one called, once the MQTT client is sought started.
    def start(self):
        # If the client is already active, it does nothing.
        if self.connection_established:
            return
        # But, if it is not already active, it establishes a connection on the host and port.
        self.__client.connect(self.host, self.port)
        # And begins to listen for events being published by the Zigbee-controller. This is performed on a dedicated
        # thread, which is started here.
        self.__client.loop_start()
        # Then, the MQTT client subscribes to the power plug, all PIRs and all LEDs defined upon instantiation of the
        # model. This is done by make a list of each device, via. the get_devices("TYPE") call, where "TYPE" can be
        # either "plug", "pir" or "led".
        plug_list = self.devicesModel.get_devices("plug")
        # Then the MQTT client iterates over this list,
        for currDevice in plug_list:
            # and subscribes to all devices in this.
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.get_friendly_name()))
        # This is then iterated for all PIRs and LEDs too.
        pir_list = self.devicesModel.get_devices("pir")
        for currDevice in pir_list:
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.get_friendly_name()))
        led_list = self.devicesModel.get_devices("led")
        for currDevice in led_list:
            self.__client.subscribe("zigbee2mqtt/" + (currDevice.get_friendly_name()))

    # The stop function is the one to be called, when the MQTT client is sought brought to a halt.
    def stop(self):
        # if the client is already inactive, the function does not do anything.
        if not self.connection_established:
            return
        # Otherwise it stops the thread listening for messages,
        self.__client.loop_stop()
        # and unsubscribes to the power plug.
        plug_list = self.devicesModel.get_devices("plug")
        for currDevice in plug_list:
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.get_friendly_name())
        # Then a sublist of all pir sensors is computed then computed,
        pir_list = self.devicesModel.get_devices("pir")
        # and, the client unsubscribes to all the PIR sensors in the model. This process is then iterated for all the
        # PIRs and all the LEDs.
        for currDevice in pir_list:
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.get_friendly_name())
        led_list = self.devicesModel.get_devices("led")
        for currDevice in led_list:
            self.__client.unsubscribe("zigbee2mqtt/" + currDevice.get_friendly_name())
            # Finally, the client disconnects.
        self.__client.disconnect()
    
    # The __on_message function is the one to be called, whenever a Zigbee message is received and converted by the
    # zigbee2mqtt-client.
    def __on_message(self, client, userdata, msg):
        # If the message is published by a device known by the model,
        if self.devicesModel.find_device(msg.topic):
            # then it is parsed into a Z2mMsg format,
            curr_z2m_msg = self.__parse(msg)
            # and the callback function from the controller is called upon the Z2mMsg.
            self.__on_message_clbk(curr_z2m_msg)
        # If the message is not published by a device known by the model, then the function does nothing.
        else:
            pass

    # The parse function is the one converting MQTT messages to Z2mMsgs. Thus, it takes MQTT message as an input argu-
    # ment and returns a Z2mMsg.
    def __parse(self, msg: mqtMsg):
        # First, the parse function decodes the payload into a utf-8 format.
        payload = msg.payload.decode("utf-8")
        # Then, it loads the payload into a dictionary that can be accessed as per a key-value principle.
        payload = json.loads(payload)
        # Then the MQTT client updates the device in the model from the which the message originates. It does so by
        # locating the device via. the friendly name in the topic of the message.
        curr_device = self.devicesModel.find_device(msg.topic)
        # If this device is a pir sensor, then the state is loaded via. the "occupancy" key.
        if curr_device.get_type() == "pir":
            curr_device.deviceState = payload["occupancy"]
        # If it is an LED or the power plug, then the state is loaded via. the "state" key.
        else:
            curr_device.deviceState = payload["state"]
        # Finally, a new Z2mMsg is returned with the friendly name of the device that sent an event. The type of this
        # device. The location of this device and, lastly, the state of this, as input arguments.
        return Z2mMsg(curr_device.get_friendly_name(), curr_device.get_type(), curr_device.get_location(),
                      curr_device.get_state())

    # Whenever an MQTT message needs to be publishes, this utility function is used. It takes a topic as a string and
    # a payload as a Z2mMsg as arguments.
    def publish_msg(self, topic: str, payload: Z2mMsg):
        # The function then differentiates between the topic being directed to the hardware devices or to the Windows
        # application. If the message is meant for the Windows application, the topic is "kg".
        if topic == "kg":
            # And thus the payload must conform to the Heucod standard. This is done by calling the "Heucodify" method
            # on the payload which returns a Heucod event.
            payload = self.heucodify(payload)
        # If the topic is not that of "kg", the payload is simply forwarded to the devices.
        self.__client.publish(topic, f"{payload}")                                #and then publishes this topic with this state

    # The heucodify method is used to convert Z2mMsgs to the Heucod event format. Therefore, it takes a Z2mMsg as argu-
    # ment and returns a Heucod event.
    @staticmethod
    def heucodify(payload: Z2mMsg):
        # First, the function creates a new Heucod event.
        curr_event = HeucodEvent()
        # If the Z2mMsg comes from a stove device, then the following modifications are made to the event.
        if payload.deviceType == "plug":
            # The Heucod event type is set to the "DeviceUsageEvent"
            curr_event.event_type = HeucodEventType.DeviceUsageEvent
            # Then, the enumerated type of the Heucod event is set to that the integer representation of the DeviceUsage
            # Event.
            curr_event.event_type_enum = int(HeucodEventType.DeviceUsageEvent)
            # Then, the Heucod event timestamp of the Heucod event is set to the moment it is declared, i.e now.
            curr_event.timestamp = datetime.now(tz=timezone.utc)
            # The Heucod event value of the Heucod event is set to the state of the device.
            curr_event.value = payload.deviceState
            # The Heucod event device vendor is set to Immax
            curr_event.device_vendor = "Immax"
            # The Heucod event model is then set
            curr_event.device_model = "07048L"
        # If the Z2mMsg, however, is a stove_absence_event instead, then another Heucod event is sent.
        elif payload.deviceType == "stove_absence_event":
            # In this, the event type is set to the "LowActivityWarning", as it is considered low activity from the user
            curr_event.event_type = HeucodEventType.LowActivityWarning
            # Then, the enumerated type of the Heucod event is set to that the integer representation of the
            # LowActivityWarning
            curr_event.event_type_enum = int(HeucodEventType.LowActivityWarning)
            # Then, the Heucod event timestamp of the Heucod event is set to the moment it is declared, i.e now.
            curr_event.timestamp = datetime.now(tz=timezone.utc)
            # The Heucod event value of the Heucod event is set to the time of absence, stored in the deviceState.
            curr_event.value = payload.deviceState
            # The Heucod event device vendor is set to non.
            curr_event.device_vendor = "non"
            # And so is the device model.
            curr_event.device_model = "non"
        # Finally, the Heucod event is returned.
        return curr_event.to_json()
