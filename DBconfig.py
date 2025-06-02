from logging import exception

import psycopg2
import json

from PyQt6.QtSql import QSqlDatabase, QSqlQueryModel




class DBConfig:
    __instance = None

    @classmethod
    def getInstance(cls):
        return cls.__instance

    def __init__(self):
        self.hostname = ''
        self.port = 5432
        self.database = ''
        self.username = ''
        self.password = ''
        self.conn = None


    def __str__(self):
        return f"Host={self.hostname};Port={self.port};Database={self.database}; Username={self.username};Password={self.password};Persist Security Info=True;"

    @classmethod
    def LoadDbFromConfig (cls, config_path):
        newdb = cls.GetDbFromConfig(config_path)
        if newdb is not None:
            try:
                newdb.CheckDbConnection()
                newdb.setDbConfig()
            except Exception as ex:
                newdb.conn and newdb.conn.close()
                raise ex

    @staticmethod
    def GetDbFromConfig(config_path):
        try:
            with open(f"{config_path}", "r", encoding="utf-8") as f:
                data = json.load(f)
            database_str = data["ConnectionStrings"]["PostgreSQL"]

            parts = database_str.split(';')

            result = {}
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if '=' in part:
                    key, value = part.split('=', 1)
                    result[key.strip()] = value.strip()


            newinstance = DBConfig()
            if result["Host"]:
                newinstance.hostname = result["Host"]
            else:
                return None

            if result["Database"]:
                newinstance.database = result["Database"]
            else:
                return None

            if result["Port"]:
                newinstance.port = int(result["Port"])
            else:
                return None

            if result["Username"]:
                newinstance.username = result["Username"]
            else:
                return None

            if result["Password"]:
                newinstance.password = result["Password"]
            else:
                return None

            return newinstance

        except Exception as ex:

            return None

    def SaveDb(self,config_path):
        self.CheckDbConnection()
        self.SaveDbToConfig(config_path)
        self.setDbConfig()

    def SaveDbToConfig(self, config_path):
        data = None
        try:
            with open(f"{config_path}", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as ex:
            print(f"Cannot open old config file, it will be created a new one \n Error: {ex}")

        finally:
            if data is None:
                data = {
                    "ConnectionStrings": {
                        "PostgreSQL": ""
                    }
                }
            data["ConnectionStrings"]["PostgreSQL"] = self.__str__()
            with open(f"{config_path}", "w", encoding="utf-8") as f:
                json.dump(data, f)


    def setDbConfig(self):
        current_instance = self.__class__.__instance
        if current_instance is not None:
            current_instance.conn and current_instance.conn.close()
        self.__class__.__instance = self


    def CheckDbConnection(self):
        self.conn = psycopg2.connect(host=self.hostname, port=self.port, dbname=self.database, user=self.username,
                                      password=self.password)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM airlines")
            cursor.execute("SELECT * FROM airports")
            cursor.execute("SELECT * FROM countries")
            cursor.execute("SELECT * FROM planes")
            cursor.execute("SELECT * FROM routes")
        finally:
            cursor.close()

    def GetQueryResult (self, query):
        cursor = self.conn.cursor()
        try:

            cursor.execute(query)
            result = cursor.fetchall()
            return result

        finally:
            cursor.close()

    def close(self):
        self.conn.close()