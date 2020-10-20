import requests
from bs4 import BeautifulSoup
from config.logger import logger_spider
from config.config import redis_connect
import ipdb
from config.config import SUCCESS,ERROR,download_process
import sys
import json
import re

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
      return {
        "status":False,
        "information":"500错误"
      }
    result = download_fun(names)
    return {
      "status":True,
      "result":result
    }

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
        item["download_url"] = span[1].a.attrs["href"]
        # 原来是会到详细页面爬取更多信息的，但是这样导致速度过慢，因此放弃
        # try:
        #   response_novel = self.download_html(item["download_url"])
        #   if response_novel == False:
        #     raise Exception("下载小说详细页面失败 url={}".format(item["download_url"]))
        #   novel_html = BeautifulSoup(response_novel.content.decode("gbk","replace"),"lxml")
        #   img_url = "https://www.biqukan.com" + novel_html.select_one(".cover img").attrs["src"]
        #   item["imageList"] = [img_url]
        #   introduction = [x for x in novel_html.select_one(".intro").stripped_strings]
        #   item["introduction"] = ["简介:" + str(introduction[1])]
        # except KeyError:
        #   logger_spider.exception("download_catalog_biqukan book_name={} 没有href".format(item["name"]))
        # except:
        #   logger_spider.exception("download_catalog_biqukan response_novel_error")
      if len(span) > 2:
        item["introduction"] = ["作者:" + str(span[2].string).strip()]
        # 注释原因同上
        # if item.get("introduction"):
        #   item["introduction"] = ["作者:" + str(span[2].string).strip()] + item["introduction"]
        # else:
        #   item["introduction"] = ["作者:" + str(span[2].string).strip()]
      if item != {}:
        result.append(item)
    # 总的元素数目
    return_result["content"] = result
    return_result["length"] = len(return_result["content"])
    return_result["status"] = SUCCESS
    return return_result
  
  # 下载爱下电子书网站小说目录
  def download_catalog_aixdzs(self,names,page=None):
    logger_spider.debug("download_catalog_aixdzs names={} page={}".format(names,page))
    # 返回的结果
    return_result = {
      "source_name":"爱下电子书",
      "source_url":"https://m.aixdzs.com/",
      "source_img_url":"https://www.aixdzs.com/style/img/logo.jpg"
    }
    home_url = "https://m.aixdzs.com/search?k="
    if type(names) == str:
      download_url = home_url + names
    elif type(names) == tuple or type(names) == list:
      download_url = home_url + "+".join(names)
    else:
      logger_spider.error("download_catalog_aixdzs names格式错误 names={}".format(names))
      return_result["status"] = ERROR
      return_result["information"] = "500错误"
      return return_result
    # 目录的页数，默认是第一页
    if page != None:
      download_url += "&page={}".format(page)
    # 开始下载网页
    response = self.download_html(download_url)
    if response == False:
      logger_spider.error("download_catalog_aixdzs 搜索下载目录失败 url={}".format(download_url))
      return_result["status"] = ERROR
      return_result["information"] = "服务器爬虫请求失败"
      return return_result
    content = response.text
    html = BeautifulSoup(content,"lxml")
    lis = html.select(".ix-list li")
    # 开始提取其中的内容
    result = []
    for li in lis:
      item = {}
      # 图片信息
      img_div = li.select_one(".ix-list-img-square img")
      img_url = img_div.attrs["src"]
      # 这张图片的意思是暂无封面
      abandon_img = ["https://img22.aixdzs.com/nopic2.jpg"]
      if img_url not in abandon_img:
        item["imageList"] = [img_url]
      # 文字信息
      info_div = li.select_one(".ix-list-info")
      item["name"] = str(info_div.h3.a.string)
      item["download_url"] = "https://m.aixdzs.com" + info_div.h3.a.attrs["href"]
      introduction = []
      author = info_div.select_one(".meta .meta-l a")
      author_content = author.string
      if author_content != None:
        introduction.append("作者:" + str(author_content).strip())
      article_type = info_div.select(".meta .meta-r em")
      article_type_content = [str(x.string).strip() for x in article_type if x.string != None]
      if article_type_content != []:
        introduction.append(" ".join(article_type_content))
      introduction_content = info_div.p.string
      if introduction_content != None:
        introduction.append("简介:" + str(introduction_content).strip())
      item["introduction"] = introduction
      result.append(item)
    # 获取后续页面
    inputs = html.select("#page,#maxpage")
    if inputs == [] or len(inputs) < 2:
      return_result["length"] = len(result)
    else:
      present_page = int(inputs[0].attrs["value"])
      max_page = int(inputs[1].attrs["value"])
      if present_page >= max_page:
        return_result["length"] = (max_page - 1) * 20 + len(result)
      else:
        return_result["length"] = str((max_page - 1) * 20) + "+"
        return_result["pointer"] = {
          "spider":sys._getframe().f_code.co_name,
          "params":{
            "names":names,
            "page":present_page + 1
          }
        }
    return_result["status"] = SUCCESS
    return_result["content"] = result
    return return_result
  
  # 下载哔哩轻小说网站小说目录
  def download_catalog_linovelib(self,names=None,url=None):
    logger_spider.debug("download_catalog_linovelib names={} url={}".format(names,url))
    # 返回的结果
    return_result = {
      "source_name":"哔哩轻小说",
      "source_url":"https://www.linovelib.com/",
      "source_img_url":"https://www.linovelib.com/images/logo.png"
    }
    home_url = "https://www.linovelib.com/s/"
    # 说明是首次搜索
    if url == None:
      post_data = {
        "searchtype":"all"
      }
      if type(names) == str:
        post_data["searchkey"] = names
      elif type(names) == tuple or type(names) == list:
        post_data["searchkey"] = " ".join(names)
      else:
        logger_spider.error("download_catalog_linovelib names格式错误 names={}".format(names))
        return_result["status"] = ERROR
        return_result["information"] = "500错误"
        return return_result
      request_params = {
        "url":home_url,
        "method":"POST",
        "data":post_data
      }
    # 说明不是首次搜索，而是接下来的页面
    else:
      request_params = {
        "url":url,
        "method":"GET"
      }
    # 开始下载网页
    response = self.download_html(**request_params)
    if response == False:
      logger_spider.error("download_catalog_linovelib 搜索下载目录失败 request_params={}".format(request_params))
      return_result["status"] = ERROR
      return_result["information"] = "服务器爬虫请求失败"
      return return_result
    content = response.text
    html = BeautifulSoup(content,"lxml")
    # 说明搜索出来不止一条结果
    if len(response.history) <= 0:
      lis = html.select(".search-result-list")
      # 开始提取其中的内容
      result = []
      for li in lis:
        item = {}
        try:
          item["download_url"] = "https://www.linovelib.com" + li.select_one(".imgbox a").attrs["href"]
          item["download_url"] = ".".join(item["download_url"].split(".")[:-1]) + "/catalog"
          item["imageList"] = [li.select_one(".imgbox a img").attrs["src"]]
          item["name"] = str(li.select_one("h2.tit a").string).strip()
          item["introduction"] = []
          bookinfo = li.select_one(".bookinfo")
          bookinfo_list = [str(x) for x in bookinfo.stripped_strings]
          if len(bookinfo_list) >= 1 and bookinfo_list[-1] == "万":
            bookinfo_list = bookinfo_list[:-1]
          bookinfo_list = [x for x in bookinfo_list if x != "|"]
          bookinfo_str = " ".join(bookinfo_list)
          regular = re.compile(r"""towan\('(\d*)'\)""")
          bookinfo_result = re.sub(regular,r"\1",bookinfo_str)
          if bookinfo_result != "":
            item["introduction"].append(bookinfo_result)
          key_word = li.select_one(".key-word").string
          if key_word != None:
            item["introduction"].append("关键词:" + str(key_word).strip())
          introduction = li.p.string
          if introduction != None:
            item["introduction"].append("简介:" + str(introduction).strip())
        except:
          logger_spider.exception("download_catalog_linovelib 网页解析错误 url={}".format(response.url))
        if item != {}:
          result.append(item)
      # 获取之后待爬取的页面
      try:
        next_page = html.select_one(".next")
        last_page = int(html.select_one(".last").string)
        # present_page = int(html.select_one(".pagelink strong").string)
      except:
        return_result["length"] = len(result)
      else:
        if next_page == None:
          return_result["length"] = (last_page - 1) * 20 + len(result)
        else:
          next_url = "https://www.linovelib.com" + next_page.attrs["href"]
          return_result["pointer"] = {
            "spider":sys._getframe().f_code.co_name,
            "params":{
              "url":next_url
            }
          }
          return_result["length"] = "{}+".format((last_page - 1) * 20)
    # 被重定向到了具体页面，说明只有一条结果
    else:
      result = []
      item = {}
      try:
        item["imageList"] = [html.select_one(".book-img img").attrs["src"]]
        item["download_url"] = "https://www.linovelib.com" + html.select_one(".btn-group .read-btn").attrs["href"]
        item["name"] = str(html.select_one(".book-name").string).strip()
        item["introduction"] = []
        item["introduction"].append(" ".join([x for x in html.select_one(".book-label").stripped_strings]))
        item["introduction"].append("简介:" + "\n".join([x for x in html.select_one(".book-dec").stripped_strings]))
      except:
        logger_spider.exception("download_catalog_linovelib 网页解析错误 url={}".format(response.url))
      if item != {}:
        result.append(item)
      return_result["length"] = len(result)
    return_result["content"] = result
    return_result["status"] = SUCCESS
    return return_result

  # 下载所有网址小说目录
  def download_catalog_all(self,names):
    return [self.download_catalog_biqukan(names),self.download_catalog_aixdzs(names),self.download_catalog_linovelib(names)]
    # return [self.download_catalog_aixdzs(names)]

  # 判断一个网址应该用哪个下载器下载
  def judge_url(self,url):
    result = url.strip().split("/")
    if len(result) < 3:
      return False
    if result[2] == "www.biqukan.com":
      return "biqukan"
    elif result[2] == "m.aixdzs.com":
      return "aixdzs"
    elif result[2] == "www.linovelib.com":
      return "linovelib"
    else:
      return False

  # 根据网址下载小说
  def download_novel(self,url):
    logger_spider.debug("download_novel url={}".format(url))
    judge_result = self.judge_url(url)
    if judge_result == False:
      logger_spider.error("download_novel url={} 该网址找不到下载器".format(url))
      return {
        "status":False,
        "information":"该网址找不到下载器"
      }
    
    funname = "download_novel_" + judge_result
    try:
      download_fun = getattr(self,funname)
    except AttributeError:
      logger_spider.error("download_novel {}不存在".format(funname))
      return {
        "status":False,
        "information":"{}下载器不存在".format(funname)
      }
    return download_fun(url)

  # 下载biqukan网站小说内容
  def download_novel_biqukan(self,url):
    logger_spider.debug("download_novel_biqukan url={}".format(url))
    response = self.download_html(url)
    if response == False:
      logger_spider.exception("download_novel_biqukan 获取小说详细页面失败 url={}".format(url))
      return {
        "status":False,
        "information":"获取小说详细页面失败"
      }
    html = BeautifulSoup(response.content.decode("gbk","replace"),"lxml")
    # 名称
    novel_name="biqukan小说.txt"
    try:
      novel_name = str(html.select_one(".info h2").string).strip() + ".txt" or novel_name
    except:
      logger_spider.exception("download_novel_biqukan url={} name获取失败")
    # 先获取小说的一些详细信息
    redis_item = {}
    detail = {}
    detail["imageList"] = ["https://www.biqukan.com" + html.select_one(".cover img").attrs["src"]]
    introduction = [x for x in html.select_one(".intro").stripped_strings]
    detail["introduction"] = ["简介:" + str(introduction[1])]
    redis_item["detail"] = detail
    self.connect.hset(download_process,url,json.dumps(redis_item))
    # 内容下载
    block = html.select_one(".listmain")
    dt = block.find_all("dt")
    if len(dt) < 1:
      logger_spider.error("download_novel_biqukan block={} 未找到dt".format(block))
      return {
        "status":False,
        "information":"页面解析失败"
      }
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
        redis_item = self.connect.hget(download_process,url)
        if redis_item == None:
          redis_item = {}
        else:
          redis_item = json.loads(redis_item)
        # 大约还要等待的时间，假设每章的时间为0.3s，取整
        redis_item["percent"] = int((length - index) * 0.3)
        redis_item["progress"] = "{}/{}".format(index,length)
        self.connect.hset(download_process,url,json.dumps(redis_item))
        # self.connect.hset(download_process,url,"{}/{}".format(index,length))
        # self.connect.set(url,"{}/{}".format(index,length))
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
    # 最后先获取详细信息，然后删掉url
    redis_item = self.connect.hget(download_process,url)
    self.connect.hdel(download_process,url)
    # self.connect.delete(url)
    return_result = {
      "status":True,
      "content":novel_contents,
      "name":novel_name
    }
    if redis_item != None:
      redis_item = json.loads(redis_item)
      if redis_item.get("detail"):
        return_result["detail"] = redis_item["detail"]
    return return_result
  
  # 下载爱下电子书网站小说内容
  def download_novel_aixdzs(self,url):
    logger_spider.debug("download_novel_aixdzs url={}".format(url))
    response = self.download_html(url)
    if response == False:
      logger_spider.exception("download_novel_aixdzs 获取小说详细页面失败 url={}".format(url))
      return {
        "status":False,
        "information":"获取小说详细页面失败"
      }
    html = BeautifulSoup(response.content,"lxml")
    # 名称,这个网站下载格式应该都是zip，如果不是可能就会出现问题
    novel_name="aixdzs小说.zip"
    try:
      novel_name_block = html.select_one(".ix-list-info h4")
      if novel_name_block.string != None:
        novel_name = str(novel_name_block.string).strip() + ".zip"
    except:
      logger_spider.exception("download_novel_aixdzs url={} name获取失败")

    lis = html.select(".zipdown li")
    download_url = False
    if len(lis) < 0:
      logger_spider.exception("download_novel_aixdzs .zipdown li 个数为0")
      return {
        "status":False,
        "information":"没有下载链接"
      }
    elif len(lis) > 2:
      download_li = lis[1]
      li_content = "".join([str(x) for x in download_li.strings])
      if "TXT下载" in li_content:
        download_url = download_li.a.attrs["href"]
    if download_url == False:
      for li in lis:
        li_content = "".join([str(x) for x in li.strings])
        if "TXT下载" in li_content:
          download_url = li.a.attrs["href"]
          break
    if download_url == False or download_url == None:
      return {
        "status":False,
        "information":"download_url获取失败"
      }
    download_url = "https://m.aixdzs.com" + download_url
    return {
      "status":True,
      "url":download_url,
      "name":novel_name
    }
    # 将该文件下载到本地
    # download_content = self.download_html(download_url)
    # if download_content == False:
    #   logger_spider.error("download_novel_aixdzs 下载小说请求失败 url={}".format(download_url))
    #   return {
    #     "status":False,
    #     "information":"下载小说请求失败"
    #   }
    # return {
    #   "status":True,
    #   "content":download_content.content,
    #   "name":novel_name
    # }

  # 下载bili轻小说网站小说内容
  def download_novel_linovelib(self,url):
    logger_spider.debug("download_novel_linovelib url={}".format(url))
    response = self.download_html(url)
    if response == False:
      logger_spider.exception("download_novel_linovelib 获取小说详细页面失败 url={}".format(url))
      return {
        "status":False,
        "information":"获取小说详细页面失败"
      }
    html = BeautifulSoup(response.text,"lxml")
    # 名称
    novel_name="linovelib小说.txt"
    try:
      novel_name = str(html.select_one(".book-meta h1").string).strip() + ".txt" or novel_name
    except:
      logger_spider.exception("download_novel_linovelib url={} name获取失败")
    # 内容下载
    lias = html.select(".chapter-list li a,.chapter-list div")
    download_list = [{"content":str(lia.string).strip(),"url":"https://www.linovelib.com" + lia.attrs["href"]} if lia.name.lower() == "a" else "\n".join([x for x in lia.stripped_strings]) for lia in lias]

    novel_contents = ""
    length = len(download_list)
    # 准备每章节进行下载
    for index in range(length):
      # 每下载30章就向redis数据库中更新一次进度
      if index % 30 == 0:
        redis_item = self.connect.hget(download_process,url)
        if redis_item == None:
          redis_item = {}
        else:
          redis_item = json.loads(redis_item)
        # 大约还要等待的时间，假设每章的时间为0.3s，取整
        redis_item["percent"] = int((length - index) * 0.3)
        redis_item["progress"] = "{}/{}".format(index,length)
        self.connect.hset(download_process,url,json.dumps(redis_item))
        # self.connect.hset(download_process,url,"{}/{}".format(index,length))
        # self.connect.set(url,"{}/{}".format(index,length))
      download_info = download_list[index]
      if type(download_info) == str:
        novel_contents = novel_contents + "《" + download_info + "》" + "\n\n"
        continue
      logger_spider.debug("当前下载：{} 主页={} 章节={}".format(download_info["content"],url,download_info["url"]))
      response = self.download_html(download_info["url"])
      if response == False:
        logger_spider.exception("download_novel_linovelib 下载章节失败 url={}".format(download_info["url"]))
        # 下载失败，那么在明文中做出标记
        novel_contents += "{}\n{}\n{}\n{}\n\n".format("#" * 20,download_info["content"],"因为不可控因素，该章节下载失败，敬请谅解","#" * 20)
      else:
        try:
          html = BeautifulSoup(response.text,"lxml")
          content_p = html.select("#TextContent > p")
          contents = "\n".join([str(p.string).strip() for p in content_p])
          novel_contents = novel_contents + download_info["content"] + "\n" + contents + "\n\n"
        except:
          logger_spider.exception("download_novel_linovelib 使用beautifulsoup提取html信息失败")
          novel_contents += "{}\n{}\n{}\n{}\n\n".format("#" * 20,download_info["content"],"异常因素，该章节下载失败，请联系416778940@qq.com","#" * 20)
    # 最后删掉url
    self.connect.hdel(download_process,url)
    # self.connect.delete(url)
    return_result = {
      "status":True,
      "content":novel_contents,
      "name":novel_name
    }
    return return_result

  # 获取http返回信息
  def download_html(self,url,method="GET",**kwargs):
    remain_count = self.__max_download_count
    while True:
      try:
        res = self.s.request(method,url,timeout=self.__timeout,**kwargs)
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
