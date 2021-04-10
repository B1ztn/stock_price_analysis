import urllib.request
import urllib
import requests
import json
from selenium import webdriver
import time
import os 
from os import path
import pandas as pd
import openpyxl
import matplotlib 
from pandas_datareader import data as pdr
import json
import csv
import datetime
import matplotlib.pylab as plt
from bs4 import BeautifulSoup
import seaborn as sns

"""

    http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5
    &cmd=&st=SECUCODE&sr=1&p=3&ps=50
    &js=var%20blocktrade={pages:(tp),data:(x)}&filter=(Stype=%27EQA%27)(TDATE=^2021-01-15^)&rt=53687669


"""

"""

    please make sure that those days change after block trade is floater 

"""

class blocktrade_node:
    def __init__(self, ticker, nowdate, volumn, price,amount,name,buy_side,sell_side, oneday_change_str, fiveday_change_str, tenday_change_str):
        ## if this volumn is 0, this one is not updated
        ## the volumn($) = volumn * price per share 
        self.ticker = ticker
        self.nowdate = nowdate
        self.volumn = volumn
        self.total_amount = amount
        self.price = price
        self.buy_side = [buy_side]
        self.sell_side = [sell_side]
        self.isBuyInstitution = False
        self.isSellInstitution = False
        self.name = name
        self.oneday_change = oneday_change_str
        self.fiveday_change = fiveday_change_str
        self.tenday_change = tenday_change_str
        ## vector of price change for example [ 0.02 ,0.0015, 0.008] 
        ## the day one after block trade is 2%, the second day is 0.15%, the third day is 0.8% 
        ## the reason is that we hope to keep it as placeholder 
        self.pricechange_vec = []
        if sell_side == "机构专用":
            isSellInstitution = True
        if buy_side == "机构专用":
            isBuyInstitution = True

    def AddInstitution(self):
        self.isBuyInstitution = True
        self.buy_side.append("机构")
    
    def AddSellInstitution(self):
        self.isSellInstitution = True
        self.sell_side.append("机构")
    
    def AddVolumn(self, volumn, price,amount, sell_side, buy_side):
        if buy_side == "机构专用":
            self.isBuyInstitution = True
        
        if sell_side == "机构专用":
            self.isSellInstitution = True

        self.volumn += volumn
        self.price.append(price)
        self.total_amount += amount 
        self.sell_side.append(sell_side)
        self.buy_side.append(buy_side)

    def check_trading_day(self,target_date):
        #we try to find whether this is trading day in the past
        tmp_url = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SECUCODE&sr=1&p=1&ps=50\
          &js=var%20blocktrade={pages:(tp),data:(x)}&filter=(Stype=%27EQA%27)(TDATE=^"+target_date+"^)&rt=53687669"
        temp_str_json = str(requests.get(tmp_url).text)
        if temp_str_json == "var blocktrade={pages:0,data:[]}":
            return False
        else: 
            return True





    def update_pricechange_after_blocktrade(self):
        """
            the logic of this function 
            1 make sure today's date 
            2 find the current closing date 
            3 find one day, two days, three day and four day closing price to make sure the increase or decrease
            4 the basic logic is that in low price and a discounted blocktrade, price will increase 
    
        """



        nowdate = self.nowdate
        company_name = self.name

        # make sure there is a valid trading date in one day, two day, three days and four days.
        # usually the nowday is a valid trading day in block trade 

        this_year, this_month, this_day = nowdate.split("-")[0], nowdate.split("-")[1],nowdate.split("-")[2]
        d0 = datetime.date(this_year,this_month,this_day)        
        delta_day = d0+datetime.timedelta(days=1)
        days = 0
        while days < 5:
            
            if(self.check_trading_day(delta_day)):
                days += 1
            delta_day += datetime.timedelta(days=1)

        update_ticker = self.ticker

        if update_ticker.startswith("0") or update_ticker.startswith("3"):
            update_ticker += ".sz"
        elif update_ticker.startswith("6"):
            update_ticker += ".sh"


        stock_table = pdr.DataReader(update_ticker, 'yahoo',datetime.date(int(this_year),int(this_month),int(this_day)),delta_day)
        for i in range(1, len(stock_table["Close"])):
            tmp_price_change = (stock_table["Close"][i]/stock_table["Close"][i-1])-1
            #the first price change will be day 0 / day 1 
            self.pricechange_vec.append(tmp_price_change)
        

    """
        we only count the first trading day and second trading day after the block trade happening 
        so the idea is that we hope to check whether this logic above is correct or not


    """
    def test_discount_blocktrade_method(self, blocktrade_discount_stock):
        
        f = open('qualified_companies_blocktrade.csv','w')
        csv_writer = csv.writer(f)

        print("--------------------------------------------------------")
        print("check discounted blocktrade method")
        print("--------------------------------------------------------")
        rise_in_1day = 0
        rise_in_2day = 0
        total_number = 0
        incorrect = 0
        rise_in_1day_list = []
        rise_in_2day_list = []
        incorrect_list = [] 

        for i in blocktrade_discount_stock:
            """

                we hope to find the lowest 20 percentile values and discounted blocktrade method and the date should be at least 60 days 

            """
            tmp_company_ticker = blocktrade_discount_stock[i].ticker

            current_date = datetime.date.today() + datetime.timedelta(days=5)
            past_date = current_date - datetime.timedelta(days=65)

            
            if tmp_company_ticker.startswith("0") or tmp_company_ticker.startswith("3"):
                tmp_company_ticker += ".sz"
            elif tmp_company_ticker.startswith("6"):
                tmp_company_ticker += ".sh"



            stock_table = pdr.DataReader(tmp_company_ticker, 'yahoo',past_date,current_date)
            max_price = stock_table["Close"].max()
            min_price = stock_table["Close"].min()
            fifteen_percentile_price = min_price + (max_price - min_price)*0.15

            temp_price = blocktrade_discount_stock[i].price

            total_number += 1
            if blocktrade_discount_stock[i].pricechange_vec[0]>0 and temp_price < fifteen_percentile_price:
                rise_in_1day += 1
                rise_in_1day_list.append(blocktrade_discount_stock[i].name)
                csv_writer.writerow([blocktrade_discount_stock[i].name,"qualified for one day after block trade"])
            if blocktrade_discount_stock[i].pricechange_vec[0] + blocktrade_discount_stock[i].pricechange_vec[1] > 0 and temp_price < fifteen_percentile_price:
                rise_in_2day += 1 
                rise_in_2day_list.append(blocktrade_discount_stock[i].name)
                csv.writerow([blocktrade_discount_stock[i].name,"qualified for two days after block trade"])
            if blocktrade_discount_stock[i].pricechange_vec[0]<0:
                incorrect += 1
                incorrect_list.append(blocktrade_discount_stock[i].name)


    









def output_blocktrade_companies(current_date,blocktrade_premium_dict, blocktrade_discount_dict):
    print("in the csv write")
    f = open('大宗交易溢价企业_'+current_date+'.csv','w')
    csv_writer = csv.writer(f)
    csv_writer.writerow(['company','price','volumn','buy side', 'sell side'])
    for i in blocktrade_premium_dict:
        tmp_company_name = blocktrade_premium_dict[i].name
        price = blocktrade_premium_dict[i].price
        volumn = blocktrade_premium_dict[i].volumn
        total_value = blocktrade_premium_dict[i].volumn
        buy_side = blocktrade_premium_dict[i].buy_side
        sell_side = blocktrade_premium_dict[i].sell_side
        csv_writer.writerow([tmp_company_name,str(price),str(volumn),buy_side,sell_side])
    f.close()
        


#### find the total url pages 

def output_blocktrade_EastMoney():
    dt = datetime.datetime.now() 
    current_date =  dt.strftime( '%Y-%m-%d' )
    #current_date =  "2021-01-15"
    #if today is not working day, find previous day data
    pages = 0

    
    temp_url = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SECUCODE&sr=1&p=1&ps=50\
          &js=var%20blocktrade={pages:(tp),data:(x)}&filter=(Stype=%27EQA%27)(TDATE=^"+current_date+"^)&rt=53687669"
    temp_str_json = str(requests.get(temp_url).text)

    ## if the length of string json is less than 20 and page is equal to 0, it is not a trading day so it will not traded. 
    while(len(temp_str_json)<33):
        dt -= datetime.timedelta(days=1)
        current_date =  dt.strftime( '%Y-%m-%d' )
        print(current_date)
        temp_url = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SECUCODE&sr=1&p=3&ps=50\
          &js=var%20blocktrade={pages:(tp),data:(x)}&filter=(Stype=%27EQA%27)(TDATE=^"+current_date+"^)&rt=53687669"
        temp_str_json = str(requests.get(temp_url).text)

    temp_str_json = temp_str_json[14::]

    


    temp_str_json2 = temp_str_json[1:2]+'"'+temp_str_json[2:7]+'"'+temp_str_json[7:10]+'"'+temp_str_json[10:14]+'"'+temp_str_json[14:]
    temp_str_json2.replace(" ","")
    JSON_string = json.loads(temp_str_json2,strict=False)
   ## JSON_output = eval(JSON_string)
   ## tmp_block_trade_response = json.loads(str(requests.get(temp_url).text))
    

    pages = JSON_string["pages"]
    JSON_data = JSON_string["data"]

    blocktrade_premium_stock = {}
    blocktrade_discount_stock = {}

    for i in JSON_data:
        tmp_name = i["SNAME"]
        print(tmp_name)
        if i["Zyl"] >=0 and tmp_name not in blocktrade_premium_stock:

            tmp_block_trade_node =blocktrade_node(i["SECUCODE"], current_date, i["TVOL"],i["PRICE"],i["TVAL"],i["SNAME"],i["BUYERNAME"],i["SALESNAME"],i["RCHANGE1DC"],i["RCHANGE5DC"],i["RCHANGE10DC"])
            blocktrade_premium_stock[tmp_name] = tmp_block_trade_node
        elif i["Zyl"] >=0 and tmp_name in blocktrade_premium_stock:
            ##(self, volumn, price,amount, sell_side, buy_side):
            blocktrade_premium_stock[tmp_name].AddVolumn(i["TVOL"],i["PRICE"],i["TVAL"],i["BUYERNAME"],i["SALESNAME"])

        elif i["Zyl"] <= 0 and tmp_name not in blocktrade_discount_stock:
            tmp_block_trade_node =blocktrade_node(i["SECUCODE"], current_date, i["TVOL"],i["PRICE"],i["TVAL"],i["SNAME"],i["BUYERNAME"],i["SALESNAME"],i["RCHANGE1DC"],i["RCHANGE5DC"],i["RCHANGE10DC"]) ;
            blocktrade_discount_stock[tmp_name] = tmp_block_trade_node

        elif i["Zyl"] <=0 and tmp_name in blocktrade_premium_stock:
            blocktrade_discount_stock[tmp_name].AddVolumn(i["TVOL"],i["PRICE"],i["TVAL"],i["BUYERNAME"],i["SALESNAME"])

    if(pages > 1):
        for i in range(2,pages):
            update_url = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SECUCODE&sr=1&p="+str(i)+"&ps=50\
          &js=var%20blocktrade={pages:(tp),data:(x)}&filter=(Stype=%27EQA%27)(TDATE=^"+current_date+"^)&rt=53687669"
            temp_str_json_after_pages = str(requests.get(update_url).text)[14::]

            temp_str_json_after_pages2 = temp_str_json_after_pages[1:2]+'"'+temp_str_json_after_pages[2:7]+'"'+temp_str_json_after_pages[7:10]+'"'+temp_str_json_after_pages[10:14]+'"'+temp_str_json_after_pages[14:]
            temp_str_json_after_pages2.replace(" ","")

            JSON_string_after_pages =  json.loads(temp_str_json_after_pages2, strict=False)
            JSON_data_update = JSON_string_after_pages["data"]
            for j in JSON_data_update:
                tmp_name = j["SNAME"]
                print(tmp_name)
                if j["Zyl"] >=0 and tmp_name not in blocktrade_premium_stock:

                    tmp_block_trade_node =blocktrade_node(j["SECUCODE"],current_date, j["TVOL"],j["PRICE"],j["TVAL"],j["SNAME"],j["BUYERNAME"],j["SALESNAME"],j["RCHANGE1DC"],j["RCHANGE5DC"],j["RCHANGE10DC"]) ;
                    blocktrade_premium_stock[tmp_name] = tmp_block_trade_node
                elif j["Zyl"] >=0 and tmp_name in blocktrade_premium_stock:
                    ##(self, volumn, price,amount, sell_side, buy_side):
                    blocktrade_premium_stock[tmp_name].AddVolumn(j["TVOL"],j["PRICE"],j["TVAL"],j["BUYERNAME"],j["SALESNAME"]);

                elif j["Zyl"] <= 0 and tmp_name not in blocktrade_discount_stock:
                    tmp_block_trade_node =blocktrade_node(j["SECUCODE"],current_date, j["TVOL"],j["PRICE"],j["TVAL"],j["SNAME"],j["BUYERNAME"],j["SALESNAME"],j["RCHANGE1DC"],j["RCHANGE5DC"],j["RCHANGE10DC"]);
                    blocktrade_discount_stock[tmp_name] = tmp_block_trade_node

                elif j["Zyl"] <=0 and tmp_name in blocktrade_premium_stock:
                    blocktrade_discount_stock[tmp_name].AddVolumn(j["TVOL"],j["PRICE"],j["TVAL"],j["BUYERNAME"],j["SALESNAME"])
    
    
    output_blocktrade_companies(current_date,blocktrade_premium_stock,blocktrade_discount_stock)
    ##print(type(JSON_string))


def collect_shibor_historical_rates(url,shibor_name,return_dic):
    #write the historical data period 
    shibor_html_content = urllib.request.urlopen(url)
    bs4_shibor_content = BeautifulSoup(shibor_html_content, 'lxml')
    current_shibor_rates_html = bs4_shibor_content.select("td")
    idx = 0
    current_shibor_rates = []
    for i in range(2,len(current_shibor_rates_html),3):
        tmp_list = []
        tmp_list.append(current_shibor_rates_html[i-2].get_text())
        tmp_list.append(float(current_shibor_rates_html[i-1].get_text()))
        tmp_list.append(float(current_shibor_rates_html[i].get_text()))
        #current_shibor_rates.append(tmp_list)
        current_shibor_rates.append(tmp_list)
    
    return_dic[shibor_name] = current_shibor_rates



def collect_shibor_rates():

    shibor_website = "http://data.eastmoney.com/shibor/default.html"
    shibor_html_content = urllib.request.urlopen(shibor_website)
    bs4_shibor_content = BeautifulSoup(shibor_html_content, 'lxml')
    #print(shibor_html_content)
    #print(bs4_shibor_content.select("td"))
    current_shibor_rates = [["O/N"],["1W"],["2W"],["1M"],["3M"],["6M"],["9M"],["1Y"]]
    current_shibor_rates_html = bs4_shibor_content.select("td")
    idx = 0
    for i in range(2,len(current_shibor_rates_html),3):
        tmp_list = []
        tmp_list.append(current_shibor_rates_html[i-2].get_text())
        tmp_list.append(current_shibor_rates_html[i-1].get_text())
        tmp_list.append(current_shibor_rates_html[i].get_text())
        #current_shibor_rates.append(tmp_list)
        current_shibor_rates[idx].append(current_shibor_rates_html[i-1].get_text())
        current_shibor_rates[idx].append(current_shibor_rates_html[i].get_text())
        idx+=1

    #this one includes dataes, interest rates and yield
    return_dic = {}
    shibor_name_url_mapping = {
        "O/N":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99221&cu=cny&type=009016",
        "1W":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99222&cu=cny&type=009017",
        "2W":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99223&cu=cny&type=009018",
        "1M":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99224&cu=cny&type=009019",
        "3M":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99225&cu=cny&type=009020",
        "6M":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99226&cu=cny&type=009021",
        "9M":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99227&cu=cny&type=009022",
        "1Y":"http://data.eastmoney.com/shibor/shibor.aspx?m=sh&t=99&d=99228&cu=cny&type=009023"
    }
    for i in shibor_name_url_mapping:
        collect_shibor_historical_rates(shibor_name_url_mapping[i],i,return_dic)
    
    historical_rates_dic ={}
    time_vec = []
    for i in return_dic["O/N"]:
        time_vec.append(i[0])
    
    for i in return_dic:
        historical_rates_dic[i] = []
        for j in return_dic[i]:
            historical_rates_dic[i].append(j[1])

    print(historical_rates_dic)

    #draw the sns line historical one 
    plt.style.use('seaborn-darkgrid')
    my_dpi=96
    plt.figure()
    sns.set()
    plt.plot(time_vec,historical_rates_dic["O/N"],color = 'tab:blue', label = 'O/N')
    plt.plot(time_vec,historical_rates_dic["1W"],color = 'tab:orange', label = '1W')
    plt.plot(time_vec,historical_rates_dic["2W"],color = 'tab:green', label = '2W')
    plt.plot(time_vec,historical_rates_dic["1M"],color = 'tab:red', label = '1M')
    plt.plot(time_vec,historical_rates_dic["3M"],color = 'tab:purple', label = '3M')
    plt.plot(time_vec,historical_rates_dic["6M"],color = 'tab:brown', label = '6M')
    plt.plot(time_vec,historical_rates_dic["9M"],color = 'tab:pink', label = '9M')
    plt.plot(time_vec,historical_rates_dic["1Y"],color = 'tab:gray', label = '1Y')
     
   

    plt.legend() 
    plt.show()

    #print(return_dic["1W"])



