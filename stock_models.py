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

import datetime


## collect universal company list 
def update_universal_company_list():

  if(path.exists('shh_list_company.txt')):
    os.remove('shh_list_company.txt')
  
  if(path.exists('sz_list_company.xlsx')):
    os.remove('sz_list_company.xlsx')

  if(path.exists('主板A股.xls')):
    os.remove('主板A股.xls')
  print("update universal company list ")
  """

  shenzhen list download including 000001(not included) and 300001(included)
 
  """ 
  sz_list_url = "http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.1755483287687798"
  ##sz_list_excel = requests.get(sz_list_url)
  urllib.request.urlretrieve(sz_list_url,"sz_list_company.xlsx")
  #shh_list_url = "http://www.sse.com.cn/assortment/stock/list/share/"
  #response = urllib.request.urlopen(shh_list_url)

  """
    
    shanghai list company download 
  
  """  

  opt = webdriver.ChromeOptions()
  opt.set_headless()
  opt.add_experimental_option('prefs', {
    "download.default_directory": r"D:\stock_project",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
  })
  driver = webdriver.Chrome(options=opt) 
  driver.get('http://www.sse.com.cn/assortment/stock/list/share/') 
  #time.sleep(20)  
  element = driver.find_elements_by_link_text('下载')[0]
  element.click()

  """
      
      we change the name and check whether the file is existing 

  """

  #if there is a old shanghai list company xls, delete it 
  if(path.exists('shh_list_company.txt')):
    os.remove('shh_list_company.txt')

  while not os.path.exists('主板A股.xls'):
    time.sleep(1)
  #change downloaded SHH listed companies xls file name to shh_list_excel

  os.rename('主板A股.xls','shh_list_company.txt')

  if path.exists('shh_list_company.txt'):
    print("shanghai listed company list is updated ")

  if path.exists('sz_list_company.xlsx'):
    print("shenzhen listed company list is updated ")

## extract those company codes from txt and xlsx files 
def load_universal_company_data():
  ##extract shanghai listed companies 
  shanghai_listed_companies = []
  shenzhen_listed_companies = []
  shh_list_tmp = open('shh_list_company.txt','r')
  line = shh_list_tmp.readlines()
  for i in line:
        shanghai_listed_companies.append(i[0:6])
  
  ##extract shenzhen listed companies 
  shenzhen_list_temp = openpyxl.load_workbook('sz_list_company.xlsx')
  shenzhen_list_sheet = shenzhen_list_temp['A股列表']
  for cases in list(shenzhen_list_sheet.rows)[1:]:
    case_data = cases[4].value        
    shenzhen_listed_companies.append(case_data)
  
  shenzhen_list_temp.close()
  
  return shanghai_listed_companies, shenzhen_listed_companies

## model 1 find companies with moving average cross with greater volumn 

def check_five_and_ten_days_moving_average(fiveday_closing_vec, tenday_closing_vec):
  maxlength = len(tenday_closing_vec)-1
  check_vector = 0
  check_end = fiveday_closing_vec[0]>tenday_closing_vec[0]
  check_start = fiveday_closing_vec[maxlength] <  tenday_closing_vec[maxlength]
  return check_end and check_start



def moving_average_greater_volumn_model(ticker,start_time, end_time):
  start_month, start_day, start_year = start_time.split('/')
  end_month, end_day, end_year = end_time.split('/')
  five_day_average = {}
  ten_day_average = {}
  try:
    stock_table = pdr.DataReader(ticker, 'yahoo',datetime.date(int(start_year),int(start_month),int(start_day)),datetime.date.today())
    #time.sleep(7)
    #date_vec = stock_table['Date']
    closing_price_vec = []
    volume_vec = [] 
    for i in stock_table['Close']:
          closing_price_vec.append(i)
    for j in stock_table['Volume']:
          volume_vec.append(j)

    """
        calculate 20 days average price and we have reverse sequence
    """
    number_10day = len(closing_price_vec)-10
    reverse_closing_vec = closing_price_vec[::-1]
    tenday_closing_vec = []
    for i in range(0, len(reverse_closing_vec)-11):
          tmp = sum(reverse_closing_vec[i:i+10]) / 10
          tenday_closing_vec.append(tmp)
    
    

    """ 
        calculate 5 days 
    """
    fiveday_closing_vec = []
    number_5day = len(closing_price_vec)-5
    for i in range(0, len(reverse_closing_vec)-6):
          tmp = sum(reverse_closing_vec[i:i+5]) / 5
          fiveday_closing_vec.append(tmp)

    """

        check whether 5 days moving average is above 10 days average 

    """
    check_MovingAverage = check_five_and_ten_days_moving_average(fiveday_closing_vec, tenday_closing_vec)
    return check_MovingAverage
  except:
    pass

def moving_average_greater_volumn(shanghai_company_codes, shenzhen_company_codes):
## find the shanghai company list and go through models 
  collection_vec = []
  write_to_txt = open("tmp_collection_company.txt",'a+')

  for i in range(1,len(shanghai_company_codes)):
    temp_ticker = shanghai_company_codes[i] + ".ss"
    #print(temp_ticker)
    tmp_result = moving_average_greater_volumn_model(temp_ticker,'11/01/2020','12/14/2020')
    #time.sleep(20)
    if(tmp_result is True):
      collection_vec.append(temp_ticker+"\n")
      print("%s meet the requirement" %(temp_ticker))
      write_to_txt.write(temp_ticker+"\n")

  for j in range(1,len(shenzhen_company_codes)):
    temp_ticker = shenzhen_company_codes[j] + ".sz"
    #print(temp_ticker)
    tmp_result = moving_average_greater_volumn_model(temp_ticker,'11/01/2020','12/14/2020')
    write_to_txt = open("tmp_collection_company.txt",'a')
    #time.sleep(20)
    if(tmp_result is True):
      collection_vec.append(temp_ticker+"\n")
      print("%s meet the requirement" %(temp_ticker))
      write_to_txt.write(temp_ticker+"\n")

  write_to_txt.close()
  return collection_vec



#we only calculate latest 6 days volumn and prices data for model!
def find_recent_abnormal_model(ticker):
  current_time = datetime.date.today()
  start_year = current_time +  datetime.timedelta(days=-7)
  try:
    stock_table = pdr.DataReader(ticker, 'yahoo',start_year,datetime.date.today())
    closing_price_vec = []
    volume_vec = [] 
    for i in stock_table['Close']:
          closing_price_vec.append(i)
    for j in stock_table['Volume']:
          volume_vec.append(j)
    
    #calculate the stock price whether there is a upward trend 
    price_upward_trend = False
    volumn_upward_trend = False 
    price_count = 0 
    volumn_count = 0 

    for i in range(1,len(closing_price_vec)):
          if closing_price_vec[i-1] <= closing_price_vec[i]:
                price_count +=1 
    
    for i in range(1,len(volume_vec)):
          if volume_vec[i-1] <= volume_vec[i]:
                volumn_count +=1
    if volumn_count > 3:
          volumn_upward_trend = True
    if price_count > 3:
          price_upward_trend = True 

    return volumn_upward_trend and price_upward_trend
  except:
    pass



#find recent five days abnormal stock prices 
def find_recent_abnormal_SHH(shanghai_company_codes):
  ## find the shanghai company list and go through models 
  collection_vec = []
  write_to_txt = open("tmp_collection_company_SHH.txt",'a+')

  for i in range(1,len(shanghai_company_codes)):
    temp_ticker = shanghai_company_codes[i] + ".ss"
    print(temp_ticker)
    tmp_result = find_recent_abnormal_model(temp_ticker)
    #time.sleep(20)
    if(tmp_result is True):
      collection_vec.append(temp_ticker+"\n")
      print("%s meet the requirement" %(temp_ticker))
      write_to_txt.write(temp_ticker+"\n")
  write_to_txt.close()
  return collection_vec

def find_recent_abnormal_SZ(shenzhen_company_codes):
  collection_vec = []
  write_to_txt = open("tmp_collection_company_SZ.txt",'a+')
  for j in range(1,len(shenzhen_company_codes)):
    #print(shenzhen_company_codes[j])
    if(shenzhen_company_codes[j]):
      temp_ticker = shenzhen_company_codes[j] + ".sz"
      print(temp_ticker)
      tmp_result = find_recent_abnormal_model(temp_ticker)
      
      #time.sleep(20)
      if(tmp_result is True):
        collection_vec.append(temp_ticker+"\n")
        print("%s meet the requirement" %(temp_ticker))
        write_to_txt.write(temp_ticker+"\n")  
  write_to_txt.close()
  return collection_vec
      
