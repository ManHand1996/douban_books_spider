import requests
import os
import time
def getIP():
	r = requests.get('http://tvp.daxiangdaili.com/ip/?tid=555423920612930&protocol=http&num=5&category=2')
	rtxt = r.text
	ipList = rtxt.split('\r\n')
	return ipList

def addToRedisList(proxyList):
	for proxy in proxyList:
		cmd = "/usr/local/redis/bin/redis-cli -a 'redispassword' lpush proxy:ip "+proxy
		os.popen(cmd)

def getProxy():
	time.sleep(2)
	proxies = getIP()
	proxyList = []
	for proxy in proxies:
		try:
			r = requests.get('https://www.baidu.com',proxies={'http':proxy})
		except Exception as e:
			print('give ip %s'%proxy)
		else:
			if r.status_code == 200:
				proxyList.append(proxy)
				print('add ip %s'%proxy)
	if len(proxyList) > 0:
		# addToRedisList(proxyList)
		return proxyList
	else:
		return getProxy()


