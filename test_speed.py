#coding=utf8
import pymongo
import redis
import time
from common import *

time_inteval = 60		# 每隔多久测一次速度，单位为秒

def Init():
	# 初始化：数据库
	# 连接 mongo 数据库
	mongo_client = pymongo.MongoClient(mongo_host,mongo_port)
	# 连接 mongo 数据库（使用用户名密码）
	# mongo_client = pymongo.MongoClient('mongodb://%s:%s@%s:%d'%(mongo_user,mongo_pwd,mongo_host,mongo_port))

	# 切换 mongo 数据库
	mongo_db = mongo_client.zhihu_crawler

	# 获取 mongo 数据库中的 peoples 集合
	mongo_peoples = mongo_db.peoples

	# 连接 redis 数据库
	redis_client = redis.Redis(host=redis_host,port=redis_port,db=0)
	# 连接 redis 数据库（使用访问密码）
	# redis_client = redis.Redis(host=redis_host,port=redis_port,password=redis_pwd,db=0)

	return mongo_peoples , redis_client

def test_speed(mongo_peoples,redis_client):
	'''个人信息抓取成功节点测速'''
	pre_num_1 = redis_client.scard(info_success_set)
	pre_num_2 = redis_client.scard(info_failed_set)
	pre_num_3 = redis_client.scard(list_success_set)
	pre_num_4 = redis_client.scard(list_failed_set)
	pre_num_5 = redis_client.scard(waiting_set)
	pre_num_6 = mongo_peoples.count()
	
	time.sleep(time_inteval)
	
	later_num_1 = redis_client.scard(info_success_set)
	later_num_2 = redis_client.scard(info_failed_set)
	later_num_3 = redis_client.scard(list_success_set)
	later_num_4 = redis_client.scard(list_failed_set)
	later_num_5 = redis_client.scard(waiting_set)
	later_num_6 = mongo_peoples.count()
	
	cur_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	printx('[cur_time] %s'%cur_time )
	printx('info_success_speed : %f p/s\tcurent info_success : %d'%( float(later_num_1-pre_num_1)/time_inteval , later_num_1 )  )
	printx('info_failed_speed : %f p/s\tcurent info_failed : %d'%( float(later_num_2-pre_num_2)/time_inteval , later_num_2 )  )
	printx('list_success_speed : %f p/s\tcurent list_success : %d'%( float(later_num_3-pre_num_3)/time_inteval , later_num_3 ) )
	printx('list_failed_speed : %f p/s\tcurent list_failed : %d'%( float(later_num_4-pre_num_4)/time_inteval , later_num_4 ) )
	printx('waiting_speed : %f p/s\tcurent waiting : %d'%( float(later_num_5-pre_num_5)/time_inteval , later_num_5 ) )
	printx('peoples_speed : %f p/s\tcurent peoples : %d'%( float(later_num_6-pre_num_6)/time_inteval , later_num_6 ) )

	printx('')


def main():
	'''主函数'''
	mongo_peoples , redis_client = Init()
	printx('开始测试抓取速度（每 %d 秒测试一次）'%time_inteval)

	while True:
		test_speed(mongo_peoples,redis_client)

if __name__ == '__main__':
	main()
