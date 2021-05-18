# The ZigbeeDevice class is the abstraction of the physical sensors and actuators, namely the LEDs, the PIRs and the
# power plug / stove. It is used to store information about each device and is located in the model containing multiple
# devices.
class ZigbeeDevice:
    # The init function is the initializer of the ZigbeeDevice class. As can be seen, it takes four string arguments:
    # 1) A friendly name which is the Zigbee identifier of each devices.
    # 2) A device type, which can be one of the three hardware sensors / actuators of the system, i.e "pir", "plug" or
    # "led".
    # 3) A location which is the room of the house.
    # 4) Finally a device state which can be "ON" or "OFF" for the power plug and the LEDs and "True" or "False" for the
    # PIRs.
    def __init__(self, input_friendly_name: str, input_device_type: str, input_device_location: str,
                 input_device_state: str):
        self.deviceFriendlyName = input_friendly_name
        self.deviceType = input_device_type
        self.deviceLocation = input_device_location
        self.deviceState = input_device_state

    # Getter that returns the friendly name of the device
    def get_friendly_name(self):
        return self.deviceFriendlyName

    # Getter that returns the type of the device
    def get_type(self):
        return self.deviceType

    # Getter that returns the location of the device
    def get_location(self):
        return self.deviceLocation

    # Getter that returns the state of the device
    def get_state(self):
        return self.deviceState


# The KitchenGuardModel is the abstraction of the physical environment in which Kitchen Guard is located, thus it
# includes all the devices. The KitchenGuardModel is the model of the model-view-controller architecture that guides
# both the Windows and the Pi application.
class KitchenGuardModel:
    # The init function is the initializer of the KitchenGuardModel class.
    def __init__(self):
        # In this a list of devices is instantiated.
        self.modelDevices = list()

    # The following is the add_device function of the KitchenGuardModel. This is called once a device needs to be added
    # to the model. The way this works, is basically by appending the device to the already existing list of devices.
    # Therefore, this method takes a ZigbeeDevice as input argument.
    def add_device(self, input_device: ZigbeeDevice):
        # This ZigbeeDevice is then appended to the list of devices.
        self.modelDevices.append(input_device)

    # Getter function that takes a device type as input argument and returns a list ZigbeeDevices.
    def get_devices(self, input_device_type: str):
        # A resultant list is instantiated.
        result_list = list()
        # Then a loop iterating over all devices in the model is facilitated,
        for curr_device in self.modelDevices:
            # And if the device currently being pointed to is equal to the device(s) sought found,
            if curr_device.deviceType == input_device_type:
                # It is appended to the resultant list
                result_list.append(curr_device)
        # And finally returned
        return result_list

    # Getter function that takes a friendly name and returns the device matching to that friendly name.
    def find_device(self, input_topic: str):
        # The function starts by making a loop that iterates over all the devices,
        for curr_device in self.modelDevices:
            # and if the friendly name of the device currently being pointed is found in the input friendly name,
            if curr_device.deviceFriendlyName in input_topic:
                # it is returned.
                return curr_device
