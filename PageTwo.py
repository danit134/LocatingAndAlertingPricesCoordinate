#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from warehouseCommunication import *
import pandas as pd

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



    def __buildInputs (self, chain, branch, startDate, endDate):
        parameters = [chain, branch,str(startDate), str(endDate)]
        query = "SELECT barcode, dateKey, cost FROM PricingProductFacts WHERE chainName=? AND branchName=? AND dateKey BETWEEN ? AND ?"
        df = self.__whCommunication.executeQuery(query, parameters)
        branch_PricesForProducts = {}
        #fill the empty row
        dateCounter = startDate
        for index, row in df.iterrows():
            if(dateCounter > endDate):
                dateCounter = startDate
            if(row['datekey'] != dateCounter):
                # print (type(row['datekey']))
                # temp = pd.tslib.Timestamp(row['datekey'])
                # temp.to_pydatetime()
                # print (type(temp))
                new_row = {}
                new_row['barcode'] = row['barcode']
                new_row['datekey'] = dateCounter
                new_row['cost'] = row['cost']
                df.append(new_row)
            dateCounter += timedelta(days=1)


    #run kendel/pearson here
    def findPriceCoordinate(self, chain1, branch1, chain2, branch2, startDate, endDate):
        #function that extract the realevent data to dictionery (key- barcodes, value- arrayes of prices per each day)
        branch1_PricesForProducts = self.__buildInputs (chain1, branch1, startDate, endDate)
        branch2_PricesForProducts = self.__buildInputs (chain2, branch2, startDate, endDate)


        # if (len(branch1_PricesForProducts) > 0 and len(branch2_PricesForProducts) > 0):
        #     #pearson
        #     return