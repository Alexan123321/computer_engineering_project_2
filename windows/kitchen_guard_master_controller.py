from enum import Enum
from heucod import HeucodEvent
from kitchen_guard_master_model import KitchenGuardMasterModel
from kitchen_guard_master_mqtt_client import KitchenGuardMasterMqttClient


class State(Enum):
    ON = "ON"
    OFF = "OFF"


class KitchenGuardMasterController:
    kitchen_guard_state: State
    port: str
    host: str

    mqttClient: KitchenGuardMasterMqttClient
    databaseModel: KitchenGuardMasterModel

    def __init__(self, model: KitchenGuardMasterModel):
        self.kitchen_guard_state = State.ON
        self.databaseModel = model

    def start(self, port: int, host: str):
        self.port = port
        self.host = host
        self.mqttClient = KitchenGuardMasterMqttClient(self.host, self.port, on_message_clbk=self.ctl_on_message)
        self.mqttClient.start()

    def stop(self):
        self.kitchen_guard_state = State.OFF
        self.mqttClient.stop()

    def ctl_on_message(self, event: HeucodEvent):
        print("Controller event received!")
        res = self.databaseModel.store(event)
        if res == -1:
            self.stop()