#!/home/students/2017/stiven.peter/public_html/proj/pyth/bin/python
print "Content-Type: text/html\n" 
print ""
import cgi
import random
#import cgitb
try :
    execfile("coll.py") #Collects list of Company names and Tickers
    def FStoD():
        '''
        Converts cgi.FieldStorage() return value into a standard dictionary
        '''
        d = {}
        formData = cgi.FieldStorage()
        for k in formData.keys():
            d[k] = formData[k].value
        return d    
    d = FStoD()
    try :
        unit = d['amt']
    except :
        unit = '1'
    try :
        timestamp = d['stamps']
    except :
        timestamp = 'y'   # Defailt range is 1 year
    compName = d['comp']
    compName = compName.strip(".!*)#%#")
    stockList = DictMaker()
    def checker() :
        if compName  in stockList :
            thestock = stockList[compName]
            return thestock
        else :
            thestock = compName
            return thestock
    unver = checker()  # Checks the Company name for the ticker
    execfile("alpha.py")
    def greatexcp(astock) :
        try :
            pullData(astock)
            processor(astock)
            ver = astock
        except :
            ver = random.choice(stockList.values()) 
        return ver
    stock = greatexcp(unver) # Verifies that the ticker is available on Yahoo Finance
    stocksToPull = ['^TYX','^GSPC',stock,'USO']  # Used for analysis
    listostock(stocksToPull, timestamp, unit)
    graph = 'graph' + '.png' # graph name

    funds = getCompFund(stock) # gets fundamentals
    try :
        grapher(stock,12,26)
    except :
        grapher(stock,5,10)


    descrip = getCompDescrip(stock) # Company descript
    stdev1 = stdev(stockdict[stock][2])
    try :
        beta1 = beta(stock)
        CAPM1 = CAPM(stock)
        beta2= beta(stock,'USO')
    except :
        beta1 = CAPM1 = beta2 = "Not Available"
    try :
        sharpe1 = sharpe(stock)
    except :
        sharpe1 = "Not Available"
    ##making of the htmlStr##
    htmlStr = "<!Doctype html>"
    htmlStr += """
    <html>
        
    <head>
      <title>W.P Financial</title>
     <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
      <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
      <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
      <script src="jquery.js" type="text/javascript"></script>
      <script src="jquery.smart_autocomplete.js" type="text/javascript"></script>
      <script type="text/javascript">     
          $(function(){
            var stocks = """
    htmlStr += str(stockList.keys())
    htmlStr += """
            $("#type_ahead_autocomplete_field").smartAutoComplete({source : stocks})
                          });
    </script>
        
    </head>
    <div id="wrap">

      <!-- Fixed navbar -->
      <div class="navbar navbar-inverse">
        <div class="container-fluid">
          <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#" style="margin-top: 6px">W.P Financial</a>
          </div>
          <div class="collapse navbar-collapse">
            <ul class="nav navbar-nav" style="background-color: transparent">
              <li><a href="home.html">Home</a></li>
              <li><a href="markowitz.html">Portfolio Optimization</a></li>
              <li class='active'><a href="stock.html">Stock Search</a></li>
              <li><a href='industry.html'>Top Sharpe Finder</a></li>
              <li><a href="about.html">About</a></li>
            </ul> <!-- end navmenu -->
              <form action="wrapper.py" method="get" style="display: inline;" ><input type="text" autocomplete="off" id="type_ahead_autocomplete_field" name='comp' style="margin-top: 24px; float: right; height: 30px; border: 4px solid #d4d0ba; color: indianred" /> <input type="submit" style="margin-top: 24px; float: right; height: 30px; border-radius: 5px; border: 0;" /></form>
          </div><!--/.nav-collapse -->
        </div>
      </div>
        
    <style>
        
        body {
        background-color: lemonchiffon; 
        padding: 3px;
    }
        ul li {list-style: none; cursor: pointer;}
        li.smart_autocomplete_highlight {background-color: #C1CE84;}
        ul { margin: 10px 0; padding: 5px; background-color: #E3EBBC; }
        
        </style>    

    """

    htmlStr += "<head><title>" + str(stock) +  "</title></head></html>\n"
    htmlStr += "<head> <link rel='stylesheet' src='endStyle.css'> <script src='script.js'></script></head>"
    htmlStr += "<body><div class='container'><div id='main'><h1 style='font-family: Times New Roman, serif;\
        color: indianred; \
        font-size: 40px;'>" + str(stock) + "</h1> <br>"
    htmlStr += str(descrip) + "<br>"
    htmlStr += """
    <div class="container">
    <ul class="nav nav-pills nav-justified">
      <li><a href="#Basics" data-toggle="pill">Charts</a></li>
      <li clas="active"><a href="#Advanced" data-toggle="pill">Tables and Stats</a></li>
    </ul>
    <div class="tab-content">
    """
    htmlStr += " <div  class='tab-pane active' id='Basics'> \
     <br>   <center><img src='" + str(graph) +"'></center> \
      </div> "

    htmlStr += "<div class = 'table-responsive tab-pane' id ='Advanced'> <br><center> <style='font-family: Times New Roman, serif;'>"+ str(funds) +"</style></center></div>\
    </div> \
     <div class='page-header'><h1 style='font-family: Times New Roman, serif;\
        color: indianred; \
        font-size: 40px;'>Special Stats: </h1></div><h3 style='font-family: Times New Roman, serif; size;15px'> <br><center> <table class = 'table table-striped table-bordered'> <tr> <td> Standard Deviation</td> <td>" + str(stdev1) + "</td> </tr> <tr> <td> Sharpe </td> <td>" + str(sharpe1) + "</td> \
        </tr> <tr> <td> Beta </td> <td>" + str(beta1) + \
    "</td></tr><tr><td> Beta to Oil </td><td>" + str(beta2) + \
    "</td> </tr> <tr> <td> CAPM </td> <td>" + str(CAPM1) + "</td> </tr> </table> </center> \
      </section></div></div></div></div> </body> </html>"
      
    print htmlStr

except :
    htmlStr = '<!Doctype html><html> \
    <meta HTTP-EQUIV="REFRESH" content="0; url=try.html"> \
    </html> ' 
    print htmlStr
    
