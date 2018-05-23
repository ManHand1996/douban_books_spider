from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.loader import ItemLoader
from douban_redis.items import BookItem,MyItemLoader
from urllib.parse import unquote
import os
from scrapy.http import Request


class DoubanBook(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'master'
    redis_key = 'master:start_urls'
    # add allowed_domains if not ,it throw 'filtered offsite ...'
    allowed_domains = ['book.douban.com']
    rules = (
        # follow all links
        Rule(LinkExtractor(allow=r'/tag/\?view=type&icn=index-sorttags-all'),process_request='process_request',
            callback='push_urls',follow=False),
        # Rule(LinkExtractor(restrict_xpaths="//div[@class='paginator']/span[@class='next']"),
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
        print("use push_next_url()")
        cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush "+key+" "+str(url)
        r = os.popen(cmd)
        print("add new url result: ",r.read())
        return r
    
    def push_urls(self,response):
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
        # le = LinkExtractor(allow=r'/tag/\?view=type&icn=index-sorttags-all')
        # # print(str(len(le.extract_links(response)))+"haha")
        # for link in le.extract_links(response):
        #     print(link.url)

        print("starting parse page")
        # print('headers :{0}'.format(response.headers))
        # print(response.url)
        if response.url == 'https://book.douban.com':
            print(response.url)
            return {'PROCESS':'YES'}
        

        else:
            linksEx = LinkExtractor(allow_domains='book.douban.com',
                restrict_xpaths="//div[@class='paginator']/span[@class='next']")
            nextlink = linksEx.extract_links(response)[0].url
            # print("next link:{0}".format(nextlink))
            self.push_next_url(self.redis_key,nextlink)
            selectors = response.css('div#subject_list ul.subject-list li.subject-item')
            # print("current link:{0}".format(response.url))
            for selector in selectors:
                tag = unquote(response.url.split('?')[0].split('/')[-1])
                l = MyItemLoader(selector=selector)
                l.add_css('book_name','div.info h2 a::text')
                l.add_css('book_info','div.info div.pub')
                l.add_css('rating','div.info div.star span.rating_nums')
                l.add_css('comments','div.info div.star span.pl')
                l.add_value('tag',tag)
                book_info_item = l.load_item()
                yield book_info_item
            return {'PROCESS':'YES'}