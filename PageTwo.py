#!/usr/bin/env python
# -*- coding: utf-8 -*-

from warehouseCommunication import *
import matplotlib.pyplot as plt


class buildPageTwo:
    def __init__(self):
        self.__whCommunication = whCommunication()
        self.__products = self.__getAllProductsQuery()
        self.__branchesInChains = self.__getBranchesInChains()

    #convert query results to dataframe
    def __as_pandas(self, cursor):
        names = [metadata[0] for metadata in cursor.description]
        return pd.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)

    #get the list of all produsts in the warehouse
    def __getAllProductsQuery(self):
        query = "select barcode from dimProduct"
        df = self.__whCommunication.executeQuery(query, [])
        Productslist = df['barcode'].tolist()
        return Productslist

    def __getBranchesInChains(self):
        branchesAndChains = {}
        query = "select chainName, branchName, codeMarket from dimBranch"
        df = self.__whCommunication.executeQuery(query, [])
        for index, row in df.iterrows():
            if ((row['chainname'].decode('cp1255','strict')) not in branchesAndChains):
                branchesAndChains[(row['chainname']).decode('cp1255','strict')] = []
            branchesAndChains[(row['chainname']).decode('cp1255', 'strict')].append((row['branchname']).decode('cp1255', 'strict'))
        return branchesAndChains

    def getAllProducts(self):
        return self.__products

    def getAllBrunchNamesInchain(self, chain):
        return (self.__branchesInChains[chain])

    def getAllChains(self):
        return list(self.__branchesInChains.keys())

    def getPriceForProduct(self, product, chain, branch, startDate, endDate):
        parameters = [str(product),chain, branch, str(startDate), str(endDate)]
        query = "SELECT dateKey, cost FROM PricingProductFacts WHERE barcode=? AND chainName=? AND branchName=? AND dateKey BETWEEN ? AND ?"
        df = self.__whCommunication.executeQuery(query, parameters)
        # print (df)
        plt.plot(df['datekey'], df['cost'], "-o")
        plt.xticks(rotation=40)
        # naming the x-axis
        plt.xlabel('Date')
        # naming the y-axis
        plt.ylabel('Price (in Shekels)')
        # plot title
        plt.title('Prices For Product')
        return plt