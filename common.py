#coding=utf8
import sys

# 通用设置
wait_time = 5               		# 进程等待时间
socket_timeout = 15          		# socket 请求超时时间
try_limit = 10              		# 尝试次数
per_page = 20               		# 关注页面每页显示的最大用户数量
list_max_process_num = 10        	# 关注列表抓取进程最大进程数
info_max_process_num = 50        	# 个人信息抓取进程最大进程数
waiting_set = 'waiting'     		# 待抓取节点集合
info_success_set = 'info_success' 	# 个人信息抓取成功节点集合
info_failed_set  = 'info_failed'    # 个人信息抓取失败节点集合
list_success_set = 'list_success'   # 列表抓取成功节点集合
list_failed_set  = 'list_failed'    # 列表抓取失败节点集合
host = 'https://www.zhihu.com'		# 主页面

# 数据库设置
redis_host = 'your_ip'				# redis 主机地址
redis_port = 6379					# redis 主机端口
# redis_pwd  = 'your_password'		# redis 访问密码
mongo_host = 'your_ip'				# mongodb 主机地址
mongo_port = 27017					# mongodb 主机端口
# mongo_user = 'your_user'			# mongodb 登陆用户
# mongo_pwd  = 'your_password'		# mongodb 用户密码


def printx(s):
	'''自定义输出函数：编码 + 标准输出'''
	s = s.decode('utf8')
	sys.stdout.write(s + '\n')

