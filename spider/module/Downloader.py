import requests
from bs4 import BeautifulSoup
from config.logger import logger_spider
from config.config import redis_connect
import ipdb
from config.config import SUCCESS,ERROR

class Downloader:
  __headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
  }
  __max_download_count = 5
  __timeout = 10
  def __init__(self):
    logger_spider.debug("Downloader")
    self.s = requests.Session()
    self.s.headers.update(self.__headers)
    self.connect = redis_connect.getConnect()

  # 根据搜索内容下载小说目录
  def download_catalog(self,names,filter="all"):
    logger_spider.debug("download_catalog names={} filter={}".format(names,filter))
    funname = "download_catalog_" + filter
    try:
      download_fun = getattr(self,funname)
    except AttributeError:
      logger_spider.exception("download_catalog {}不存在".format(funname))
      return False,"500错误"
    result = download_fun(names)
    return result

  # 下载biqukan网站小说目录
  def download_catalog_biqukan(self,names):
    logger_spider.debug("download_catalog_biqukan names={}".format(names))
    # 返回的结果
    return_result = {
      "source_name":"笔趣看",
      "source_url":"https://www.biqukan.com/",
      "source_img_url":"https://www.biqukan.com/images/logo.png"
    }
    home_url = "https://so.biqusoso.com/s.php?ie=utf-8&siteid=biqukan.com&q="
    if type(names) == str:
      download_url = home_url + names
    elif type(names) == tuple or type(names) == list:
      download_url = home_url + "+".join(names)
    else:
      logger_spider.error("download_catalog_biqukan names格式错误 names={}".format(names))
      return_result["status"] = ERROR
      return_result["information"] = "500错误"
      return return_result
    # 开始下载网页
    response = self.download_html(download_url)
    if response == False:
      logger_spider.error("download_catalog_biqukan 搜索下载目录失败 url={}".format(download_url))
      return_result["status"] = ERROR
      return_result["information"] = "服务器爬虫请求失败"
      return return_result
    content = response.text
    html = BeautifulSoup(content,"lxml")
    # 不要第一行的标题
    li = html.select(".search-list ul li")[1:]
    # 开始提取其中的内容
    result = []
    for line in li:
      span = line.find_all("span")
      item = {}
      if len(span) > 1:
        item["name"] = str(span[1].string).strip()
        try:
          item["download_url"] = span[1].a.attrs["href"]
          response_novel = self.download_html(item["download_url"])
          if response_novel == False:
            raise Exception("下载小说详细页面失败 url={}".format(item["download_url"]))
          novel_html = BeautifulSoup(response_novel.content.decode("gbk","replace"),"lxml")
          img_url = "https://www.biqukan.com" + novel_html.select_one(".cover img").attrs["src"]
          item["imageList"] = [img_url]
          introduction = [x for x in novel_html.select_one(".intro").stripped_strings]
          item["introduction"] = ["简介:" + str(introduction[1])]
        except KeyError:
          logger_spider.exception("download_catalog_biqukan book_name={} 没有href".format(item["name"]))
        except:
          logger_spider.exception("download_catalog_biqukan response_novel_error")
      if len(span) > 2:
        if item.get("introduction"):
          item["introduction"] = ["作者:" + str(span[2].string).strip()] + item["introduction"]
        else:
          item["introduction"] = ["作者" + str(span[2].string).strip()]
      if item != {}:
        result.append(item)
    return_result["status"] = SUCCESS
    return_result["content"] = result
    return return_result

  # 下载所有网址小说目录
  def download_catalog_all(self,names):
    return [self.download_catalog_biqukan(names)]

  # 判断一个网址应该用哪个下载器下载
  def judge_url(self,url):
    result = url.strip().split("/")
    if len(result) < 3:
      return False
    if result[2] == "www.biqukan.com":
      return "biqukan"
    else:
      return False

  # 根据网址下载小说
  def download_novel(self,url):
    logger_spider.debug("download_novel url={}".format(url))
    judge_result = self.judge_url(url)
    if judge_result == False:
      logger_spider.error("download_novel url={} 该网址找不到下载器")
      return False
    
    funname = "download_novel_" + judge_result
    try:
      download_fun = getattr(self,funname)
    except AttributeError:
      logger_spider.error("download_novel {}不存在".format(funname))
      return False
    return download_fun(url)

  # 下载biqukan网站小说内容
  def download_novel_biqukan(self,url):
    logger_spider.debug("download_novel_biqukan url={}".format(url))
    response = self.download_html(url)
    if response == False:
      logger_spider.exception("download_novel_biqukan 下载目录页面失败 url={}".format(url))
      return False
    html = BeautifulSoup(response.content.decode("gbk","replace"),"lxml")
    # 名称
    novel_name="biqukan小说"
    try:
      novel_name = str(html.select_one(".info h2").string).strip() or novel_name
    except:
      logger_spider.exception("download_novel_biqukan url={} name获取失败")
    # 内容
    block = html.select_one(".listmain")
    dt = block.find_all("dt")
    if len(dt) < 1:
      logger_spider.error("download_novel_biqukan block={} 未找到dt".format(block))
      return False
    dt = dt[-1]
    download_list = []
    for x in dt.next_siblings:
      if x.name == "dd":
        item = {}
        try:
          item["content"] = str(x.string.strip())
          item["url"] = "http://www.biqukan.com" + x.a.attrs["href"]
        except:
          logger_spider.exception("download_novel_biqukan dd={}".format(x))
        if item != {}:
          download_list.append(item)

    novel_contents = ""
    length = len(download_list)
    # 准备每章节进行下载
    for index in range(length):
      download_info = download_list[index]
      logger_spider.debug("当前下载：{} 主页={} 章节={}".format(download_info["content"],url,download_info["url"]))
      # 每下载30章就向redis数据库中更新一次进度
      if index % 30 == 0:
        self.connect.set(url,"{}/{}".format(index,length))
      response = self.download_html(download_info["url"])
      if response == False:
        logger_spider.exception("download_novel_biqukan 下载章节失败 url={}".format(download_info["url"]))
        # 下载失败，那么在明文中做出标记
        novel_contents += "{}\n{}\n{}\n{}\n\n".format("#" * 20,download_info["content"],"因为不可控因素，该章节下载失败，敬请谅解","#" * 20)
      else:
        try:
          html = BeautifulSoup(response.content.decode("gbk","replace"),"lxml")
          content_div = html.select_one("#content")
          scripts = content_div.find_all("script")
          # 清除script标签的内容
          for script in scripts:
            script.clear()
          contents = "\n".join([x for x in content_div.stripped_strings])
          novel_contents = novel_contents + download_info["content"] + "\n" + contents + "\n\n"
        except:
          logger_spider.exception("download_novel_biqukan 使用beautifulsoup提取html信息失败")
          novel_contents += "{}\n{}\n{}\n{}\n\n".format("#" * 20,download_info["content"],"异常因素，该章节下载失败，请联系416778940@qq.com","#" * 20)
    # 最后删掉url
    self.connect.delete(url)
    return novel_contents,novel_name

  def download_html(self,url):
    remain_count = self.__max_download_count
    while True:
      try:
        res = self.s.get(url,timeout=self.__timeout)
        res.raise_for_status()
        return res
      except:
        logger_spider.exception("download_html url={}".format(url))
        remain_count -= 1
        # 说明已经到达最大下载次数
        if remain_count == 0:
          logger_spider.error("达到最大下载次数 url = {}".format(url))
          break
    return False
