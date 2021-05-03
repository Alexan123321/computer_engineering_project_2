#
# TODO: Needs to be integrated into main, controller and client.
# TODO: Needs commenting
#Zigbee device model
class zigbeeDevice:
    def __init__(self, inputFriendlyName:str, inputDeviceType:str, inputDeviceState:str, inputDeviceLocation:str):
        self.deviceFriendlyName = inputFriendlyName
        self.deviceType = inputDeviceType
        self.deviceLocation = inputDeviceLocation

class kitchenGuardModel:
    self.modelDevices = list()

    def __init__(self):
        pass

    def addDevice(self, inputDevice:zigbee):
        modelDevices.append(inputDevice)

    def getDevices(self, inputDeviceType:str) -> List[zigbee]:
        resultList = list()
        for currDevice in self.modelDevices:
            if(currDevice.Type == inputDeviceType):
                resultList.append(currDevice)
        return resultList