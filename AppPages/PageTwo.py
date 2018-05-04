#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bidi import algorithm as bidialg #help display the hebrew in labels of graph in correct way

#page 2- plot prices of two branches over a certain period of time
class pageTwoLogic:
    def __init__(self, whCommunication):
        self.__whCommunication = whCommunication

    def getPricesForProduct(self, product,city, chain1, branch1, chain2, branch2, startDate, endDate):
        parameters1 = [str(product),city, chain1, branch1, str(startDate), str(endDate)]
        parameters2 = [str(product), city, chain2, branch2, str(startDate), str(endDate)]
        #query = "SELECT dateKey, cost FROM PricingProductFacts WHERE barcode=? AND cityName=? AND chainName=? AND branchName=? AND dateKey BETWEEN ? AND ?"
        query = "SELECT pp.dateKey, pp.cost FROM PricingProductFacts pp INNER JOIN dimBranch b ON pp.branchId = b.branchId LEFT JOIN dimChain ch ON ch.chainId = b.chainId LEFT JOIN dimArea a ON b.areaId = a.areaId LEFT JOIN dimCity c ON c.cityId = a.cityId INNER JOIN dimProduct p ON pp.productId = p.productId WHERE p.barcode=? AND c.cityName=? AND ch.chainName=? AND b.branchName=? AND pp.dateKey BETWEEN ? AND ?"
        df1 = self.__whCommunication.executeQuery(query, parameters1)
        df2 = self.__whCommunication.executeQuery(query, parameters2)
        text1 = bidialg.get_display(chain1 + '- '+ branch1)
        text2 = bidialg.get_display(chain2 + '- ' + branch2)
        title = 'Prices For Product '+ product
        return title, text1, df1['datekey'], df1['cost'], text2, df2['datekey'], df2['cost']
