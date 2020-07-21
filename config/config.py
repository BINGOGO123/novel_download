from .Redis import Redis

SUCCESS = 0
ERROR = 1

redis_connect = Redis()

# 定义一次返回的条数
once_return_count = 20

# 存储下载进度的redis表名
download_process = "novel_download_process"

# 最多同时开启的爬虫数目
spider_max_count = 30

# 存储当前爬虫数量的redis表名
name_novel_download_spider_count = "novel_download_spider_count"