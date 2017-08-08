#coding=utf8
# 使用该模块必须首先启动 IPProxyPool 代理池

import requests
import random

class ProxyIP():
	host = 'http://your_proxy_pool_ip:8000'					# 代理池请求IP
	ip_pool = []										# 代理池 

	def __init__(self):
		'''初始化函数'''
		# 初始化代理池
		print 'Init proxy pool !!!!!!!!!!!!!!!!!!!'
		self.update_pool()

	def get(self,protocol = -1):
		'''
		从代理池获取代理IP，默认获取一个
		参数：
		protocol= 0,1,2 分别代表协议 http、https、http/https都可
		if protocol == -1,无所谓协议
		'''	
		# 超出界限，或者代理池为空，更新代理池
		if len(self.ip_pool)==0:
			print 'proxy pool is NULL, update proxy pool !!!!!!!!'
			self.update_pool(protocol)

		# 从代理池随机返回一个 ip
		size = len(self.ip_pool)
		idx = int(random.random()*size)
		return self.ip_pool[idx]

	def update_pool(self,protocol = -1):
		'''更新代理池'''
		print 'Update proxy pool !!!!!!!!!'
		params = {
			# 'count':count,
		}
		if protocol != -1:
			params['protocol'] = protocol
		response = requests.get(self.host,params=params,timeout=10)
		self.ip_pool = eval(response.content)


	def delete(self,ip):
		'''
		从代理池中删除一个ip
		'''
		url = '%s/delete'%self.host
		params = {
			'ip':ip[0]
		}
		response = requests.get(url,params=params,timeout=10)
		return response.content

	def sum(self):
		response = requests.get(self.host)
		ips = eval(response.content)
		return len(ips)


if __name__=="__main__":
	print ProxyIP().sum()
