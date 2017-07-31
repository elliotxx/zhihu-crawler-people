## zhihu_crawler_windows

一个简单的分布式知乎爬虫，抓取知乎用户个人信息。

使用该爬虫做的数据分析：[大数据报告：知乎百万用户分析](http://yangyingming.com/article/389/)

该分布式爬虫的源码解析：[如何写一个简单的分布式知乎爬虫？](http://www.yangyingming.com/article/392/)

### 依赖
* BeautifulSoup
* pymongo
* redis
* requests

### 分布式爬虫架构

redis 中设置五个集合：**待抓取节点集合** 和 **个人信息抓取成功节点集合** 和 **个人信息抓取失败节点集合** 和 **列表抓取成功节点集合** 和 **列表抓取失败节点集合**。

它们在 Redis 中分别命名为 **waiting / info\_success / info\_failed / list\_success / list\_failed**。

它们的关系为：
![](http://www.yangyingming.com/uploads/markdownx/2017/7/c4595153-977e-4ee0-b5a7-217c31157ce2.png)

**个人信息抓取进程** 从 待抓取节点集合 中随机取出一个节点，抓取该节点代表的用户信息。如果抓取成功，加入 个人信息抓取成功节点集合，如果抓取失败，加入 个人信息抓取失败节点集合。

**列表抓取进程** 从 个人信息抓取成功节点集合 中随机取出一个节点，抓取该节点的 follower 列表。如果抓取成功，加入 列表抓取成功节点集合，如果抓取失败，加入 列表抓取失败节点集合。

整个分布式架构采用 **主从结构**：主机维护的数据库，配合从机的 info_crawler 和 list_crawler 爬虫程序，便可以循环起来：info_crawler 不断从 waiting 集合中获取节点，抓取个人信息，存入数据库；list_crawler 不断的补充 waiting 集合。

主机和从机的关系如下图：
![](http://www.yangyingming.com/uploads/markdownx/2017/7/b08b1bc1-36a0-46a9-a844-3def95e249f1.png)

### 参考资料
Python操作redis（python client 操作）  
http://www.cnblogs.com/melonjiang/p/5342505.html

Redis集合（redis 控制台操作）  
http://www.yiibai.com/redis/redis_sets.html

Redis系列-存储篇set主要操作函数小结（redis 并集操作，可以将一个 set 数据移动到另一个 set）  
http://blog.csdn.net/love__coder/article/details/8497497

Redis数据备份与恢复  
http://www.cnblogs.com/qinghub/p/5909921.html

MongoDB入门（3）- MongoDB备份与恢复  
http://www.cnblogs.com/wardensky/p/5799276.html

MongoDB 如何修改数据库名称  
https://segmentfault.com/q/1010000000694527

