#coding=utf8
import urllib,urllib2
import ProxyIP
import socket
from common import printx

class Crawler:
	timeout = 15    # 超时时间默认设置为10秒
	cur_proxy_ip = ['','']     # 当前代理ip
	#headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'  }   # 头部伪装
	headers = {
		#'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
		'Host': 'www.zhihu.com'
	}   # 头部伪装
	myopener = urllib2.build_opener()       # 自定义opener

	def __init__(self,isCookie=False,login_url=None,postdata=None,timeout=None):
		if timeout != None:
			self.set_timeout(timeout)
		# 使用cookie需要 import cookielib
		if isCookie:
			# 模拟登陆，将登陆的cookie信息保存在新的opener中
			try:
				# 创建cookie处理器
				handler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
				#handler2 = urllib2.ProxyHandler({'http':'117.90.4.204:9000'})
				# 创建新的opener
				self.myopener = urllib2.build_opener(handler)
				#self.myopener = urllib2.build_opener(handler,handler2)
				# 登陆信息
				postdata = urllib.urlencode(postdata)
				request = urllib2.Request(login_url,data=postdata,headers=self.headers)
				# 验证登陆，保存cookie信息
				response = self.myopener.open(request,timeout=self.timeout)
				#print response.read()
			except Exception,e:
				raise Exception,'[ERROR] 验证登陆错误，初始化cookie失败！\n%s'%e
		else:
			# # 获得代理
			# ip = ProxyIP.get()
			# # 设置代理
			# self.set_proxyip(ip)
			pass

	def set_timeout(self,timeout):
		# 设置超时时间
		self.timeout = timeout
		socket.setdefaulttimeout(self.timeout)

	def set_proxyip(self,ip):
		# 设置代理ip
		printx('设置抓取器的代理IP：%s'%ip[0])
		handler = urllib2.ProxyHandler({'https':'%s:%d'%(ip[0],ip[1])})
		# 创建新的opener
		self.myopener = urllib2.build_opener(handler)
		# 更新当前代理ip
		self.cur_proxy_ip = ip

	def reset_proxyip(self):
		# 获取新代理
		ip = ProxyIP.get()
		printx('换代理: %s ---> %s'%(self.cur_proxy_ip[0],ip[0]))
		# 设置代理IP
		self.set_proxyip(ip)

	def get_html(self,url,postdata=None):
		# 获取指定url的html源码
		# 登陆信息
		if postdata:
			postdata = urllib.urlencode(postdata)
			request = urllib2.Request(url,data=postdata,headers=self.headers)
		else:
			request = urllib2.Request(url,headers=self.headers)
		# 请求
		response = self.myopener.open(request,timeout=self.timeout)
		return response.read()



