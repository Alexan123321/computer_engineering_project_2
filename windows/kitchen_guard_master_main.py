from time import sleep

from kitchen_guard_master_controller import KitchenGuardMasterController, State
from kitchen_guard_master_model import KitchenGuardMasterModel

dbHost = "localhost"
dbName = "kg_data"
dbUser = "root"
dbPass = "root"

mqttHost = "192.168.87.104"
mqttPort = 1883


def main():
    model = KitchenGuardMasterModel(dbHost, dbName, dbUser, dbPass)
    model.start()

    controller = KitchenGuardMasterController(model)
    controller.start(mqttPort, mqttHost)

    while controller.kitchen_guard_state == State.ON:
        sleep(1)


if __name__ == "__main__":
    main()