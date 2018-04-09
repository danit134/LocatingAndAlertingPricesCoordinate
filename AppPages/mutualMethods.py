#!/usr/bin/env python
# -*- coding: utf-8 -*-
from warehouseCommunication import *

class mutualMethods:
    def __init__(self):
        self.__whCommunication = whCommunication()
        self.__branchesAndChainsInCity = self.__getBranchesAndChainsInCity()
        self.__sortedProductsNames = []
        self.__productsByNames = self.__getAllProductsQuery() #key-product name, value- barcode
        self.__productsByBarcode = dict((v, k) for k, v in self.__productsByNames.iteritems()) #key-barcode, value- product name


    #get the list of all products in the warehouse
    def __getAllProductsQuery(self):
        likeParm = u'%[אבגדהוזחטיכלמנסעפצקרשת]%' #define the order of the alpha-beit hebrew so we can sort the products names
        parameters = [likeParm]
        query = "select barcode, productName from dimProduct order by case when productName like ? then productName end collate Hebrew_CI_AS"
        df = self.__whCommunication.executeQuery(query, parameters)
        allProducts = {}
        for index, row in df.iterrows():
            productName = row['productname'].decode('cp1255', 'strict')
            allProducts[productName] = row['barcode']
            self.__sortedProductsNames.append(productName)
        return allProducts

    def getAllProductsNames(self):
        return self.__sortedProductsNames

    def getBarcode(self, productName):
        return (self.__productsByNames[productName])

    def getProductName(self, barcode):
        return (self.__productsByBarcode[barcode])

    def productExist(self, productName):
        if (productName in self.__productsByNames.keys()):
            return True
        else:
            return False

    def __getBranchesAndChainsInCity(self):
        branchesAndChainsInCity = {}
        query = "select cityName, chainName, branchName from dimBranch"
        df = self.__whCommunication.executeQuery(query, [])
        for index, row in df.iterrows():
            cityName = (row['cityname']).decode('cp1255', 'strict')
            chainName = (row['chainname']).decode('cp1255', 'strict')
            branchName = (row['branchname']).decode('cp1255', 'strict')
            if (cityName not in branchesAndChainsInCity):
                branchesAndChainsInCity[cityName] = {}
            if (chainName not in branchesAndChainsInCity[cityName]):
                branchesAndChainsInCity[cityName][chainName] = []
                branchesAndChainsInCity[cityName][chainName].append(branchName)
            else:
                branchesAndChainsInCity[cityName][chainName].append(branchName)
        return branchesAndChainsInCity

    def getAllBrunchNamesInchain(self, city, chain):
        return (self.__branchesAndChainsInCity[city][chain])

    def getAllChainsInCity(self, city):
        return list(self.__branchesAndChainsInCity[city].keys())

    def getAllBranchesAndChainsInCity (self, city):
        return (self.__branchesAndChainsInCity[city])

    def getAllCities(self):
        return list(self.__branchesAndChainsInCity.keys())

    def getAllAreasInCity (self, city):
        parameters = [city]
        query = "SELECT areaName FROM dimArea WHERE cityName=?"
        df = self.__whCommunication.executeQuery(query, parameters)
        areaList = []
        for index, row in df.iterrows():
            areaList.append(row['areaname'].decode('cp1255', 'strict'))
        return areaList

    def getAllBranchesInArea(self,city ,areaName):
        parameters = [city, areaName]
        query = "SELECT chainName, branchName FROM dimBranch WHERE cityName=? AND areaName=?"
        df = self.__whCommunication.executeQuery(query, parameters)
        return df

    def cityExist(self, city):
        if (city in self.__branchesAndChainsInCity):
            return True
        else:
            return False

    def chainExist(self, city, chain):
        if (chain in self.__branchesAndChainsInCity[city]):
            return True
        else:
            return False

    def branchExist(self, city, chain, branch):
        if (branch in self.__branchesAndChainsInCity[city][chain]):
            return True
        else:
            return False

