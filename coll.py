# -*- coding: utf-8 -*-
"""
Created on Sat Jun 06 23:53:37 2015

@Stiven Peter: owner
"""
# Transfers company name into ticker
def DictMaker( ) :
    instream = open('Tickers.txt','r')
    Initial = instream.read()
    Initial = Initial.split('\n')
    Initial.pop()
    Compdict = {}
    for comp in Initial :
        seper = comp.split('\t')
        seper[1] = seper[1].strip(".!*)#%#")
        Compdict[seper[1]] = seper[0]
    #for elem in Compdict:
    #    Compdict[elem.lower()]=Compdict.pop(elem)
    return Compdict
    
