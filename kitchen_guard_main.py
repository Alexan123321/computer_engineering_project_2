#
# TODO: Needs commenting and cleanup
from kitchen_guard_controller import kitchenGuardController, State
from kitchen_guard_model import kitchenGuardModel, zigbeeDevice
from time import sleep

host = "127.0.0.1"
port = 1883

def main():
    # Creating zigBee device abstractions #
    pir = zigbeeDevice("0x00158d0005727f3a", "pir", "kitchen", "False")
    plug = zigbeeDevice("0xccccccfffee3d7aa", "plug", "kitchen", "OFF")
    led = zigbeeDevice("0xbc33acfffe8b8ea8", "led", "office", "OFF")

    # Adding these abstractions to the model #
    model = kitchenGuardModel()
    model.addDevice(pir)
    model.addDevice(plug)
    model.addDevice(led)

    # Creating a the kitchenGuardController #
    controller = kitchenGuardController(model)
    controller.start(port, host)
    
    # Run it until it, as long as its internal state is ON #
    while controller.kitchenGuardState == State.ON:
        sleep(1)

# Driver function #
if __name__== "__main__" :
    main()