#!/usr/bin/env python
# -*- coding: utf-8 -*-
from warehouseCommunication import *
import pandas as pd
import wx
import collections
from scipy.stats import pearsonr
import numpy as np
import math


class buildPageOne:
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

    def chainExist(self, chainName):
        if (chainName in self.__branchesInChains):
            return True
        else:
            return False

    def branchExist(self, chainName, branchName):
        if (branchName in self.__branchesInChains[chainName]):
            return True
        else:
            return False

    def __getProductsPrices(self, chain, branch, startDate, endDate):
        parameters = [chain, branch, str(startDate), str(endDate)]
        query = "SELECT barcode, dateKey, cost FROM PricingProductFacts WHERE chainName=? AND branchName=? AND dateKey BETWEEN ? AND ?"
        df = self.__whCommunication.executeQuery(query, parameters)
        return df

    # assistance function that convert from class 'wx._core.DateTime' to type 'datetime.date'
    def __wxdate2pydate(self, date):
        import datetime
        assert isinstance(date, wx.DateTime)
        if date.IsValid():
            ymd = map(int, date.FormatISODate().split('-'))
            return datetime.date(*ymd)
        else:
            return None


    # function that extract the realevent data to dictionery (key- barcodes, value- arrayes of prices per each day)
    def __buildInputsForPearson (self, chain, branch, startDate, endDate):
        df = self.__getProductsPrices(chain, branch, startDate, endDate)
        if (df.empty):
            return None

        df['datekey'] = df['datekey'].apply(lambda x: x.date()) # convert the columns- datekey from timestamp to type 'datetime.date'
        countProducts = df['barcode'].value_counts()  #count how many different barcodes we have (this way we discovered all products need to filled there dates)
        numOfDays = (endDate - startDate).days + 1
        needToFilledProducts = countProducts[countProducts < numOfDays]
        df_ProductsWithGaps = df[df['barcode'].isin(list(needToFilledProducts.keys()))] # df_ProductsWithGaps contain all the rows of products from df that have missing rows (dates)
        datesList = pd.date_range(startDate, periods=numOfDays).tolist()
        newRowsToAdd = pd.DataFrame()#dataframe that contain all the missing products's dates and their costs

        #find all the dates that missing for each incomplete product (barcode) and complete its cost from the nearest available date
        for barcode in needToFilledProducts.keys():# run on all products that have missing dates
            last_cost = -1.0
            for dateToCheck in datesList: #run on all dates (from start to end date)
                if (needToFilledProducts[barcode] < numOfDays):
                    dateToCheck = dateToCheck.date()
                    if not (((df_ProductsWithGaps['datekey'] == dateToCheck) & (df_ProductsWithGaps['barcode'] == barcode)).any()):
                        if (last_cost == -1.0): #we dont have the cost of the day before
                            last_cost_index = df_ProductsWithGaps.barcode[df_ProductsWithGaps.barcode == barcode].index.tolist()[0]
                            last_cost = df_ProductsWithGaps.get_value(last_cost_index, 'cost', takeable=False) #the earliest cost of this barcode(of the next day)
                        new_row = pd.Series([barcode, dateToCheck, last_cost], index=['barcode', 'datekey', 'cost'])
                        newRowsToAdd = newRowsToAdd.append(new_row, ignore_index=True)
                        needToFilledProducts[barcode]+=1

                    else: #this date dont missing- remember the last known cost of this product
                        mask = ((df_ProductsWithGaps['datekey'] == dateToCheck) & (df_ProductsWithGaps['barcode'] == barcode))
                        last_cost_index = df_ProductsWithGaps.loc[mask].index.tolist()[0]
                        last_cost = df_ProductsWithGaps.get_value(last_cost_index, 'cost', takeable=False)
                else:
                    break #we complete all the dates for current product- go to the next product

        branch_PricesForProducts = {}
        df = df.append(newRowsToAdd, ignore_index=True)
        df = df.sort_values(by=['barcode', 'datekey'], ascending=[0, 1]) #sort the complete df (all the dates and their costs for all products is there)

        # create dictionary from df (key- barcodes, value- arrayes of prices per each day)
        for barcode in countProducts.keys():
            costsFromDf = df.loc[df['barcode'] == barcode, ['cost']].values
            cost_list = []
            for cost in costsFromDf:
                cost_list.append(round(float(cost[0]), 2))#convert cost to float
            branch_PricesForProducts[barcode] = cost_list
        # branch_PricesForProducts = collections.OrderedDict(sorted(branch_PricesForProducts.items()))
        return branch_PricesForProducts

    def __average(self, x):
        assert len(x) > 0
        return float(sum(x)) / len(x)

    def __pearsonCalc(self, x, y):
        assert len(x) == len(y)
        n = len(x)
        assert n > 0
        avg_x = self.__average(x)
        avg_y = self.__average(y)
        diffprod = 0
        xdiff2 = 0
        ydiff2 = 0
        for idx in range(n):
            xdiff = x[idx] - avg_x
            ydiff = y[idx] - avg_y
            diffprod += xdiff * ydiff
            xdiff2 += xdiff * xdiff
            ydiff2 += ydiff * ydiff
        return diffprod / math.sqrt(xdiff2 * ydiff2)

    def __all_same(self, items):
        return all(x == items[0] for x in items)

    #run kendel/pearson here
    def findPriceCoordinate(self, chain1, branch1, chain2, branch2, startDate, endDate):
        #convert from class 'wx._core.DateTime' to type 'datetime.date'
        startDate = self.__wxdate2pydate(startDate)
        endDate = self.__wxdate2pydate(endDate)
        #function that extract the realevent data to dictionery (key- barcodes, value- arrayes of prices per each day)
        branch1_PricesForProducts = self.__buildInputsForPearson (chain1, branch1, startDate, endDate)
        branch2_PricesForProducts = self.__buildInputsForPearson (chain2, branch2, startDate, endDate)


        pearsonResults = {} #key- product, value- pearson correlation between the arrays of the 2 branches
        if ((branch1_PricesForProducts is not None) and (branch2_PricesForProducts is not None)):
             #loop on all barcode that are appear in two dictionary
             for barcode in branch1_PricesForProducts.viewkeys() & branch2_PricesForProducts.viewkeys():
                 #check if the series contain the same value. if it those- set nan at the result (for example two identical series- return 1 in pearson but its not really price fixing)
                 if (self.__all_same(branch1_PricesForProducts[barcode]) and self.__all_same(branch1_PricesForProducts[barcode])):
                  if (branch1_PricesForProducts[barcode][0] != branch2_PricesForProducts[barcode][0]): #if we have two identical series but each series have different number- no price correlation. example-[9.9,9.9,9.9], [8.8,8.8,8.8]
                      pearsonResults[barcode] = np.nan
                  else:#if we have two identical series we have price correlation. example-[3.7,3.7,3.7], [3.7,3.7,3.7]
                      pearsonResults[barcode] = 1.0
                  continue

                 try:
                     result = self.__pearsonCalc(branch1_PricesForProducts[barcode], branch2_PricesForProducts[barcode])
                     pearsonResults[barcode] = result
                 except(ZeroDivisionError):
                     pearsonResults[barcode] = np.nan



        #write the results dic to csv file or maybe show the results on the apll and the user can export to file.. choose only the results > 0.6
        print (pearsonResults)
        return