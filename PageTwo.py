#!/usr/bin/env python
# -*- coding: utf-8 -*-

from warehouseCommunication import *

class buildPageTwo:
    def __init__(self):
        self.__whCommunication = whCommunication()
        self.__branchesInChains = self.__getBranchesInChains()

    def __getBranchesInChains(self):
        branchesAndChains = {}
        query = "select chainName, branchName, codeMarket from dimBranch"
        df = self.__whCommunication.executeQuery(query, [])
        for index, row in df.iterrows():
            if ((row['chainname'].decode('cp1255','strict')) not in branchesAndChains):
                branchesAndChains[(row['chainname']).decode('cp1255','strict')] = {}
            branchesAndChains[(row['chainname']).decode('cp1255', 'strict')][((row['branchname']).decode('cp1255', 'strict'))] = row['codemarket']
        return branchesAndChains

    #The algorithm will get codeMarkets- more easy to manage then two strings (brunchName, chainName)
    def getMarketCodeOfBrunch(self, chain, brunch):
        return (self.__branchesInChains[chain][brunch])

    def getAllBrunchNamesInchain(self, chain):
        return (self.__branchesInChains[chain].keys())

    def getAllChains(self):
        return list(self.__branchesInChains.keys())

    #run kendel/pearson here
    def findPriceCoordinate(self, chain1, brunch1, chain2, brunch2, startDate, endDate):
        return