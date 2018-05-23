import random
import base64
import redis
from douban_redis.getIP import getProxy
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import os
from douban_redis import settings
# def get_cookie():
#     with open('/home/manhand/Downloads/scrapy-redis/example-project/example/spiders/cookies.txt','r') as f:
#         cookieStr = f.read()
#         cookieList = cookieStr.split(';')
#         cookies = {}
#         for cookie in cookieList:
#             temp = cookie.split('=')
#             name, value = temp[0].strip(' '), temp[1].strip('"')
#             cookies[name] = value
#         return cookies

class RandomUserAgent(object):

    def __init__(self,agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self,request,spider):

        request.headers.setdefault('User-Agent',random.choice(self.agents))
        request.headers.setdefault('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        request.headers.setdefault('Accept-Encoding','gzip,deflate,br')
        # request.cookies = get_cookie()
        request.headers.setdefault('Accept-Language','en-US,en;q=0.5')
        request.headers.setdefault('Host','book.douban.com')
        request.headers.setdefault('Connection','keep-alive')
        request.headers.setdefault('Upgrade-Insecure-Requests','1')


class ProxyMiddleware(object):
    
    # def __init__(self,ip):
    #     self.ip = ip

    def process_request(self,request,spider):

        if len(settings.PROXIES) == 0:
            settings.PROXIES = getProxy()
        ip_port = random.choice(settings.PROXIES)
        request.meta['proxy'] = "http://"+ip_port
        print('current proxy: %s'%request.meta['proxy'])
        print(settings.PROXIES)
    
    def process_response(self,request,response,spider):
        if str(response.url).find("https://sec.douban.com/") >= 0:
            raise IgnoreRequest
        print('precess_response -> proxy:%s'%request.meta['proxy'])
        if response.status == 200:
            
            return response
        else:
            try:
                if settings.PROXIES.index(request.meta['proxy'].strip('http://')) >= 0:
                    settings.PROXIES.remove(request.meta['proxy'].strip('http://'))
            except Exception as e:
                pass
            print('pop :%s'%request.meta['proxy'].strip('http://'))
            cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush "+'master:start_urls'+" "+request.url
            os.popen(cmd)
            print('response proxy fail -> readd: %s'%request.url)
            raise IgnoreRequest

    def process_exception(self,request,exception,spider):
        if str(request.url).find("https://sec.douban.com/") >= 0:
            return 
        print('proxy fail connect')
        print(request.meta['proxy'])
        print(settings.PROXIES)
        # settings.PROXIES.remove(request.meta['proxy'].strip('http://'))
        try:
            if settings.PROXIES.index(request.meta['proxy'].strip('http://')) >= 0:
                settings.PROXIES.remove(request.meta['proxy'].strip('http://'))
                print("current proxies:{0}".format(settings.PROXIES))
        except Exception as e:
            pass
        cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush "+'master:start_urls'+" "+request.url
        os.popen(cmd)
        print('exception proxy fail -> readd: %s'%request.url)
        raise IgnoreRequest
        return

class MyRetryMiddleware(RetryMiddleware):

    def _retry(self, request, reason, spider):
        try:
            if settings.PROXIES.index(request.meta['proxy'].strip('http://')) >= 0:
                settings.PROXIES.remove(request.meta['proxy'].strip('http://'))
        except Exception as e:
            pass
        print('pop :%s'%request.meta['proxy'].strip('http://'))

        if len(settings.PROXIES) >= 1 :
            settings.PROXIES = getProxy()
        request.meta['proxy'] = 'http://'+random.choice(settings.PROXIES)
        super(MyRetryMiddleware,self)._retry(request, reason, spider)
        if request.meta['retry_times'] >= settings.RETRY_TIMES:
            
            cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush "+'master:start_urls'+" "+request.url
            os.popen(cmd)
            print('end retry :add %s'%request.url)