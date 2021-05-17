from enum import Enum


# Enumerated state type
class State(Enum):
    ON = "ON"
    OFF = "OFF"


# Zigbee device model
class ZigbeeDevice:
    def __init__(self, input_friendly_name: str, input_device_type: str, input_device_location: str,
                 input_device_state: str):
        self.deviceFriendlyName = input_friendly_name
        self.deviceType = input_device_type
        self.deviceLocation = input_device_location
        self.deviceState = input_device_state

    def get_friendly_name(self):
        return self.deviceFriendlyName

    def get_type(self):
        return self.deviceType

    def get_location(self):
        return self.deviceLocation

    def get_state(self):
        return self.deviceState


class KitchenGuardModel:
    def __init__(self):
        self.modelDevices = list()

    def add_device(self, input_device: ZigbeeDevice):
        self.modelDevices.append(input_device)

    def get_devices(self, input_device_type: str):
        result_list = list()
        for currDevice in self.modelDevices:
            if currDevice.deviceType == input_device_type:
                result_list.append(currDevice)
        return result_list

    def find_device(self, input_topic:str):
        for curr_device in self.modelDevices:
            if curr_device.deviceFriendlyName in input_topic:
                return curr_device
