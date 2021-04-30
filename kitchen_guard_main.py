from kitchen_guard_controller import kitchenGuardController
from time import sleep

def main():
    controller = kitchenGuardController()
    controller.myClient.start()
    
    while True:
        sleep(1)
    
if __name__== "__main__" :
    main()