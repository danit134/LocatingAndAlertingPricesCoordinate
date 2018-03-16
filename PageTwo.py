#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from warehouseCommunication import *
import pandas as pd
import wx
import numpy

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

    def __wxdate2pydate(self, date):
        import datetime
        assert isinstance(date, wx.DateTime)
        if date.IsValid():
            ymd = map(int, date.FormatISODate().split('-'))
            return datetime.date(*ymd)
        else:
            return None


    def __buildInputs (self, chain, branch, startDate, endDate):
        parameters = [chain, branch,str(startDate), str(endDate)]
        query = "SELECT barcode, dateKey, cost FROM PricingProductFacts WHERE chainName=? AND branchName=? AND dateKey BETWEEN ? AND ?"
        df = self.__whCommunication.executeQuery(query, parameters)
        newRowsToAdd = pd.DataFrame()
        branch_PricesForProducts = {}
        dateCounter = startDate
        # convert the columns- datekey from timestamp to type 'datetime.date'
        df['datekey'] = df['datekey'].apply(lambda x: x.date())
        countProducts = df['barcode'].value_counts() #count how many different barcodes we have (this way we discovered all products need to filled there dates)
        diff = endDate - startDate
        numOfDays = diff.days + 1
        needToFilledProducts = countProducts[countProducts < numOfDays]
        df2 = df[df['barcode'].isin(list(needToFilledProducts.keys()))]
        datelist = pd.date_range(startDate, periods=numOfDays).tolist()

        #find all the dates that missing for each incomplete product (barcode)
        for barcode in needToFilledProducts.keys():
            last_cost = -1.0
            for dateToCheck in datelist:
                dateToCheck = dateToCheck.date()
                if not (((df2['datekey'] == dateToCheck) & (df2['barcode'] == barcode)).any()):
                    if (last_cost == -1.0): #on the elsw insert the cost..
                        # last_cost = df2[df2.barcode == barcode].head(1)
                        last_cost_index = df2.barcode[df2.barcode == barcode].index.tolist()[0]
                        last_cost = df2.get_value(last_cost_index, 'cost', takeable=False) #the earliest cost of this barcode
                    new_row = pd.Series([barcode, dateToCheck, last_cost], index=['barcode', 'datekey', 'cost'])
                    newRowsToAdd = newRowsToAdd.append(new_row, ignore_index=True)

                else:
                    mask = ((df2['datekey'] == dateToCheck) & (df2['barcode'] == barcode))#the last known cost of this barcode
                    last_cost_index = df2.loc[mask].index.tolist()[0]
                    last_cost = df2.get_value(last_cost_index, 'cost', takeable=False)



        df = df.append(newRowsToAdd, ignore_index=True)
        # df = df.sort_values(['barcode', 'datekey'], ascending=[False, True], inplace=True) #sort dont work! check and make dictonery from df (key- barcodes, value- arrayes of prices per each day)
        print (df)

    #run kendel/pearson here
    def findPriceCoordinate(self, chain1, branch1, chain2, branch2, startDate, endDate):
        #convert from class 'wx._core.DateTime' to type 'datetime.date'
        startDate = self.__wxdate2pydate(startDate)
        endDate = self.__wxdate2pydate(endDate)
        #function that extract the realevent data to dictionery (key- barcodes, value- arrayes of prices per each day)
        branch1_PricesForProducts = self.__buildInputs (chain1, branch1, startDate, endDate)
        branch2_PricesForProducts = self.__buildInputs (chain2, branch2, startDate, endDate)


        # if (len(branch1_PricesForProducts) > 0 and len(branch2_PricesForProducts) > 0):
        #     #pearson
        #     return