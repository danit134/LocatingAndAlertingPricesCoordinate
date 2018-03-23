#!/usr/bin/env python
# -*- coding: utf-8 -*-
from warehouseCommunication import *

class mutualMethods:
    def __init__(self):
        self.__whCommunication = whCommunication()
        self.__branchesAndChainsInCity = self.__getBranchesAndChainsInCity()
        self.__productsByBarcode = self.__getAllProductsQuery() #key-barcode, value- product name
        self.__productsByNames = dict((v, k) for k, v in self.__productsByBarcode.iteritems())

    #get the list of all produsts in the warehouse
    def __getAllProductsQuery(self):
        query = "select barcode, productName from dimProduct"
        df = self.__whCommunication.executeQuery(query, [])
        allProducts = {}
        for index, row in df.iterrows():
            allProducts[row['barcode']] = row['productname'].decode('cp1255', 'strict')
        return allProducts

    def getAllProductsNames(self):
        return self.__productsByNames.keys()

    def getBarcode(self, productName):
        return (self.__productsByNames[productName])

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

    def getAllCities(self):
        return list(self.__branchesAndChainsInCity.keys())

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

