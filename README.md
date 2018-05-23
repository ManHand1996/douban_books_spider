### 豆瓣图书爬虫

Scrapy + redis + MySQL爬去douban图书8w条数据
模块:

- Scrapy
- redis
- MySQL
- pandas
- sqlalchemy
- MySQLdb
- CSV
#### 处理流程 

- 1.spider获取数据用ItemLoader提取保存至item
- 2.pipeline处理返回的item存储到redis
- 3.process_items.py提取redis的数据进行数据清洗保存到csv文件


##### getIP.py

```
获取代理接口的代理IP
```
##### process_item_mysql.py
为process_items.py提供数据清洗函数
- 
