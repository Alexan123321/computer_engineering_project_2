from enum import Enum

# TODO: Needs commenting and cleen-up

# Enumerated state type #
class State(Enum):
    ON = "ON"
    OFF = "OFF"

#Zigbee device model
class zigbeeDevice:
    def __init__(self, inputFriendlyName:str, inputDeviceType:str, inputDeviceLocation:str, inputDeviceState:str):
        self.deviceFriendlyName = inputFriendlyName
        self.deviceType = inputDeviceType
        self.deviceLocation = inputDeviceLocation
        self.deviceState = inputDeviceState

    def getFriendlyName(self):
        return self.deviceFriendlyName

    def getType(self):
        return self.deviceType

    def getLocation(self):
        return self.deviceLocation

    def getState(self):
        return self.deviceState

class kitchenGuardModel:
    def __init__(self):
        self.modelDevices = list()

    def addDevice(self, inputDevice:zigbeeDevice):
        self.modelDevices.append(inputDevice)

    def getDevices(self, inputDeviceType:str):
        resultList = list()
        for currDevice in self.modelDevices:
            if(currDevice.deviceType == inputDeviceType):
                resultList.append(currDevice)
        return resultList

    def findDevice(self, inputTopic:str):
        for currDevice in self.modelDevices:
            if currDevice.deviceFriendlyName in inputTopic:
                return currDevice