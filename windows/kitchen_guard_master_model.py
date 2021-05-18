import sys  #exit
from heucod import HeucodEvent  #used to store events that make a bit more sense in the eyes of the user
from mysql.connector import connect as mysql_connect, Error as mySqlError   #mysql connection, disconnection, sql_query and cursor
import datetime #used to make timestamp the right format

class KitchenGuardMasterModel:
    def __init__(self, host: str, database_name: str, user: str, password: str):
        self.host = host       
        #host is the ip address of the web page 
        self.dbName = database_name
        #database_name is kg_data
        self.dbUser = user
        #username is root
        self.dbPass = password
        #password is root
        self.sqlConnection = None
        #no connection has been established to the database yet

    def start(self):
        try:
            self.sqlConnection = mysql_connect(host=self.host, user=self.dbUser, password=self.dbPass)
            #establish connection with mysql database

            self.sqlConnection.cursor().execute(f"USE {self.dbName}")
            #integrate cursor mechanincs
            print("Connected to database successfully")

        except mySqlError as err:
            print(f"Database error encountered: {err}. Exiting...") 
            sys.exit()
        #print what error has occured and that connection cannot get established

    def stop(self):
        self.sqlConnection.close()
        self.sqlConnection = None
        #close connection

    def store(self, event: HeucodEvent): 
        if not self.sqlConnection:
            #if there is no connection to the database then data cannot be stored
            print("Database connection not found. Exiting...")
            return -1
        #otherwise then store the event on the database
        print("Storing new event in database...")
        sql_query = (
            f"INSERT INTO kg_table (timestamp,value,event_type,event_type_enum,device_model,device_vendor)"
            f"VALUES(%s, %s, %s, %s, %s, %s);")
            #insert the values into the kg_table in the kg database
        sql_cursor = self.sqlConnection.cursor()
        #make a cursor for the sql connection
        sql_cursor.execute(sql_query, (datetime.datetime.fromtimestamp(event.timestamp), event.value, event.event_type, event.event_type_enum, event.device_model, event.device_vendor))
        #execute a query with the data that is to be stored
        self.sqlConnection.commit()
        #commit changes 
        sql_cursor.close()
        #close cursor connection
        return 0


