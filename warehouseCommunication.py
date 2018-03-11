import pypyodbc
import pandas as pd

class whCommunication:
    def __init__(self):
        self.__driver = "{SQL Server Native Client 11.0}"
        self.__server = "DESKTOP-BDO2MF0"
        self.__database = "pricingProductsDW"
        self.__userName = "sa"
        self.__password = "danIN134"

    def __connectWH(self):
        self.connection = pypyodbc.connect(driver=self.__driver, server=self.__server, database=self.__database, uid=self.__userName, pwd=self.__password)

    def __disconnectWH(self):
        self.connection.close()

    #convert query results to dataframe
    def __as_pandas(self, cursor):
        names = [metadata[0] for metadata in cursor.description]
        return pd.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)

    def executeQuery (self, query, parameters):
        self.__connectWH()
        cursor = self.connection.cursor()
        cursor.execute(query, parameters)
        df = self.__as_pandas(cursor)
        cursor.close()
        self.__disconnectWH()
        return df

