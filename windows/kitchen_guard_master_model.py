import sys
from heucod import HeucodEvent
from mysql.connector import connect as mysql_connect, Error as mySqlError
import datetime

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
            print("Connected to database successfully")

        except mySqlError as err:
            print(f"Database error encountered: {err}. Exiting...")
            sys.exit()

    def stop(self):
        self.sqlConnection.close()
        self.sqlConnection = None

    def store(self, event: HeucodEvent):
        if not self.sqlConnection:
            print("Database connection not found. Exiting...")
            #sys.exit()
            return -1
        print("Storing new event in database...")
        sql_query = (
            f"INSERT INTO kg_table (timestamp,value,event_type,event_type_enum,device_model,device_vendor)"
            f"VALUES(%s, %s, %s, %s, %s, %s);")
        sql_cursor = self.sqlConnection.cursor()
        sql_cursor.execute(sql_query, (datetime.datetime.fromtimestamp(event.timestamp), event.value, event.event_type, event.event_type_enum, event.device_model, event.device_vendor))
        self.sqlConnection.commit()
        sql_cursor.close()
        return 0


