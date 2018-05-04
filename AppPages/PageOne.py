#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from AppPages.mutualMethods import *
import csv
import os
import itertools

#page 1- discover price coordinate between two branches (between 2 specific branches or between 2 branches in a particular areas)
class pageOneLogic:
    def __init__(self, mutualMet, whCommunication):
        self.__whCommunication = whCommunication
        self.__mutualMet = mutualMet

    def findPriceCoordinateInCity (self, city, areasNames, startDate, endDate, pathToResultFile):
        branchesAndChainsInArea = {}
        for area in areasNames:
            df =  self.__mutualMet.getAllBranchesInArea(city, area)
            branchesAndChainsInArea[area] = {}
            for index, row in df.iterrows():
                chainName = (row['chainname']).decode('cp1255', 'strict')
                branchName = (row['branchname']).decode('cp1255', 'strict')
                if (chainName not in branchesAndChainsInArea[area]):
                    branchesAndChainsInArea[area][chainName] = []
                    branchesAndChainsInArea[area][chainName].append(branchName)
                else:
                    branchesAndChainsInArea[area][chainName].append(branchName)

        # branchesAndChains = self.__mutualMet.getAllBranchesAndChainsInCity(city)
        branchesAndChainsInArea = branchesAndChainsInArea[area]
        allCombinationsOfChainsInArea = map(dict, itertools.combinations(branchesAndChainsInArea.iteritems(), 2)) #contain dictionaries of all chains combination in city
        for chainPair in allCombinationsOfChainsInArea:
            chain1 = list(chainPair.keys())[0]
            chain2 = list(chainPair.keys())[1]
            branchs1 = branchesAndChainsInArea[chain1]
            branchs2 = branchesAndChainsInArea[chain2]
            allCombinationsOfBranches = list(itertools.product(branchs1, branchs2))
            for (branch1,branch2) in allCombinationsOfBranches:
                self.findPriceCoordinate(city, chain1, branch1, chain2, branch2, startDate, endDate, pathToResultFile)

    def __CountSamePrice(self, startDate, endDate, chain1, chain2, product, productPrice):
        parameters = [startDate, endDate, chain1, chain2, product, productPrice]
        query = "SELECT COUNT(DISTINCT ch.chainName) AS count FROM PricingProductFacts pp INNER JOIN dimBranch b ON pp.branchId = b.branchId LEFT JOIN dimChain ch ON ch.chainId = b.chainId INNER JOIN dimProduct p ON pp.productId = p.productId WHERE pp.dateKey BETWEEN ? AND ? AND ch.chainName!=? AND ch.chainName!=? AND p.barcode=? AND pp.cost=?"
        df = self.__whCommunication.executeQuery(query, parameters)
        count = df.iloc[0]['count']
        return count

    # Run pearson algorithm on 2 branches
    def findPriceCoordinate(self,city, chain1, branch1, chain2, branch2, startDate, endDate, pathToResultFile):
        # convert from class 'wx._core.DateTime' to type 'datetime.date'
        startDate = self.__mutualMet.wxdate2pydate(startDate)
        endDate = self.__mutualMet.wxdate2pydate(endDate)
        # function that extract the relevant data to dictionary (key- barcodes, value- arrays of prices per each day)
        branch1_PricesForProducts = self.__buildInputsForPearson(city, chain1, branch1, startDate, endDate)
        branch2_PricesForProducts = self.__buildInputsForPearson(city, chain2, branch2, startDate, endDate)

        pearsonResults = {}  # key- product's barcode, value- pearson correlation score between the arrays of the 2 branches
        if ((branch1_PricesForProducts is not None) and (branch2_PricesForProducts is not None)):
            # loop on all barcode that are appear in two dictionary
            for barcode in branch1_PricesForProducts.viewkeys() & branch2_PricesForProducts.viewkeys():
                # check if the series contain the same values(two identical series- return sometimes 1 in pearson but its not really price fixing)
                if (self.__all_same(branch1_PricesForProducts[barcode]) and self.__all_same(branch1_PricesForProducts[barcode])):
                    if (branch1_PricesForProducts[barcode][0] == branch2_PricesForProducts[barcode][0]):  # if we have two identical series we maybe have price correlation. example-[3.7,3.7,3.7], [3.7,3.7,3.7]
                        threshold = 0 # number of different branches we allow to have the same price as the 2 branches for current product in this iteration
                        productPrice = branch1_PricesForProducts[barcode][0]
                        count = self.__CountSamePrice (startDate, endDate, chain1, chain2, barcode, productPrice)
                        if (count <= threshold): #we check if the identical series are really price cooridnate bwtween 2 branches. (or maybe this price is set in amother chains and then its not cooridnate)
                            pearsonResults[barcode] = 1.0
                    #cases where we will continue to next product:
                        #we have two identical series but each series have different number- no price correlation. example-[9.9,9.9,9.9], [8.8,8.8,8.8].nan values not interesting.
                        #we have two series different from each other but each series have identical price (return sometimes 1 in pearson but its not really price fixing)
                    continue
                try:
                    result = self.__pearsonCalc(branch1_PricesForProducts[barcode], branch2_PricesForProducts[barcode])
                    if (result > 0):  # negative values not interesting
                        pearsonResults[barcode] = result
                except(ZeroDivisionError):
                    continue


        # write the results dic to csv file or maybe show the results on the apll and the user can export to file.. choose only the results > 0.6
        if (len(pearsonResults) > 0):
            fileName = city+"_"+chain1+" "+branch1+"_"+chain2+" "+branch2+"_"+str(startDate)+"_"+str(endDate)
            self.__writeResultsToCSV(pearsonResults, pathToResultFile, fileName)
            return True
        return False

    def __getProductsPrices(self,city, chain, branch, startDate, endDate):
        parameters = [city, chain, branch, str(startDate), str(endDate)]
        query = "SELECT p.barcode, pp.dateKey, pp.cost FROM PricingProductFacts pp INNER JOIN dimBranch b ON pp.branchId = b.branchId LEFT JOIN dimChain ch ON ch.chainId = b.chainId LEFT JOIN dimArea a ON b.areaId = a.areaId LEFT JOIN dimCity c ON c.cityId = a.cityId INNER JOIN dimProduct p ON pp.productId = p.productId WHERE c.cityName=? AND ch.chainName=? AND b.branchName=? AND pp.dateKey BETWEEN ? AND ?"
        df = self.__whCommunication.executeQuery(query, parameters)
        return df

    # function that extract the realevent data to dictionery (key- barcodes, value- arrayes of prices per each day)
    def __buildInputsForPearson (self, city, chain, branch, startDate, endDate):
        df = self.__getProductsPrices(city, chain, branch, startDate, endDate)
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

        # create dictionary from df (key- barcodes, value- arrays of prices per each day)
        for barcode in countProducts.keys():
            costsFromDf = df.loc[df['barcode'] == barcode, ['cost']].values
            cost_list = []
            for cost in costsFromDf:
                cost_list.append(round(float(cost[0]), 2))#convert cost to float
            branch_PricesForProducts[barcode] = cost_list
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

    def __writeResultsToCSV(self, results, pathToResultFile, fileName):
        productNameColumnTemp = [self.__mutualMet.getProductName(barcode) for barcode in results.keys()]
        productNameColumn = [x.encode('cp1255', 'strict') for x in productNameColumnTemp]
        barcodeColumn = results.keys()
        correlationScoreColumn =  results.values()
        fileName = fileName.replace(u'"', '')
        foupath = os.path.join(pathToResultFile, '%s.csv' % fileName)
        fou = open(foupath, 'wb')
        writer = csv.writer(fou)
        writer.writerow(["Product Barcode", "Product Name", "Correlation Score"])
        for val in itertools.izip(barcodeColumn, productNameColumn, correlationScoreColumn):
            writer.writerow(val)
