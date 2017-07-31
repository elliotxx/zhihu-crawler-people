#coding=utf8
import redis
import pymongo
import re
from bs4 import BeautifulSoup as BS
import cookielib
import json
import time
import datetime
import logging
import logging.handlers
import threading
import os,random
import requests
import socket
import sys
from multiprocessing import Pool
from common import *

from Crawler import Crawler
from ProxyIP import ProxyIP

# 实例化代理池对象，全局使用，最多实例化进程个数次，防止冗余的实例化
proxyip = ProxyIP()


def Init():
	# 初始化：数据库、socket 超时时间
	# 连接 mongo 数据库
	mongo_client = pymongo.MongoClient(mongo_host,mongo_port)

	# 切换 mongo 数据库
	mongo_db = mongo_client.zhihu_crawler

	# 获取 mongo 数据库中的 peoples 集合
	mongo_peoples = mongo_db.peoples

	# 连接 redis 数据库
	redis_client = redis.Redis(host=redis_host,port=redis_port,db=0)

	# 设置 socket 超时时间
	socket.setdefaulttimeout(socket_timeout)

	return mongo_peoples , redis_client


def start():
	'''抓取进程开始，每次取出一个节点抓取 '''
	# 初始化
	mongo_peoples , redis_client = Init()

	# 待抓取节点集合是否为空
	while redis_client.scard(waiting_set) == 0: # 为空
		# 等待 waiting_size 秒
		time.sleep(wait_time)

	# 从待抓取节点集合随机（右端）取出一个节点
	node = redis_client.spop(waiting_set)
	urlToken = node

	# 抓取节点代表用户的个人信息
	# printx('准备代理……')
	printx('正在抓取用户 %s 的个人信息……'%urlToken)
	try_cnt = try_limit
	while try_cnt > 0:
		try:
			c = Crawler(isCookie=False,timeout=socket_timeout)
			# 手动设置代理IP
			ip = proxyip.get()
			c.set_proxyip(ip)

			people = get_Info(c,urlToken)
			if people==None:
				raise Exception,'抓取的用户信息为空'
		except Exception,e:
			try_cnt -= 1
			print e
			printx('用户 %s 个人信息抓取出错，还可以尝试抓取 %d 次'%(urlToken,try_cnt))
		else:
			break

	# 用户个人信息抓取失败，将该节点放入抓取失败节点集合，结束进程
	if try_cnt <= 0:
		printx('该用户个人信息抓取失败，将该节点放入个人信息抓取失败节点集合，结束进程')
		printx('')
		redis_client.sadd(info_failed_set,node)
		return

	# 用户个人信息抓取成功
	# 将该用户个人信息插入到 mongodb 中
	printx('该用户个人信息抓取成功')
	printx('将该用户个人信息插入到 mongodb 中……')
	mongo_peoples.insert(people)

	printx('该用户个人信息抓取成功，将该节点放入个人信息抓取成功节点集合')
	redis_client.sadd(info_success_set,node)

	printx('目前待抓取节点集合中有 %d 人'%redis_client.scard(waiting_set))
	printx('目前个人信息抓取成功节点集合中有 %d 人'%redis_client.scard(info_success_set))
	printx('目前个人信息抓取失败节点集合中有 %d 人'%redis_client.scard(info_failed_set))

	printx('该用户个人信息抓取完毕')
	printx('')
	

def get_Info(c,urlToken):
	''' 获取某用户的个人信息'''
	url = '%s/people/%s/answers'%(host,urlToken)
	html = c.get_html(url)

	# 解析html
	printx('正在解析用户页面HTML……')
	s = BS(html,'html.parser')

	# 获得该用户藏在主页面中的json格式数据集
	data = s.find('div',attrs={'id':'data'})['data-state']
	data = json.loads(data)
	data = data['entities']['users'][urlToken]

	# 只抓取people类型用户
	if data['userType'] != 'people':
		raise Exception,'不是people类型用户，放弃该用户的抓取任务'

	# 从数据集中提取该用户必要的信息
	printx('正在提取用户信息……')
	try:
		people = get_peopleInfo(urlToken,data)
	except Exception,e:
		raise Exception,'提取用户信息的过程中出错\n错误原因：%s'%e

	return people

def get_peopleInfo(urlToken,data):
	# 从数据集中提取必要的用户信息
	people = { 'urlToken':urlToken }

	# 解析信息
	people['educations'] = '&&'.join(map( (lambda x:'%s%s%s'%( (x['school']['name'] if x.has_key('school') else '') , (',' if x.has_key('school') and x.has_key('major') else '') ,  (x['major']['name'] if x.has_key('major') else ''))),data['educations'])).strip().replace("'","\\'")
	people['followingCount'] = data['followingCount']     # 他关注的人数
	people['pinsCount'] = data['pinsCount']     # 他的分享数
	people['favoriteCount'] = data['favoriteCount']     # 他的收藏数
	people['voteupCount'] = data['voteupCount']       # 他获得的赞同数
	people['followingColumnsCount'] = data['followingColumnsCount'] # 关注的专栏个数
	people['headline'] = data['headline'].replace("'","\\'")     # 一句话描述 brief
	people['participatedLiveCount'] = data['participatedLiveCount'] # 赞助过的live
	people['followingFavlistsCount'] = data['followingFavlistsCount'] # 关注的收藏夹
	people['favoritedCount'] = data['favoritedCount']  # 获得多少次收藏
	people['followerCount'] = data['followerCount']   # 关注他的人数
	people['employments'] = '&&'.join(map( (lambda x:'%s%s%s'%( (x['company']['name'] if x.has_key('company') else '') , (',' if x.has_key('company') and x.has_key('job') else '') , (x['job']['name'] if x.has_key('job') else ''))),data['employments'])).strip().replace("'","\\'")
	people['markedAnswersCount'] = data['markedAnswersCount']     # 知乎收录了多少个回答
	people['avatarUrlTemplate'] = data['avatarUrlTemplate'].replace('{size}','xl')   # 头像临时链接
	people['followingTopicCount'] = data['followingTopicCount']   # 关注的话题数量
	people['description'] = data['description'].replace("'","\\'")       # 个人简介
	if hasattr(data,'business'):
		people['business'] = data['business']['name'].replace("'","\\'")     # 所在行业
	else:
		people['business'] = ''
	people['hostedLiveCount'] = data['hostedLiveCount']   # 主持的live数量
	people['answerCount'] = data['answerCount']   # 回答的数量
	people['articlesCount'] = data['articlesCount']   # 发表的文章数量
	people['name'] = data['name']     # 昵称
	people['questionCount'] = data['questionCount']   # 提了多少个问题
	people['locations'] = '&&'.join(map(lambda x:x['name'] ,data['locations'])).strip().replace("'","\\'")
	people['logsCount'] = data['logsCount']   # 参与过多少次公共编辑
	people['followingQuestionCount'] = data['followingQuestionCount']     # 关注的问题数量
	people['thankedCount'] = data['thankedCount']     # 收到的感谢数量
	people['gender'] = data['gender']         # 性别

	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")     #  当前时间
	people['addtime'] = now
	people['uptime'] = now

	return people

def main():
	'''主函数'''
	# 设置最大多少次就更新代理池
	max_cnt = 30000
	start_cnt = 0
	while True:
		start_cnt += 1
		if start_cnt < max_cnt:
			start()
		else:
			proxyip.update_pool()
			start_cnt = 0
	

if __name__ == '__main__':
	# while True:
	#    start()

	pool = Pool(processes = info_max_process_num)
	for i in range(info_max_process_num):
		printx('个人信息抓取进程 %d 启动'%(i+1))
		pool.apply_async(main,())
	# 关闭进程池，使其不再接受请求
	pool.close()
	# 等待所有进程请求执行完毕
	pool.join()

