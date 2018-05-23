# #!/usr/bin/env python

# # -*- coding: utf-8 -*-
# """A script to process items from a redis queue."""
# from __future__ import print_function, unicode_literals

# import argparse
# import json
# import logging
# import pprint
# import sys
# import time

# from scrapy_redis import get_redis


# logger = logging.getLogger('process_items')


# def process_items(r, keys, timeout, limit=0, log_every=1000, wait=.1):
#     """Process items from a redis queue.

#     Parameters
#     ----------
#     r : Redis
#         Redis connection instance.
#     keys : list
#         List of keys to read the items from.
#     timeout: int
#         Read timeout.

#     """
#     limit = limit or float('inf')
#     processed = 0
#     while processed < limit:
#         # Change ``blpop`` to ``brpop`` to process as LIFO.
#         ret = r.blpop(keys, timeout)
#         # If data is found before the timeout then we consider we are done.
#         if ret is None:
#             time.sleep(wait)
#             continue

#         source, data = ret
#         try:
#             item = json.loads(data)
#         except Exception:
#             logger.exception("Failed to load item:\n%r", pprint.pformat(data))
#             continue

#         try:
#             name = item.get('name') or item.get('title')
#             url = item.get('url') or item.get('link')
#             logger.debug("[%s] Processing item: %s <%s>", source, name, url)
#         except KeyError:
#             logger.exception("[%s] Failed to process item:\n%r",
#                              source, pprint.pformat(item))
#             continue

#         processed += 1
#         if processed % log_every == 0:
#             logger.info("Processed %s items", processed)


# def main():
#     parser = argparse.ArgumentParser(description=__doc__)
#     parser.add_argument('key', help="Redis key where items are stored")
#     parser.add_argument('--host')
#     parser.add_argument('--port')
#     parser.add_argument('--timeout', type=int, default=5)
#     parser.add_argument('--limit', type=int, default=0)
#     parser.add_argument('--progress-every', type=int, default=100)
#     parser.add_argument('-v', '--verbose', action='store_true')

#     args = parser.parse_args()

#     params = {}
#     if args.host:
#         params['host'] = args.host
#     if args.port:
#         params['port'] = args.port

#     logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

#     r = get_redis(**params)
#     host = r.connection_pool.get_connection('info').host
#     logger.info("Waiting for items in '%s' (server: %s)", args.key, host)
#     kwargs = {
#         'keys': [args.key],
#         'timeout': args.timeout,
#         'limit': args.limit,
#         'log_every': args.progress_every,
#     }
#     try:
#         process_items(r, **kwargs)
#         retcode = 0  # ok
#     except KeyboardInterrupt:
#         retcode = 0  # ok
#     except Exception:
#         logger.exception("Unhandled exception")
#         retcode = 2

#     return retcode


# if __name__ == '__main__':
#     sys.exit(main())

import redis
import csv
import os
import re
import pandas
DATA_FILE_PATH = os.path.join(os.path.expanduser("~"),"Data","douban")
DictCurrency = {"$":6.38,"CNY": 1.0,"GBP":8.574, "HKD":0.8,"USD":6.38, "CAD":5.0 ,
            "JPY":0.058,"RMB":1.0, "EUR":7.52, "AUD":4.83,"CDN":5, "NT$":0.21,
            " $":6.38, "£ ":8.574,"日元":0.058,"NTD":0.21,"NT":0.21,"元":1.0}

def clearnData():
    books_data = os.path.join(os.path.expanduser('~'),'Data','douban','books_v2.csv')

def isPrice(info):
    try:
        price = float(info)
    except ValueError as e:
        for key in DictCurrency:
            if info.find(key) >= 0:
                info = info.strip(key).strip(" ")
                try:
                    price = float(info)
                except ValueError as e:
                    return -1
                else:
                    return float(DictCurrency[key]*price)
        return -1
    else:
        return price

def isPublishing(info):
    if info.find('出版社') >= 0:
        return info
    else:
        return -2

def checkBookInfo(infos):
    # check date and price
    tmp_infos = ['unknow' for i in range(5)]
    date_pattern = r"[0-9]{4}(-[0-9]{1,2})?(-[0-9]{1,2})?"

    print('current infos len:',len(infos))
    for i in range(0,len(infos)):

        price = isPrice(infos[i])
        r = re.search(date_pattern,infos[i])
        
        if price != -1 and r is None:
            # 兑换
            tmp_infos[4] = price
            continue
        elif r is not None and price == -1:
            tmp_infos[3] = r.group(0)
            continue

        elif price == -1 and r is None:
            if i != 3 and i !=4:
                tmp_infos[i] = infos[i]
            continue        
        else:
            continue
        # except ValueError as e:
        #     continue
             
    return tmp_infos

def purgeItems(data,file_name):
	
    with open(file_name,'a') as csvFile:
        csv_writer = csv.writer(csvFile)
        if not data.get('book_info') or not data.get('book_name'):
            return
        if not data.get('rating'):
            data['rating'] = '0.0'
        
        full_data = []
        full_data.append(data['book_name'])
        full_data.append(data['comments'])
        full_data.append(data['rating'])
        full_data.append(data['tag'])
        print('book name:',data['book_name'])
        count_unknow = 0
        for t in date['book_info'].split('/'):
            if t == "unknow"
                count_unknow += 1
        if count_unknow == 5:
            return 


        infos = [i.strip(' "') for i in data['book_info'].split(' / ')]
        print(infos)
        info_len = len(infos)
        if info_len > 5:
            infos = infos[:5]
        # info[0] book name,info[1] translator info[2] publishing info[3] date info[4] price
        if len(infos) > 0:
            new_infos = checkBookInfo(infos)
        else:
            return
        
        if len(new_infos) == 5:
            for info in new_infos:
                full_data.append(info)
        else:
            return
        if len(full_data) == 9:
            csv_writer.writerow(full_data)

def process_items(host,port,passwd,db,keys):
    """
	keys = []:redis keys
	"""
    rd = redis.Redis(host=host,port=port,password=passwd,db=db,decode_responses=True)

    file_name = os.path.join(DATA_FILE_PATH,'books.csv')
    print(file_name)
    # if file not exists ,create it
    if not os.path.exists(file_name):
        os.mknod(file_name)
    with open(file_name,'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['Bookname','Comments','Rating','Tag','Author','Translator','Publishing',
    'Date','Price'])
    for key in keys:

        for item in rd.lrange(key,0,-1):
            purgeItems(eval(item),file_name)

if __name__ == '__main__':
    process_items('127.0.0.1',6379,'redispassword',0,['master:items','salve1:items'])