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
import MySQLdb
from sqlalchemy import create_engine
from process_item_mysql import checkBookInfo,to_mysql

DATA_FILE_PATH = os.path.join("./Data","douban-books.csv")
NEW_DATA_FILE_PATH = os.path.join("./Data","douban-books_clean.csv")

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
        for t in data['book_info'].split('/'):
            if t == "unknow":
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

    file_name = os.path.join(DATA_FILE_PATH)
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
    # mysql_engine = create_engine('mysql+mysqldb://root:manhand@localhost:3306/douban_books_db?charset=utf8')
    # to_mysql(mysql_engine,DATA_FILE_PATH,NEW_DATA_FILE_PATH)