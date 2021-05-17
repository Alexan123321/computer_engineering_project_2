from kitchen_guard_controller import KitchenGuardController, State
from kitchen_guard_model import KitchenGuardModel, ZigbeeDevice
from time import sleep
import threading

host = "127.0.0.1"
port = 1883


def stop(input_controller: KitchenGuardController):
    input_data = input("Press e to exit: ")
    if input_data == "e":
        input_controller.stop()


def main():
    # Creating zigBee device abstractions #
    pir = ZigbeeDevice("0x00158d0005727f3a", "pir", "kitchen", "False")
    led = ZigbeeDevice("0xbc33acfffe8b8ea8", "led", "office", "OFF")
    plug = ZigbeeDevice("0xccccccfffee3d7aa", "plug", "kitchen", "OFF")

    # Adding these abstractions to the model #
    model = KitchenGuardModel()
    model.add_device(pir)
    model.add_device(led)
    model.add_device(plug)

    # Creating a the KitchenGuardController #
    controller = KitchenGuardController(model, port, host)
    controller.start()
    user_input_thread = threading.Thread(target=stop(controller))
    user_input_thread.start()
    
    # Run it until it, as long as its internal state is ON #
    while controller.kitchenGuardState == State.ON:
        sleep(1)

    user_input_thread.join()

    print("Exiting Kitchen Guard...")


# Driver function #
if __name__ == "__main__":
    main()
