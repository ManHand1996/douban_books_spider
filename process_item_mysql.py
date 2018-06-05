import re
import pandas


DictCurrency = {"$":6.38,"CNY": 1.0,"GBP":8.574, "HKD":0.8,"USD":6.38, "CAD":5.0 ,
            "JPY":0.058,"RMB":1.0, "EUR":7.52, "AUD":4.83,"CDN":5, "NT$":0.21,
            " $":6.38, "£ ":8.574,"日元":0.058,"NTD":0.21,"NT":0.21,"元":1.0}

def to_mysql(mysql_engine,DATA_FILE_PATH,NEW_DATA_FILE_PATH):
    books_data = pandas.read_csv(DATA_FILE_PATH,skiprows=[0,],
        names =['Bookname','Comments','Rating','Tag',
                'Author','Translator','Publishing',
                'Date','Price'
                    ]
                )
    
    books_data['Date'] = pandas.to_datetime(books_data['Date'],errors='coerce')
    books_data['Price'] = pandas.to_numeric(books_data['Price'],errors='coerce',downcast='float')
    
    books_data.to_csv(path_or_buf=NEW_DATA_FILE_PATH,index=False,float_format='%.3f',
        header=['Bookname','Comments','Rating','Tag','Author','Translator','Publishing','Date','Price'])    
    books_data = pandas.read_csv(NEW_DATA_FILE_PATH,skiprows=[0,],names =['Bookname','Comments','Rating','Tag'
                                                    ,'Author','Translator','Publishing','Date','Price'])
    # books_data.index = range(1,len(books_data)+1)
    # mysql_engine = create_engine('mysql+mysqldb://root:manhand@localhost:3306/douban_books_db?charset=utf8')

    # books_data.to_sql(name='douban_books_tb',if_exists='append',con=mysql_engine,index=True,index_label='num')

    # print("To MySQL...")
    # r = mysql_engine.execute("select count(num) from douban_books_tb")
    # print("books quantity:",r.first())

def clean_data(DATA_FILE_PATH,NEW_DATA_FILE_PATH):
    books_data = pandas.read_csv(DATA_FILE_PATH,skiprows=[0,],
        names =['Bookname','Comments','Rating','Tag',
                'Author','Translator','Publishing',
                'Date','Price'
                    ]
                )
    
    books_data['Date'] = pandas.to_datetime(books_data['Date'],errors='coerce')
    books_data['Price'] = pandas.to_numeric(books_data['Price'],errors='coerce',
                                            downcast='float')
    
    books_data.to_csv(path_or_buf=NEW_DATA_FILE_PATH,index=False,float_format='%.3f',
        header=['Bookname','Comments','Rating','Tag','Author',
                'Translator','Publishing','Date','Price']) 

    print("success ")

def trans_Price(info):
    if info == 'unknow':
        return 0.0

    info = info.replace("、",".")
    try:
        price = float(info)
    except ValueError as e:
        for key in DictCurrency:
            if info.find(key) >= 0:
                info = info.strip(key).strip(" ")
                try:
                    price = float(info)
                except ValueError as e:
                    return 0.0
                else:
                    return float(DictCurrency[key]*price)
        return 0.0
    else:
        return price

def isPublishing(info):
    if info.find('出版社') >= 0:
        return info
    else:
        return -1

def checkBookInfo(infos):

    # tag bookname :no tag no name
    # unknow
    if infos['ISBN'] == 'unknow' or infos['book_name'] == 'unknow':
        return {}

    infos['price'] = trans_Price(infos['price'])
    return infos