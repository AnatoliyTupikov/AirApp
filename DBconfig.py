import psycopg2
import json

class DBConfig:

    def __init__(self):
        self.hostname = ''
        self.port = 5432
        self.database = ''
        self.username = ''
        self.password = ''



    def __str__(self):
        return f"Host={self.hostname};Port={self.port};Database={self.database}; Username={self.username};Password={self.password};Persist Security Info=True;"


    @staticmethod
    def GetDbConfigFromConfig(config_path):
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

            instance = DBConfig()
            if result["Host"]:
                instance.hostname = result["Host"]
            else:
                return None

            if result["Database"]:
                instance.database = result["Database"]
            else:
                return None

            if result["Port"]:
                instance.port = int(result["Port"])
            else:
                return None

            if result["Username"]:
                instance.username = result["Username"]
            else:
                return None

            if result["Password"]:
                instance.password = result["Password"]
            else:
                return None

            return instance

        except Exception as ex:
            return None

    @staticmethod
    def SetDbConfigToConfig(config_path, dbconfig):
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
            data["ConnectionStrings"]["PostgreSQL"] = dbconfig.__str__()
            with open(f"{config_path}", "w", encoding="utf-8") as f:
                json.dump(data, f)

    def CheckDbConnection(self):

        conn = psycopg2.connect(host=self.hostname, port=self.port, dbname=self.database,
                                user=self.username, password=self.password)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM airlines")
        cursor.execute("SELECT * FROM airports")
        cursor.execute("SELECT * FROM countries")
        cursor.execute("SELECT * FROM planes")
        cursor.execute("SELECT * FROM routes")

        cursor.close()
        conn.close()

    def GetQueryModel (self, query):
        self.CheckDbConnection()