import sys
import json
from datetime import datetime
from mysql.connector import connect as mysql_connect, errorcode as mysql_errorcode, Error as mySqlError
from paho.mqtt.client import MQTTMessage as mqtMsg
from kitchen_guard_master_mqtt_client import Z2MMsg

# TODO: Denne klasse skal ændres til HEUCOD event.
# Generelt, så kender alt udenfor klienten på master-side ikke til Z2MMsgs


class KitchenGuardMasterModel:
    def __init__(self, host: str, database_name: str, user: str, password: str):
        self.host = host
        self.dbName = database_name
        self.dbUser = user
        self.dbPass = password
        self.sqlConnection = None

    def start(self):
        try:
            self.sqlConnection = mysql_connect(host=self.host, user=self.dbUser, password=self.dbPass)

            self.sqlConnection.cursor().execute(f"USE {self.dbName}")

        except mySqlError as err:
            print(f"Database error encountered: {err}. Exiting...")
            sys.exit()

    def stop(self):
        self.sqlConnection.close()
        self.sqlConnection = None

    def store(self, event: Z2MMsg):
        if not self.sqlConnection:
            print("Database connection not found. Exiting...")
            #sys.exit()
            return -1
        print("Storing new event in database")
        sql_query = (
            f"INSERT INTO kg_service (device_id,device_type,measurement,timestamp)"  # HER HAR DU ÆNDRET DATABASENS TABELNAVN
            f"VALUES(%s, %s, %s, %s);")
        sql_cursor = self.sqlConnection.cursor()
        sql_cursor.execute(sql_query, (event.deviceFriendlyName, event.deviceType, event.deviceState,
                                       event.timestamp))  # HER BØR DU ÆNDRE DE VARIABLE, DER SKAL INDSÆTTES I TABELLEN
        self.sqlConnection.commit()
        sql_cursor.close()
        return 0


