from time import sleep    

from kitchen_guard_master_controller import KitchenGuardMasterController, State
from kitchen_guard_master_model import KitchenGuardMasterModel

dbHost = "localhost"            
#database host is on localhost
dbName = "kg_data"              
#database name
dbUser = "root"                 
#username
dbPass = "root"                 
#password

mqttHost = "192.168.110.94"
#connect to pi ip address
mqttPort = 1883                     
#using TCP (MQTT) port 1883 to communicate over                  

def main():
    model = KitchenGuardMasterModel(dbHost, dbName, dbUser, dbPass)
    model.start()                                   
    #start connecting to database

    controller = KitchenGuardMasterController(model)
    controller.start(mqttPort, mqttHost)            
    #start controller where we listen for pi to publish events
    while controller.kitchen_guard_state == State.ON:
        sleep(1)                                    
        #sleep for 1 second while the kitchen_guard_state is on


if __name__ == "__main__":
    main()