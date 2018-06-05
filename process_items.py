# #!/usr/bin/env python

# -*- coding: utf-8 -*-

import redis
import csv
import os
import MySQLdb
from sqlalchemy import create_engine
from process_item_mysql import checkBookInfo,to_mysql,clean_data

DATA_FILE_PATH = os.path.join("./Data","douban-books.csv")
NEW_DATA_FILE_PATH = os.path.join("./Data","douban-books_clean.csv")


def purgeItems(data,file_name):

    with open(file_name,'a') as csvFile:
        csv_writer = csv.writer(csvFile)
        # if not data.get('book_info') or not data.get('book_name'):
        #     return
        # if not data.get('rating'):
        #     data['rating'] = '0.0'

        infos = checkBookInfo(data)
        if len(infos) == 0:
            return
        full_data = []
        full_data.append(infos['ISBN'])
        full_data.append(infos['book_name'])
        full_data.append(infos['author'])
        full_data.append(infos['price'])
        full_data.append(infos['comments'])
        full_data.append(infos['rating'])
        full_data.append(infos['tag'])
        full_data.append(infos['original'])
        full_data.append(infos['translator'])
        full_data.append(infos['publishing'])
        full_data.append(infos['date'])
        full_data.append(infos['pages'])
        full_data.append(infos['series'])

        csv_writer.writerow(full_data)


def purgeItems2(data,file_name):
    
    with open(file_name,'a') as csvFile:
        csv_writer = csv.writer(csvFile)
        full_data = []
        if data['book_name'] == "no name":
            return
        for item in data.keys():
            full_data.append(data[item])
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
        csv_writer.writerow(['ISBN','Bookname','Author','Price','Comments',
                            'Rating','Tag','Original','Translator',
                            'Publishing','Date','Pages','Series',
                            ])
    for key in keys:

        for item in rd.lrange(key,0,-1):
            purgeItems(eval(item),file_name)

if __name__ == '__main__':
    process_items('127.0.0.1',6379,'redispassword',0,['booksSpider1:items','booksSpider2:items','booksSpider3:items'])
    # mysql_engine = create_engine('mysql+mysqldb://root:manhand@localhost:3306/douban_books_db?charset=utf8')
    # clean_data(DATA_FILE_PATH,NEW_DATA_FILE_PATH)