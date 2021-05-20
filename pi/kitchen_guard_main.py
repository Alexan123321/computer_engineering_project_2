from kitchen_guard_controller import KitchenGuardController, State
from kitchen_guard_model import KitchenGuardModel, ZigbeeDevice
from time import sleep
import threading
import sys

host = "127.0.0.1"
port = 1883


def stop(input_controller: KitchenGuardController):
    input_data = input("Press e to exit: ")
    if input_data == "e":
        input_controller.stop()


def main():
    # Creating zigBee device abstractions #
    # Office devices #
    officePIR = ZigbeeDevice("0x00158d00057acc4b", "pir", "office", "False")
    officeLED = ZigbeeDevice("0x60a423fffe023455", "led", "office", "False")
    
    # Bedroom devices #
    bedroomPIR = ZigbeeDevice("0x00158d00057b28e3", "pir", "bedroom", "False")
    bedroomLED = ZigbeeDevice("0x842e14fffe9e2d85", "led", "bedroom", "False")
    
    # Bathroom devices #
    bathroomPIR = ZigbeeDevice("0x00158d0005727f3a", "pir", "bathroom", "False")
    bathroomLED = ZigbeeDevice("0xbc33acfffe8b8e62", "led", "bathroom", "False")
    
    # Living room devices # 
    livingroomPIR = ZigbeeDevice("0x00158d0005729f18", "pir", "livingroom", "False")
    livingroomLED = ZigbeeDevice("0xbc33acfffe8b8e71", "led", "livingroom", "False")
    
    # Kitchen devices #
    kitchenPIR = ZigbeeDevice("0x00158d000572a346", "pir", "kitchen", "False")
    kitchenPLUG = ZigbeeDevice("0xccccccfffee3df19", "plug", "kitchen", "False")
    
    # Adding these abstractions to the model #
    model = KitchenGuardModel()
    model.add_device(officePIR)
    model.add_device(officeLED)
    
    model.add_device(bedroomPIR)
    model.add_device(bedroomLED)
    
    model.add_device(bathroomPIR)
    model.add_device(bathroomLED)
    
    model.add_device(livingroomPIR)
    model.add_device(livingroomLED)
    
    model.add_device(kitchenPIR)
    model.add_device(kitchenPLUG)

    # Creating a the KitchenGuardController #
    controller = KitchenGuardController(model, port, host)
    controller.start()
    user_input_thread = threading.Thread(target=stop(controller))
    user_input_thread.start()
    
    # Run it until it, as long as its internal state is ON #
    while controller.kitchenGuardState == State.ON:
        sleep(1)

    print("Exiting Kitchen Guard...")
    
    user_input_thread.join()


# Driver function #
if __name__ == "__main__":
    main()
