from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.loader import ItemLoader
from douban_redis.items import BookItem,MyItemLoader
from urllib.parse import unquote
import os,re
from scrapy.http import Request


class DoubanBook(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'booksSpider1'
    redis_key = 'books:start_urls'
    # add allowed_domains if not ,it throw 'filtered offsite ...'
    allowed_domains = ['book.douban.com']
    rules = (
        # follow all links
        Rule(LinkExtractor(allow=r'/tag/\?view=type&icn=index-sorttags-all'),process_request='process_request',
            callback='book_tags',follow=False),
        # Rule(LinkExtractor(restrict_xpaths="//div[@class='article']/span[@class='next']"),
        #     process_request='process_request',callback='parse_start_url',follow=False),
    )

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(DoubanBook, self).__init__(*args, **kwargs)

    # use in Rule(process_request), but dont add argument 'spider'
    def process_request(self,request):
        request.dont_filter = True
        # request.cookies = get_cookie()
        return request

    @staticmethod
    def push_next_url(key,url):
        # print('headers :{0}'.format(response.headers))
        # print("use push_next_url()")
        cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush "+key+" "+str(url)
        r = os.popen(cmd)
        print("add new url : ",url)
        return r
    
    def book_tags(self,response):
        print("use push_urls()")
        # print('push book urls')
        # print('cookie :{0}'.format(response.request.headers.getlist('Cookie')))
        linksEx = LinkExtractor(allow_domains='book.douban.com',allow='/tag/[\u4e00-\u9fa5]{2,}')
        links = linksEx.extract_links(response)
        for link in links:
            cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush "+self.redis_key+" "+str(link.url)
            r = os.popen(cmd)
            if r.read():
                print('pushed url :{0} '.format(link.url))
        
        return {'PROCESS':'YES'}
    

    # if overwrite parse() ,rules request would failed 
    def parse_start_url(self,response):
        pattern = '/tag/[\u4e00-\u9fa5]{2,}'
        url = unquote(response.url)
        r_tag = re.search(pattern,url)
        r_subject = re.search('/subject/[0-9]+',url)

        print("starting parse page")
        # print('headers :{0}'.format(response.headers))
        # print(response.url) 
        if r_tag is not None:
            cur_linksEx = LinkExtractor(allow_domains='book.douban.com',
                restrict_xpaths ="//div[@id='subject_list']/ul[@class='subject-list']/li[@class='subject-item']/div[@class='info']/h2")
            
            next_linksEx = LinkExtractor(allow_domains='book.douban.com',
                        restrict_xpaths="//div[@class='paginator']/span[@class='next']")
            
            next_link = next_linksEx.extract_links(response)
            if len(next_link) > 0:
                self.push_next_url(self.redis_key,next_link[0].url)
            # print("next link:{0}".format(nextlink))
            # self.push_next_url(self.redis_key,next_link)
            # print(len(cur_linksEx))
            cur_links = cur_linksEx.extract_links(response)

            for link in cur_links:
                # print(str(link.url))
                self.push_next_url(self.redis_key,str(link.url))
            return {'PROCESS':'gg'}
        elif r_subject is not None:
            return self.parse_book_infos(response)
        else:
            print(response.url)
            return {'PROCESS':'YES'}



    def parse_book_infos(self,response):
        info_filed = {'作者':'author','出版社':'publishing','原作名':'original',
                      '译者':'translator','出版年':'date','页数':'pages',
                      '定价':'price','丛书':'series','ISBN':'ISBN'}

        texts = response.css("div#info ::text")
        
        text_infos = []
        for i,text in enumerate(texts):
            t = texts[i].extract().strip("\n ").strip("\xa0")
            t = t.replace("\n","").replace(" ","")
            if t != "" and t != ":":
                text_infos.append(t.replace(':',''))


        loader = MyItemLoader(selector=response)
        if len(text_infos) == 0:
            self.push_next_url(self.redis_key,unquote(response.url))
            return {'PROCESS':'invalid item'}

        for key in info_filed.keys():
            try:
                index = text_infos.index(key)
                
            except ValueError as e:
                loader.add_value(info_filed[key],'unknow')
            else:
                loader.add_value(info_filed[key],text_infos[index+1])
        loader.add_css('rating',"div.rating_self strong.rating_num ::text")
        loader.add_value('rating','0.0')
        loader.add_css('comments',"div.rating_sum span a.rating_people span ::text")
        loader.add_value('comments','0')
        loader.add_css('book_name',"div#wrapper h1 span ::text")
        loader.add_value('book_name','no name')
        loader.add_css('tag',"div#db-tags-section div.indent span a ::text")
        loader.add_value('tag','no tag')
        return loader.load_item()
