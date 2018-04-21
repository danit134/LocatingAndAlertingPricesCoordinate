#!/usr/bin/env python
# -*- coding: utf-8 -*-

from warehouseCommunication import *
import matplotlib.pyplot as plt
from bidi import algorithm as bidialg #help display the hebrew in labels of graph in correct way

class pageTwoLogic:
    def __init__(self, whCommunication):
        self.__whCommunication = whCommunication

    # #convert query results to dataframe
    # def __as_pandas(self, cursor):
    #     names = [metadata[0] for metadata in cursor.description]
    #     return pd.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)


    def getPricesForProduct(self, product,city, chain1, branch1, chain2, branch2, startDate, endDate):
        parameters1 = [str(product),city, chain1, branch1, str(startDate), str(endDate)]
        parameters2 = [str(product), city, chain2, branch2, str(startDate), str(endDate)]
        query = "SELECT dateKey, cost FROM PricingProductFacts WHERE barcode=? AND cityName=? AND chainName=? AND branchName=? AND dateKey BETWEEN ? AND ?"
        df1 = self.__whCommunication.executeQuery(query, parameters1)
        df2 = self.__whCommunication.executeQuery(query, parameters2)
        text1 = bidialg.get_display(chain1 + '- '+ branch1)
        text2 = bidialg.get_display(chain2 + '- ' + branch2)
        title = 'Prices For Product '+ product
        return title, text1, df1['datekey'], df1['cost'], text2, df2['datekey'], df2['cost']
        # plt.plot(df1['datekey'], df1['cost'], "-o", alpha=0.7, label= text1, color='red')
        # plt.plot(df2['datekey'], df2['cost'], "-o", alpha=0.4, label=text2, color='blue')
        # plt.xticks(rotation=40)
        # # naming the x-axis
        # plt.xlabel('Date')
        # # naming the y-axis
        # plt.ylabel('Price (in Shekels)')
        # # plot title
        # plt.title('Prices For Product '+ product)
        # plt.legend()
        # return plt
