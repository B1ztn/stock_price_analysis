import stock_models
import EastMoney_spider
from multiprocessing import Process, Pool
import time

if __name__ == '__main__':
    start = time.time()

    #pool = Pool(processes=4) 

    #  we update stock lists for both SHH and SZ 
    #stock_models.update_universal_company_list()
    #pool = Pool(processes=4) 

    # we shall collect related sotck info and data 
    #shanghai_exchange_company_codes, shenzhen_exchange_company_codes = stock_models.load_universal_company_data()


    #collection_vec = stock_models.moving_average_greater_volumn(shanghai_exchange_company_codes,shenzhen_exchange_company_codes)
    ##collection_vec_shh = stock_models.find_recent_abnormal_SHH(shanghai_exchange_company_codes)
    ##collection_vec_sz = stock_models.find_recent_abnormal_SZ(shenzhen_exchange_company_codes)

    ##collection_vec_shh = pool.apply_async(stock_models.find_recent_abnormal_SHH,kwargs = {'shanghai_company_codes':shanghai_exchange_company_codes})
    ##collection_vec_sz = pool.apply_async(stock_models.find_recent_abnormal_SZ,kwargs = {'shenzhen_company_codes':shenzhen_exchange_company_codes})
    """
    collection_vec_shh = pool.apply_async(stock_models.find_recent_abnormal_SHH,(shanghai_exchange_company_codes,))
    collection_vec_sz = pool.apply_async(stock_models.find_recent_abnormal_SZ,(shenzhen_exchange_company_codes,))
    pool.close()
    pool.join()
    print(f'multi-process time cost: {time.time() - start}s')

    collection_vec = []

    if len(collection_vec_shh.get())>0:
        collection_vec = collection_vec_shh.get()
    ##print(collection_vec)

    if(len(collection_vec_sz.get())>0):
        for j in collection_vec_sz.get():
            collection_vec.append(j)


    write_to_txt = open("collection_company.txt","w")
    for i in collection_vec:
        write_to_txt.write(i)

    write_to_txt.close()
"""
    #EastMoney_spider.output_blocktrade_EastMoney()
    EastMoney_spider.collect_shibor_rates()
    # def __init__(self, nowdate, volumn, price,amount,name,sell_side,buy_side, oneday_change_str, fiveday_change_str, tenday_change_str):


