import urllib.request
import urllib
import requests
import json
from selenium import webdriver
import time
import os 
from os import path
import pandas as pd
import sys
import imp
import openpyxl
import matplotlib 
from pandas_datareader import data as pdr
import json
import csv
import datetime
import matplotlib.pylab as plt
from bs4 import BeautifulSoup
import seaborn as sns
import stock_models 
import stock_logs


"""
   this is the log functions that we can  

"""
import logging


"""
    copy this function from EastMoney_spider.py
"""

def check_trading_day(target_date):
    #we try to find whether this is trading day in the past
    tmp_url = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SECUCODE&sr=1&p=1&ps=50\
      &js=var%20blocktrade={pages:(tp),data:(x)}&filter=(Stype=%27EQA%27)(TDATE=^"+target_date.strftime( '%Y-%m-%d' ) +"^)&rt=53687669"
    temp_str_json = str(requests.get(tmp_url).text)
    if temp_str_json == "var blocktrade={pages:0,data:[]}":
        return False
    else: 
        return True

class real_time_ticker_node:
    def __init__(self, ticker,timestamp, daily_trading_node_vec):
        self.ticker = ticker
        self.timestamp = timestamp  # this field is about date 
        self.daily_trading_node_vec = daily_trading_node_vec

class daily_node:
    def __init__(self,ticker,transaction_time,transaction_price,price_change,transaction_volumn,transaction_amount,nature):
        self.transaction_time = transaction_time
        self.transaction_price = transaction_price
        self.price_change = price_change
        self.transaction_volumn = transaction_volumn
        self.transaction_amount = transaction_amount
        self.nature = nature
        self.stock_ticker = ticker





"""
    function process_page_real_time_data tries to collect real time data with one single page 
    input: the url to collect real time data with ticker, timedate, and page

"""

def process_page_real_time_data(url_for_real_time_data_url, ticker,pages_daily_trade_node_vec):
    #url_for_real_time_data_url = "http://market.finance.sina.com.cn/transHis.php?symbol=sz000001&date=2021-02-10&page=50"
    #print(url_for_real_time_data_url)
    #print(url_for_real_time_data_url)
    real_time_html_content = urllib.request.urlopen(url_for_real_time_data_url)
    print(url_for_real_time_data_url)
    bs4_real_time_content = BeautifulSoup(real_time_html_content, 'lxml')
    #real_time_period = bs4_real_time_content.select("tr")
    #real_time_price = bs4_real_time_content.select("td")
    tmp_list_first = []
    tmp_list_second = []

    """
    for i in real_time_period:
        if "style" not in i:
            tmp_list_first.append(str(i).replace("<th>","").replace("<h6>","").replace("</th>","").replace("</h5>","").replace("<h5>","").replace("</h6>","")
                                        .replace('<th style="width: 16%;">成交时间</th>','').replace('<th style="width: 16%;">性质</th>','').replace('<td style="width: 17%;">成交价</td>','')
                                        .replace('<td style="width: 17%;">价格变动</td>','').replace('<td style="width: 17%;">成交量(手)</td>','')
                                        .replace('<td style="width: 17%;">成交额(元)</td>',''))
    for i in real_time_price:
        if "style" not in i:
            tmp_list_second.append(str(i).replace("<td>","").replace("</td>","").replace('<td style="width: 17%;">成交价</td>','')
                                        .replace('<td style="width: 17%;">价格变动</td>','').replace('<td style="width: 17%;">成交量(手)</td>','')
                                        .replace('<td style="width: 17%;">成交额(元)</td>','').replace('<th style="width: 16%;">成交时间</th>','').replace('<th style="width: 16%;">性质</th>',''))

    if len(tmp_list_first)==0 or len(tmp_list_second) == 0:
        #print("tmp_list_first is empty")
        return
    """
    for i in bs4_real_time_content.find_all("tr"):
        if(len(i.find_all("th",{"style": ""}))>0 and len(i.find_all("td",{"style": ""}))>2 and i.find_all("th",{"style": ""})[1] is not None):
            tmp_timeframe = str(i.find_all("th",{"style": ""})[0]).replace("<th>","").replace("</th>","")
            tmp_nature = str(i.find_all("th",{"style": ""})[1]).replace("<th>","").replace("</th>","").replace("<h5>","").replace("</h5>","")\
                                .replace("<h1>","").replace("</h1>","").replace("<h6>","").replace("</h6>","")
            tmp_list_first.append(tmp_timeframe)
            tmp_list_first.append(tmp_nature)
            tmp_closing = str(i.find_all("td",{"style": ""})[0]).replace("<td>","").replace("</td>","")
            tmp_price_change = str(i.find_all("td",{"style": ""})[1]).replace("<td>","").replace("</td>","")
            tmp_trading_volumn = str(i.find_all("td",{"style": ""})[2]).replace("<td>","").replace("</td>","")
            tmp_trading_amount = str(i.find_all("td",{"style": ""})[3]).replace("<td>","").replace("</td>","")
            tmp_list_second.append(tmp_closing)
            tmp_list_second.append(tmp_price_change)
            tmp_list_second.append(tmp_trading_volumn)
            tmp_list_second.append(tmp_trading_amount)




    #print(tmp_list_second)
    price_change_vec = []
    date_vec = []
    closing_vec = [] 
    trading_volumn_vec = []
    trading_amount_vec = []
    trading_nature_vec = []
    for i in range(0,len(tmp_list_first),2):
        date_vec.append(tmp_list_first[i])
    for i in range(1,len(tmp_list_first),2):
        trading_nature_vec.append(tmp_list_first[i])
    for i in range(0, len(tmp_list_second),4):
        closing_vec.append(tmp_list_second[i])
    for i in range(1, len(tmp_list_second),4):
        price_change_vec.append(tmp_list_second[i])
    for i in range(2, len(tmp_list_second),4):
        trading_volumn_vec.append(tmp_list_second[i])
    for i in range(3, len(tmp_list_second),4):
        trading_amount_vec.append(tmp_list_second[i])


    #combind those data into node daily_node so the length should be the same
    length = len(date_vec)
    if(length != len(trading_nature_vec) or length!=len(closing_vec) or 
        length != len(price_change_vec) or length != len(trading_volumn_vec) 
        or length != len(trading_amount_vec)):
        print("there is something wrong in the data selection from real time trading website")
    """
    class daily_node:
        def __init__(self,ticker,transaction_time,transaction_price,price_change,transaction_volumn,transaction_amount,nature):
    """
    for i in range(0,length):
        #print(ticker,date_vec[i])
        tmp_daily_node = daily_node(ticker,date_vec[i],closing_vec[i],price_change_vec[i],trading_volumn_vec[i],trading_amount_vec[i],trading_nature_vec[i])
        #print(pages_daily_trade_node_vec)
        pages_daily_trade_node_vec.append(tmp_daily_node)
  
    #print(len(daily_trade_node_vec))





"""
    update ticker, date and pages for URL for url list 
    and process those updated urls to web collecter 

    if input parameter update_date > 0, it will update the date that is equal to update_date
"""

def update_pages_with_url(update_date):

    update_pages_with_url_log = stock_logs.Logger('logs.txt',level = 'debug')
    update_pages_with_url_log.logger.info('start in function update_pages_with_url ')


    total_url_list = []
    imp.reload(sys)
    #sys.setdefaultencoding('utf8')   
    """ 
        collect all stock tickers

    """
    shanghai_listed_companies=[]
    shenzhen_listed_companies = []
    shanghai_listed_companies, shenzhen_listed_companies =stock_models.load_universal_company_data()
    updated_listed_company = []
    for i in range(1,len(shanghai_listed_companies)):
        if shanghai_listed_companies[i] is not None:
            tmp_string = "sh"+shanghai_listed_companies[i]
            updated_listed_company.append(tmp_string)

    for i in range(1,len(shenzhen_listed_companies)):
        if shenzhen_listed_companies[i] is not None:
            tmp_string = "sz"+shenzhen_listed_companies[i]
            updated_listed_company.append(tmp_string)
    
    update_pages_with_url_log.logger.info('after collecting all companies the size is '+str(len(updated_listed_company)))



    if(update_date > 0):
        #update time frame for about more than 30 days 
        update_pages_with_url_log.logger.info('we set a time length '+str(update_date))
        current_time = datetime.date.today()
        timeframe_list = []
        time_counter = 50

        while time_counter>0:
            tmp_datetime_string = str(current_time.year)+"-"+str(current_time.month)+"-"+str(current_time.day)
            if check_trading_day(current_time):
                timeframe_list.append(current_time)
                current_time = current_time +  datetime.timedelta(days=-1)
            time_counter -= 1

        #print(timeframe_list)


        """
            we created the combination of date and tickers 

        """
        all_companies_daily_trade_node_vec = []
        for i in updated_listed_company:
                    
            for j in timeframe_list:
                all_pages_daily_trade_node_vec = []
                tmp_url = "http://market.finance.sina.com.cn/transHis.php?symbol="+str(i)+"&date="+str(j)+"&page="
                tmp_pages = 120

                write_csv_files = open('./real_time/'+i+'_'+str(j)+'.csv','a+')
                csv_writer = csv.writer(write_csv_files)
                csv_writer.writerow(["ticker","date","transaction price","price change","transaction volumn(thousand)","transaction amount","nature"])
    
                while(tmp_pages > 0):
                    tmp_url1 =tmp_url+ str(tmp_pages)
                    time.sleep(5)
                    print(tmp_url1)
                    process_page_real_time_data(tmp_url1, str(i),all_pages_daily_trade_node_vec)
                    tmp_pages-=1

                tmp_company_node = real_time_ticker_node(str(i),j,all_pages_daily_trade_node_vec)

                for k in tmp_company_node.daily_trading_node_vec:
                    csv_writer.writerow([i,str(j)+"_"+str(k.transaction_time),k.transaction_price,k.price_change,k.transaction_volumn,k.transaction_amount,k.nature])
                    print(i,str(j)+"_"+str(k.transaction_time),k.transaction_price,k.price_change,k.transaction_volumn,k.transaction_amount,k.nature)
                write_csv_files.close()
            all_companies_daily_trade_node_vec.append(tmp_company_node)
    else:
        """
            if this update_date is equal to 0, it will only update the nearest trading day real time (this only implement in historical record)

            so the first time we shall check whether it is trading day or not 

            implement save log function in csv files

            1 we collect all those urls and then we save it in a txt file 

            2 for every urls that we read we shall delete one url that we finished 

            3 the name convention shall be URLs_collection_20xx_yy_dd.txt

            4 check whether this url is the same company or different company

        """

        update_pages_with_url_log.logger.info('we only collect latest trading day ')


        current_time = datetime.date.today()
        while(check_trading_day(current_time) is not True):
            current_time += datetime.timedelta(days=-1)

        current_time_str = current_time.strftime( '%Y_%m_%d' )
        current_time_str2 = current_time.strftime( '%Y-%m-%d')

        urls_collection_today = []
        for i in updated_listed_company:
            tmp_url = "http://market.finance.sina.com.cn/transHis.php?symbol="+str(i)+"&date="+str(current_time_str2)+"&page="
            urls_collection_today.append(i+","+tmp_url)

        """
            
            write those urls in a txt files and after running those urls we shall pop up one 

        """
        
        url_collection_name = 'URL_collection_'+current_time_str+'.txt'
        if os.path.exists(url_collection_name) is not True:
            with open(url_collection_name,'a',encoding='utf-8') as f:

                for i in urls_collection_today:
                    write_txt = i+'\n'
                    
                    f.write(write_txt)
            f.close()

        
        current_company = ""
        log_file_function = open(url_collection_name,'r',encoding='utf-8')
        tmp_line = log_file_function.readline()
        all_line = log_file_function.readlines()


        
        all_companies_daily_trade_node_vec = []
        while tmp_line:
            
            current_company = tmp_line.split(",")[0].strip()
            current_url = tmp_line.split(",")[1].strip()
        
            all_pages_daily_trade_node_vec = []
            tmp_pages = 120

            write_csv_files = open('./real_time/'+current_company+'_'+current_time_str+'.csv','a+')
            csv_writer = csv.writer(write_csv_files)
            #csv_writer.writerow(["ticker","date","transaction price","price change","transaction volumn(thousand)","transaction amount","nature"])
            update_pages_with_url_log.logger.info('collect company '+current_company+" real time data")
            while(tmp_pages > 0):
                tmp_url1 =current_url+ str(tmp_pages)
                time.sleep(4)
                print(tmp_url1)
                process_page_real_time_data(tmp_url1, str(current_company),all_pages_daily_trade_node_vec)
                tmp_pages-=1

            tmp_company_node = real_time_ticker_node(str(current_company),current_time_str,all_pages_daily_trade_node_vec)

            for k in tmp_company_node.daily_trading_node_vec:
                csv_writer.writerow([current_company,str(current_time_str)+"_"+str(k.transaction_time),k.transaction_price,k.price_change,k.transaction_volumn,k.transaction_amount,k.nature])
                #print(current_company,str(current_time_str)+"_"+str(k.transaction_time),k.transaction_price,k.price_change,k.transaction_volumn,k.transaction_amount,k.nature)
            write_csv_files.close()
            update_pages_with_url_log.logger.info('after collect company '+current_company+" real time data in csv files")

            log_file_function = open(url_collection_name,'r',encoding='utf-8')
            tmp_line = log_file_function.readline()
            log_file_function.close()
            all_line = all_line[1::]
            overwrite_log_file = open(url_collection_name,'w',encoding='utf-8')
            overwrite_log_file.writelines(all_line)
            print(len(all_line))


        """
            if last partial url is the same as current_partial url, we assume that those two urls are the same company
            if last partial url is different from current url, we assume that those two urls are not the same company 

            we put same company into one csv file
        """
        """    
        with open(url_collection_name,'w',encoding='utf-8') as f:
            current_company =  f.readline().strip().split(",")[0]
            content = f.readline().strip().split(",")[1]
            if len(content) == 0 :
                print("URLs in this file are finished ")
            else:
                if current_company == last_company:
                    #those two urls are for the same company 
                    process_page_real_time_data(tmp_url1, str(i),all_pages_daily_trade_node_vec)
        """
    

        """
        all_companies_daily_trade_node_vec = []
        for i in updated_listed_company:
                    
            all_pages_daily_trade_node_vec = []
            tmp_url = "http://market.finance.sina.com.cn/transHis.php?symbol="+str(i)+"&date="+str(current_time_str)+"&page="
            tmp_pages = 120

            write_csv_files = open('./real_time/'+i+'_'++'.csv','a+')
            csv_writer = csv.writer(write_csv_files)
            csv_writer.writerow(["ticker","date","transaction price","price change","transaction volumn(thousand)","transaction amount","nature"])
    
            while(tmp_pages > 0):
                tmp_url1 =tmp_url+ str(tmp_pages)
                time.sleep(5)
                print(tmp_url1)
                process_page_real_time_data(tmp_url1, str(i),all_pages_daily_trade_node_vec)
                tmp_pages-=1

            tmp_company_node = real_time_ticker_node(str(i),current_time_str,all_pages_daily_trade_node_vec)

            for k in tmp_company_node.daily_trading_node_vec:
                csv_writer.writerow([i,str(current_time_str)+"_"+str(k.transaction_time),k.transaction_price,k.price_change,k.transaction_volumn,k.transaction_amount,k.nature])
                print(i,str(current_time_str)+"_"+str(k.transaction_time),k.transaction_price,k.price_change,k.transaction_volumn,k.transaction_amount,k.nature)
            write_csv_files.close()
        """
        
   # http://market.finance.sina.com.cn/transHis.php?symbol=&date=&page=


"""
    write those real_time_company_ticker_node to csv files 

"""
"""
def write_to_csv_company_node(real_time_company_ticker_node):
    company_ticker = real_time_company_ticker_node.ticker
    current_date = real_time_company_ticker_node.timestamp
    f = open('./real_time/'+company_ticker+'_'+str(current_date)+'.csv','w')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["ticker","date","transaction price","price change","transaction volumn(thousand)","transaction amount","nature"])
    
    for i in real_time_company_ticker_node.daily_trading_node_vec:
        csv_writer.writerow([company_ticker,str(current_date)+"_"+str(i.transaction_time),i.transaction_price,i.price_change,i.transaction_volumn,i.transaction_amount,i.nature])

    f.close()    
"""



"""
url_for_real_time_data_url = "http://market.finance.sina.com.cn/transHis.php?symbol=sh600000&date=2021-02-19&page=77"
#print(url_for_real_time_data_url)
#print(url_for_real_time_data_url)
real_time_html_content = urllib.request.urlopen(url_for_real_time_data_url)
bs4_real_time_content = BeautifulSoup(real_time_html_content, 'lxml')
real_time_period = bs4_real_time_content.find_all("tr")
for i in real_time_period:
    if(len(i.find_all("th",{"style": ""}))>0 and len(i.find_all("td",{"style": ""}))>2 and i.find_all("th",{"style": ""})[1] is not None):
        tmp_timeframe = i.find_all("th",{"style": ""})[0]
        print(tmp_timeframe)
        tmp_nature = i.find_all("th",{"style": ""})[1]
        print(str(tmp_nature).replace("<h5>","").replace("</h5>","").replace("<h1>","").replace("</h1>","").replace("<h6>","").replace("</h6>",""))

"""

"""
    trace log function: 

    we should do a trace log to record those urls that we finished and those urls that we didn't finish.


"""



count_num = 0
update_pages_with_url(count_num)

#print(os.path.exists("URL_collection_2021_03_05.txt"))

