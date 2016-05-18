#!/home/students/2017/stiven.peter/public_html/proj/pyth/bin/python
import datetime
import matplotlib 
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt 
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ochl
import numpy as np
from bs4 import BeautifulSoup
from urllib2 import urlopen
import urllib2
import  os
matplotlib.rcParams.update({'font.size': 10 })

def getCompDescrip(stock): # gets company descript
    BASE_URL = "http://finviz.com/quote.ashx?t="
    try :
        html = urlopen(BASE_URL+stock).read()
        soup = BeautifulSoup(html, "lxml")
        CompDescrip = soup.find("td", "fullview-profile")
        CompDescrip =  str(CompDescrip)
        return CompDescrip.strip("""<td align="left" class="fullview-profile"></td>""")
    except :
        return ""
def getCompFund(stock): # gets company fundamentals
    BASE_URL = "http://finviz.com/quote.ashx?t="
    try :
        html = urlopen(BASE_URL+stock).read()
        soup = BeautifulSoup(html, "lxml")
        Fund = soup.find("table", "snapshot-table2")
        Fund =  str(Fund)
        Fund = Fund.replace("\n","")
        Fund = Fund.replace('border="0"','border="1"')
        Fund = Fund.replace('width="100%"','width="50%"')
        Fund = Fund.replace("<table",'<table class ="table table-striped table-bordered" ')
        return Fund
    except :
        return ""
def pullData(stock, stamp = 'y', amt = 1) : # gets data from yahoo finance in a csv fie
    try :
        global timeline
        timeline = stamp
        fileLine = stock + '.txt'
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/' + str(stock) + \
        '/chartdata;type=quote;range=' + str(amt) + stamp + '/csv'
        sourceCode = urllib2.urlopen(urlToVisit).read()
        splitSource = sourceCode.split('\n')
        for eachLine in splitSource :
            splitLine = eachLine.split(',')
            tstamp = splitLine[0]
            if 'values' not in eachLine:
                if len(splitLine) == 6 :
                    if timeline == 'd':
                        fixed = eachLine.replace(tstamp,str(datetime.datetime.fromtimestamp(int(tstamp)).strftime('%Y-%m-%d %H:%M:%S')))
                        saveFile = open(fileLine,'a')
                        lineToWrite = fixed +'\n'
                        saveFile.write(lineToWrite)
                    else :
                        saveFile = open(fileLine,'a')
                        lineToWrite = eachLine +'\n'
                        saveFile.write(lineToWrite)
        saveFile.close()
    except Exception,e:
        return "Not There"
def processor(stock) : # gets the important stuff from the file
        CleanList = []
        fileLine = stock + '.txt'
        if timeline == 'd' :
            Date, Close, High,Low, Open, Volume = np.loadtxt(fileLine, 
                            delimiter = ',', unpack = True,
                            converters = { 0 : mdates.strpdate2num('%Y-%m-%d %H:%M:%S')})
        else :
            Date, Close, High,Low, Open, Volume = np.loadtxt(fileLine, 
                            delimiter = ',', unpack = True,
                            converters = { 0 : mdates.strpdate2num('%Y%m%d')})
        CleanList.append(np.array(Date).tolist())
        CleanList.append(np.array(Close).tolist())
        CleanList.append(np.array(High).tolist())
        CleanList.append(np.array(Low).tolist())
        CleanList.append(np.array(Open).tolist())
        CleanList.append(np.array(Volume).tolist())
        os.remove(fileLine)
        return CleanList
def dataextracter(stock): # organizes it in a large list
        eachlist = processor(stock)
        FinList = []
        Date = eachlist[0]
        Open = eachlist[4]
        Close = eachlist[1]
        High = eachlist[2]
        Low = eachlist[3]
        Volume = eachlist[5]
        FinList.append(Date)
        FinList.append(Open)
        FinList.append(Close)
        FinList.append(High)
        FinList.append(Low)
        FinList.append(Volume)
        return FinList
def listostock(AlistofStock, stamps, data) : # creates a dictionary with tickers as keys and hugelists as values
    global stockdict
    stockdict = {} 
    for stock in AlistofStock :
        try :
            pullData(stock, stamps, data)
            stockdict[stock] = dataextracter(stock)
        except :
            pullData('^DJI')
            stockdict['^DJI'] = dataextracter('^DJI')



def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    return sum(data)/float(n)        
def ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = 0
    for num in data :
        ss += ( (num - c) ** 2 )
    return ss

def stdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    sumsquare = ss(data)
    var = sumsquare/n # variance
    return var**0.5
def avgGrowth(stockClose): #provide range of time 
    ctr = 1 
    avgSum = [ ]
    while ctr < len(stockClose) :
        avgSum.append( float(stockClose[ctr]) / float(stockClose[ctr -1]) - 1)
        ctr += 1
    return avgSum

def sharpe(stock) : # calculates sharpe ratio
    ReturnStock = avgGrowth(stockdict[stock][2])
    RiskFree = avgGrowth(stockdict['^TYX'][2])
    RiskPremium = []
    ctr = 0
    while ctr < len(ReturnStock) :
        RiskPrem = ReturnStock[ctr] - RiskFree[ctr]
        RiskPremium.append(RiskPrem)
        ctr += 1
    AvgRisk = float(mean(RiskPremium))
    stand = np.std(stockdict[stock][2])
    return (AvgRisk/stand) * 252
def beta(stock, index= '^GSPC') :
    MarketReturnD = avgGrowth(stockdict[index][2])
    StockReturnD = avgGrowth(stockdict[stock][2])
    StockAvg = mean(StockReturnD)
    MarketAvg = mean(MarketReturnD)
    precov = 0
    ctr = 0
    while ctr < len(MarketReturnD) :
        precov += (MarketReturnD[ctr] - MarketAvg)*(StockReturnD[ctr] - StockAvg)
        ctr += 1
    cov = precov / (len(MarketReturnD) - 1)
    return cov/ np.std(MarketReturnD) ** 2.0
def CAPM(stock) :
    RiskFreeRate = (float(stockdict['^TYX'][2][-1]) /stockdict['^TYX'][2][0]) - 1
    MarketAvg = (float(stockdict['^GSPC'][2][-1]) / stockdict['^GSPC'][2][0]) - 1
    return RiskFreeRate + (beta(stock,'^GSPC')* (MarketAvg - RiskFreeRate))

def RSI(price) : 
    delta = np.diff(price)
    seed = delta[:16]
    pos = 0.0
    neg = 0.0
    for x in seed :
        if x >= 0.0 :
            pos += x
        if x < 0.0 :
            neg += x
    up = pos / 15.0
    down = -neg / 15.0
    
    rs = up/down
    rsi = np.zeros_like(price)
    rsi[:15] = 100.0 - 100.0/(1+rs)
    for i in range(15, len(price)) :
        delt = delta[i - 1]
        if delt > 0 :
            upval = delt
            downval = 0.0
        else :
            upval = 0.0
            downval = -delt
        up = (up*(15-1) + upval)/15.0
        down = (down*(15-1)+downval)/15.0
        rs = up/down
        rsi[i] = 100.0 - 100.0/(1. + rs)
    return rsi
    
def MovAvg(data,time) : # moving average
    weights = np.repeat(1.0, time)/time
    sma = np.convolve(data, weights, 'valid')
    return sma


def ExpMovAvg(data,time):
    weights = np.exp(np.linspace(-1.0,0.0,time))
    weights/= sum(weights)
    a = np.convolve(data, weights, 'full')[:len(data)]
    a[:time] = a[time]
    return a
def MACD(x,slow = 26, fast = 12) :
    emaslow = ExpMovAvg(x,slow)
    emafast = ExpMovAvg(x,fast)
    return emaslow,emafast,emafast - emaslow
    
    
    
def grapher(stock,MA1 = 12 ,MA2 = 26) : # graphing
    CandleVar = []
    x = 0
    while x < len(stockdict[stock][0]) :
        shortL = stockdict[stock]
        appLine = shortL[0][x], shortL[1][x], \
            shortL[2][x],shortL[3][x],shortL[4][x], \
            shortL[5][x]
        CandleVar.append(appLine)
        x += 1
    Av1 = MovAvg(stockdict[stock][2],MA1)    
    Av2 = MovAvg(stockdict[stock][2],MA2)
    
    SP = len(stockdict[stock][0][MA2 - 1:]) # Used to space everything evenly
    label1 = str(MA1) + 'SMA'
    label2 =str(MA2) + 'SMA'
    
    
        
    fig  = plt.figure(facecolor="#07000d" )
    
  
    
    ax1 = plt.subplot2grid((6,4) ,(1,0), rowspan=4, colspan=4, axisbg="#07000d") 
    plt.ylabel('Stock Price')
    if timeline == 'd':
        candlestick_ochl(ax1,CandleVar[-SP:],width=0.0005,colorup="#00A877",colordown="#ff1717")  
    else :
        candlestick_ochl(ax1,CandleVar[-SP:],width=0.6,colorup="#00A877",colordown="#ff1717")    # Candlesticks chart
    ax1.plot(stockdict[stock][0][-SP:],Av1[-SP:],'#5998ff',label=label1,linewidth=1.5)
    ax1.plot(stockdict[stock][0][-SP:],Av2[-SP:],'#5F9F9F',label=label2,linewidth=1.5)   
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.grid(True, color= 'white')
    ax1.yaxis.label.set_color("w")  
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis="y", colors="w")
    ax1.tick_params(axis="x", colors="w")

        
    
 
    MALeg = plt.legend(loc=9,ncol=2,prop={'size':7}, fancybox=True)
    MALeg.get_frame().set_alpha(0.4)  
    
    
    
    ax0 = plt.subplot2grid((6,4),(0,0),rowspan=1,sharex=ax1,colspan=4,axisbg="#07000d")
  
    volumeMin =  0    
    
    
    rsi = RSI(stockdict[stock][2]) # Top part
    ax0.plot(stockdict[stock][0][-SP:], rsi[-SP:],'#00ffe8',linewidth=1)
    ax0.axhline(70,color= '#8f2020')
    ax0.axhline(30,color= '#386d13')
    ax0.spines['bottom'].set_color("#5998ff")
    ax0.spines['top'].set_color("#5998ff")
    ax0.spines['left'].set_color("#5998ff")
    ax0.spines['right'].set_color("#5998ff")
    ax0.tick_params(axis="x", colors="w")
    ax0.tick_params(axis="y", colors="w")
    ax0.set_yticks([30,70])
    ax0.set_ylim(15,80) # Fills red is graph is over 70, green if under 30
    ax0.fill_between(stockdict[stock][0][-SP:], rsi[-SP:],70,where= rsi[-SP:]>=70, \
                                                 facecolor ='#8f2020',edgecolor ='#8f2020')
    ax0.fill_between(stockdict[stock][0][-SP:], rsi[-SP:],30,where=rsi[-SP:]<=30, \
                                                 facecolor ='#386d13',edgecolor ='#386d13')                                                 
    ax0.yaxis.label.set_color("w")
    plt.ylabel('RSI')
    
   
   
  
    
    ax1v = ax1.twinx()
    ax1v.fill_between(stockdict[stock][0][-SP:],volumeMin,stockdict[stock][-1][-SP:], \
                     facecolor= "#00ffe8", alpha =.5)
    ax1v.axes.yaxis.set_ticklabels([])
    
    
    
    ax1v.grid(False) 
    ax1v.yaxis.label.set_color("w")  
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis="x", colors="w")
    ax1v.tick_params(axis="y", colors="w")
    ax1v.set_ylim(0,(5*max(stockdict[stock][-1])))
    
    ax2 = plt.subplot2grid((6,4),(5,0),sharex=ax1, rowspan =1, colspan=4, axisbg ='#07000d')
    nslow = MA2
    nfast= MA1
    nema=9
    emaslow,emafast,macd = MACD(stockdict[stock][2], MA2, MA1)
    ema9 = MACD(macd,nema)
    ax2.plot(stockdict[stock][0][-SP:], macd[-SP:], color = '#4ee6fd', linewidth =2)
    ax2.plot(stockdict[stock][0][-SP:], ema9[1][-SP:], color = '#4ee6fd', linewidth = 1)
    ax2.fill_between(stockdict[stock][0][-SP:], np.array(macd)[-SP:] - ema9[1][-SP:], 0, alpha = 0.5, \
                                          facecolor = "#00ffe8", edgecolor = "#00ffe8")                         
    
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune = "upper"))
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")
    ax2.tick_params(axis="x", colors="w")
    ax2.tick_params(axis="y", colors="w")
    plt.ylabel("MACD",color = "w")
    
    
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)   
   
    
    plt.subplots_adjust(left=.09,bottom=.16,right=.94,top=.95,wspace=.20,hspace=0)
    plt.xlabel('Date',color='w')
    plt.suptitle(stock, color='w')
    plt.setp(ax0.get_xticklabels(),visible=False)
    plt.setp(ax1.get_xticklabels(),visible=False)
    fig.savefig('graph' + '.png', facecolor= fig.get_facecolor())  

