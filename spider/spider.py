from .module.Downloader import Downloader
from config.config import redis_connect
from config.logger import logger_spider

__max_count = 30
__name_novel_download_spider_count = "novel_download_spider_count"

# 加redis数据库的操作数目，同时最多只能有__max_count组爬虫
def operate_spider_count(count):
  connect = redis_connect.getConnect()
  value = connect.get(__name_novel_download_spider_count)
  if value == None:
    if count < 0:
      logger_spider.error("operate_spider_count novel_download_spider_count=None operate_count={}".format(count))
      count = 0
    elif count > __max_count:
      logger_spider.error("operate_spider_count novel_download_spider_count=None operate_count={} __max_count={}".format(count,__max_count))
      count = __max_count
    connect.set(__name_novel_download_spider_count,str(count))
  else:
    value = int(value)
    new_value = value + count
    if new_value > __max_count:
      return False
    elif new_value < 0:
      logger_spider.error("operate_spider_count new_value小于0 value={} count={} new_value={}".format(value,count,new_value))
      new_value = 0
    connect.set("novel_download_spider_count",str(new_value))
  return True

# 搜索目录，names是str或者list，例如：
# "三国演义"
# ["三国演义","水浒传"]
def search_novel(names):
  # 如果下载已经满了，那么就算了
  if not operate_spider_count(1):
    return False,"当前爬虫队列已满"
  downloader = Downloader()
  content = downloader.download_catalog(names)
  # 返回之前需要减回来
  operate_spider_count(-1)
  return content

def download_novel(url):
  # 如果下载已经满了，那么就算了
  if not operate_spider_count(1):
    return False,"当前爬虫队列已满"
  downloader = Downloader()
  content = downloader.download_novel(url)
  # 返回之前需要减回来
  operate_spider_count(-1)
  return content
