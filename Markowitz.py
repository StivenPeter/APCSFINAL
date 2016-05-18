#!/home/students/2017/stiven.peter/public_html/proj/pyth/bin/python
import pandas as pd
import numpy as np
import urllib2
import matplotlib.pyplot as plt
from cvxopt import matrix, solvers
import numpy as np
import matplotlib
matplotlib.use('Agg')
""" Sources Used
http://rexyroo.github.io/Articles/2014/03/09/markowitz_portfolio_optimization/
https://github.com/rexyroo/Markowitz/blob/master/MarkowitzScript.py
http://blog.quantopian.com/markowitz-portfolio-optimization-2/ """

# For simplicity, assume fixed interest rate
interest_rate = 0.000005
# Minimum desired return
rmin = 0.20
def pullData(stock) :
        urlToVisit = 'http://ichart.yahoo.com/table.csv?s='
        newlURL = urlToVisit + stock
        sourceCode = urllib2.urlopen(newlURL).read()
        splitSource = sourceCode.split('\n')
        del splitSource[0]
        del splitSource[-1]
        d = {}
        newl = []
        for i in splitSource :
            newl.append(float(i.split(",")[-1]))
        d[stock]= newl
        return d
def stockStripper(alist) :
   MetaDict = {}
   minlist = []
   for i in alist :
       MetaDict.update(pullData(i))
       minlist.append(len(MetaDict[i]))
   minum = 617
   for key in MetaDict:
       MetaDict[key] = MetaDict[key][: minum - 1]
   urlToVisit = 'http://ichart.yahoo.com/table.csv?s=AAPL'
   sourceCode = urllib2.urlopen(urlToVisit).read()
   splitSource = sourceCode.split('\n')
   del splitSource[0]
   time = []
   for i in splitSource :
       time.append(i.split(",")[0])
   time = time[:minum - 1]
   arr = pd.DataFrame(MetaDict, columns = MetaDict.keys(), index = pd.to_datetime(time))
   arr.index.name = "Date"
   return arr.iloc[::-1]
#  Gets daily stock data, creates a dictionary with values length = shortest list of available prices

price = stockStripper(StockList)
# Specify number of days to shift
shift = 50 # days portfolio allocation is calculated
# Compute returns over the time period specified by shift
shift_returns = price/price.shift(shift) - 1

# Specify filter "length"
filter_len = shift
shift_returns_mean = pd.ewma(shift_returns,span=filter_len)
shift_returns_var = pd.ewmvar(shift_returns,span=filter_len)
# Compute covariances
NumStocks = len(StockList)
CovSeq = pd.DataFrame()
for FirstStock in np.arange(NumStocks-1):
	for SecondStock in np.arange(FirstStock+1,NumStocks):
		ColumnTitle = StockList[FirstStock] + '-' + StockList[SecondStock]
		CovSeq[ColumnTitle] = pd.ewmcov(
                                    shift_returns[StockList[FirstStock]],
                                    shift_returns[StockList[SecondStock]],
                                    span=filter_len)
""" Not Done by Me, see web/other sources """
def MarkowitzOpt(meanvec,varvec,covvec,irate,rmin):
	'''Framework and variable names taken from pg.155 of Boyd and Vandenberghe
	CVXOPT setup taken from:
	http://cvxopt.org/userguide/coneprog.html#quadratic-programming
	http://cvxopt.org/userguide/coneprog.html#quadratic-programming'''

	# Number of positions
	# Additional position for interest rate
	numPOS = meanvec.size+1
	# Number of stocks
	NumStocks = meanvec.size
	# mean return vector
	pbar = matrix(irate,(1,numPOS))
	pbar[:numPOS-1]=matrix(meanvec)

	# Ensure feasability Code
	pbar2 = np.array(pbar)
	if(pbar2.max() < rmin):
		rmin_constraint = irate
	else:
		rmin_constraint = rmin;

	counter = 0
	SIGMA = matrix(0.0,(numPOS,numPOS))
	for i in np.arange(NumStocks):
		for j in np.arange(i,NumStocks):
			if i == j:
				SIGMA[i,j] = varvec[i]
			else:
				SIGMA[i,j] = covvec[counter]
				SIGMA[j,i] = SIGMA[i,j]
				counter+=1

	# Generate G matrix and h vector for inequality constraints
	G = matrix(0.0,(numPOS+1,numPOS))
	h = matrix(0.0,(numPOS+1,1))
	h[-1] = -rmin_constraint
	for i in np.arange(numPOS):
		G[i,i] = -1
	G[-1,:] = -pbar
	# Generate p matrix and b vector for equality constraints
	p = matrix(1.0,(1,numPOS))
	b = matrix(1.0)
	q = matrix(0.0,(numPOS,1))
	# Run convex optimization program
	solvers.options['show_progress'] = False
	sol=solvers.qp(SIGMA,q,G,h,p,b)
	# Solution
	xsol = np.array(sol['x'])
	dist_sum = xsol.sum()

	return xsol
 # Variable Initialization'
""" Simulates the portfolio walk """
def simul() :
    START_DATE = '2014-01-13'
    INDEX = shift_returns.index
    START_INDEX = INDEX.get_loc(START_DATE)
    END_DATE = INDEX[-1]
    END_INDEX = INDEX.get_loc(END_DATE)
    DATE_INDEX_iter = START_INDEX
    StockList.append('InterestRate')
    DISTRIBUTION = pd.DataFrame(index=StockList)
    RETURNS = pd.Series(index=INDEX)
    # Start Value
    TOTAL_VALUE = 1.0
    RETURNS[INDEX[DATE_INDEX_iter]] = TOTAL_VALUE
    
    while DATE_INDEX_iter + 10 < END_INDEX:
    	DATEiter = INDEX[DATE_INDEX_iter]
    	# print DATEiter
    
    	xsol = MarkowitzOpt(shift_returns_mean.ix[DATEiter],
                            shift_returns_var.ix[DATEiter],
                            CovSeq.ix[DATEiter],interest_rate,rmin)
    
    	dist_sum = xsol.sum()
    	DISTRIBUTION[DATEiter.strftime('%Y-%m-%d')] = xsol
    
    	DATEiter2 = INDEX[DATE_INDEX_iter+shift]
    	temp1 = price.ix[DATEiter2]/price.ix[DATEiter]
    	temp1.ix[StockList[-1]] = interest_rate+1
    	temp2 = pd.Series(xsol.ravel(),index=StockList)
    	TOTAL_VALUE = np.sum(TOTAL_VALUE*temp2*temp1)
    	# print TOTAL_VALUE
    
    	# Increase Date
    	DATE_INDEX_iter += shift
    # 	print 'Date:' + str(INDEX[DATE_INDEX_iter])
    	RETURNS[INDEX[DATE_INDEX_iter]] = TOTAL_VALUE
    return RETURNS,DISTRIBUTION
      
RETURNS, DISTRIBUTION = simul()
# Remove dates that there are no trades from returns
RETURNS = RETURNS[np.isfinite(RETURNS)]
temp3 = DISTRIBUTION.T
""""GRAPHS """
def distr() :
    ax = temp3.ix[-15:].plot(kind='bar',stacked=True)
    plt.ylim([0,1])
    plt.xlabel('Date')
    plt.ylabel('Distribution')
    plt.title('Distribution vs. Time')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.subplots_adjust(left=.09,bottom=.16,right=.75,top=.95,wspace=.20,hspace=0)
    plt.savefig('dist.png')
def fun() :
    fig, axes = plt.subplots(nrows=2,ncols=1)
    price.plot(ax=axes[0])
    shift_returns.plot(ax=axes[1])
    axes[0].set_title('Stock Prices')
    axes[0].set_xlabel('Date')
    axes[0].set_ylabel('Price')
    axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    axes[1].set_title(str(shift)+ ' Day Shift Returns')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('Returns ' + str(shift) + ' Days Apart')
    axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.subplots_adjust(left=.09,bottom=.16,right=.75,top=.95,wspace=.20,hspace=0.5)
    plt.figure()
    RETURNS = RETURNS * 100
    RETURNS.plot()
    plt.xlabel('Date')
    plt.ylabel('Portolio Returns')
    plt.title('Portfolio Returns vs. Time')
    fig.savefig('stocks.png')
    plt.savefig('port.png')
distr()
fun()
