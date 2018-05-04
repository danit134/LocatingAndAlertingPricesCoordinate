#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import itertools


#page 3- the cheapest shopping basket
class pageThreeLogic:
    def __init__(self, mutualMet, whCommunication):
        self.__whCommunication = whCommunication
        self.__mutualMet = mutualMet
        self.__priceOfProductsInBranches = {}
        self.__sumPricesOfBranches = {}


    def __filledDicInPrices(self, city, productsNames, date):
        for chain in self.__priceOfProductsInBranches.keys():
            for branch in self.__priceOfProductsInBranches[chain].keys():
                for productName in productsNames:
                    barcode = self.__mutualMet.getBarcode(productName)
                    parameters = [city, chain, branch, date, barcode]
                    query = "SELECT pp.cost, pp.saleCost, pp.saleDesc FROM PricingProductFacts pp INNER JOIN dimBranch b ON pp.branchId = b.branchId LEFT JOIN dimChain ch ON ch.chainId = b.chainId LEFT JOIN dimArea a ON b.areaId = a.areaId LEFT JOIN dimCity c ON c.cityId = a.cityId INNER JOIN dimProduct p ON pp.productId = p.productId WHERE c.cityName=? AND ch.chainName=? AND b.branchName=? AND pp.dateKey=? AND p.barcode=?"
                    df = self.__whCommunication.executeQuery(query, parameters)
                    for index, row in df.iterrows():
                        price = row['cost']
                        salePrice = row['salecost']
                        saleDesc = row['saledesc']
                        #if sale is exist we take salePrice and not the original price.
                        if (salePrice is None and price is not None):
                            self.__priceOfProductsInBranches[chain][branch][productName] = (price, None)
                        elif (salePrice is not None):
                            if (saleDesc is not None):
                                saleDesc = saleDesc.decode('cp1255', 'strict').rstrip()
                            self.__priceOfProductsInBranches[chain][branch][productName] = (salePrice, saleDesc)

    #init the dictionary that contain the sum of all prices per branches for *all* the products that insert in the app
    def __initSumPricesDic (self, productsNames):
        for chain in self.__priceOfProductsInBranches.keys():
            for branch in self.__priceOfProductsInBranches[chain].keys():
                if (len(self.__priceOfProductsInBranches[chain][branch].keys()) == len(productsNames)): #if branch not contain all the products we ignore it
                    self.__sumPricesOfBranches[chain]= {}
                    self.__sumPricesOfBranches[chain][branch] = 0

    def __sumAllProductPrices(self, productsNames):
        minSum = float('inf')
        self.__initSumPricesDic(productsNames)
        for chain in self.__sumPricesOfBranches.keys():
            for branch in self.__sumPricesOfBranches[chain].keys():
                branchSum = 0 #sum of all price's products in current branch
                for productName in productsNames:
                    branchSum += self.__priceOfProductsInBranches[chain][branch][productName][0]
                self.__sumPricesOfBranches[chain][branch] = branchSum
                if (branchSum < minSum):
                    minSum = branchSum
        return minSum

    def __getCheapestBranchs(self, minSum):
        cheapestBranches = []
        for chain in self.__sumPricesOfBranches.keys():
            for branch in self.__sumPricesOfBranches[chain].keys():
                if (self.__sumPricesOfBranches[chain][branch] == minSum):
                    cheapestBranches.append ((chain, branch))
        return cheapestBranches

    def __getColumnsForCSV(self, branchTuple, productsNames):
        branchDic = self.__priceOfProductsInBranches[branchTuple[0]][branchTuple[1]]
        priceColumn = []
        saleDescColumn = []
        for product in productsNames:
            priceColumn.append(branchDic[product][0])
            saleDecs = branchDic[product][1]
            if (saleDecs is None):
                saleDecs = ''
            saleDescColumn.append(saleDecs)
        return priceColumn, saleDescColumn

    def __writeBasketToCSV(self, productsNames, priceColumn, saleDescColumn, pathToResultFile, fileName, minSum):
        productNameColumn = [x.encode('cp1255', 'strict') for x in productsNames]
        priceColumn.append("total ="+(str(minSum)).decode('utf-8'))
        saleDescColumn = [x.encode('cp1255', 'strict') for x in saleDescColumn]
        fileName = fileName.replace(u'"', '')
        foupath = os.path.join(pathToResultFile, '%s.csv' % fileName)
        fou = open(foupath, 'wb')
        writer = csv.writer(fou)
        writer.writerow(["Product Name", "Price", "Sale Description"])
        for val in itertools.izip(productNameColumn, priceColumn, saleDescColumn):
            writer.writerow(val)
        writer.writerow(['', (str(minSum)).decode('utf-8'), ''])

    def findTheCheapestBasket(self, city, areasNames, productsNames, date, pathToResultFile):
        # if the user want to find another cheap basket its needed to init the dictionaries
        self.__priceOfProductsInBranches = {}
        self.__sumPricesOfBranches = {}

        date = self.__mutualMet.wxdate2pydate(date)
        for area in areasNames:
            df = self.__mutualMet.getAllBranchesInArea(city, area)
            for index, row in df.iterrows():
                chainName = (row['chainname']).decode('cp1255', 'strict')
                branchName = (row['branchname']).decode('cp1255', 'strict')
                if (chainName not in self.__priceOfProductsInBranches):
                    self.__priceOfProductsInBranches[chainName] = {}
                if (branchName not in self.__priceOfProductsInBranches[chainName]):
                    self.__priceOfProductsInBranches[chainName][branchName] = {}
        self.__filledDicInPrices(city, productsNames, date)
        minSum = self.__sumAllProductPrices(productsNames) #return the lowest sum prices for all the products insert
        cheapestBranches = self.__getCheapestBranchs(minSum)
        for branchTuple in cheapestBranches:
            priceColumn, saleDescColumn = self.__getColumnsForCSV(branchTuple, productsNames)
            fileName = u"cheapestBasket_"+city+"_"+branchTuple[0]+" "+branchTuple[1]+"_"+str(date)
            self.__writeBasketToCSV(productsNames, priceColumn, saleDescColumn, pathToResultFile, fileName, minSum)
        return (len(cheapestBranches) > 0)



