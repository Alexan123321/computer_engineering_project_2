#
# TODO: Needs commenting
from kitchen_guard_controller import kitchenGuardController, State
from time import sleep

host = "127.0.0.1"
port = 1883

def main():
    controller = kitchenGuardController()
    controller.start(port, host)
    
    while controller.kitchenGuardState == ON:
        sleep(1)
    
if __name__== "__main__" :
    main()