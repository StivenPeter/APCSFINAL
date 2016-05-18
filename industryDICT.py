# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 19:09:20 2015

@author: waris
"""
# Create a dictionary that returns industries as keys, and list of tickers as values
def industryDICT():
    ind = open('industry.csv','r')
    indR = ind.readlines()
    ctr = 0
    while ctr<len(indR):
        indR[ctr] = indR[ctr].strip()
        indR[ctr] = indR[ctr].split('\t')
        ctr += 1
    indDict = {}
    for elem in indR:
        if elem[1] not in indDict.keys():
            indDict[elem[1]] = [elem[0]]
        else:
            indDict[elem[1]] += [elem[0]]
    return indDict

#print indDict()
