from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from config.config import SUCCESS,ERROR
from spider.spider import download_novel,search_novel
from config.logger import logger_backend
from .image_list import image_list
import random,math
import base64
import hashlib
import time
import math
import json
import ipdb
from novel_download import settings
import threading
from .essential import getInMemoryUploadedFile_bytes
from config.config import redis_connect
import copy

from .models import SearchToken,SearchCache,DownloadCache

# Create your views here.

def get_exist_search_result(names):
  search = json.dumps(names)
  try:
    search_cache = SearchCache.objects.get(search=search)
  except SearchCache.DoesNotExist:
    return False
  return json.loads(search_cache.data)

def save_search_result(names,content):
  search = json.dumps(names)
  data = json.dumps(content)
  search_cache = SearchCache(search=search,data=data)
  search_cache.save()

# 生成32Byte随机token
def get_token():
  now = str(time.time()).encode("ascii")
  random_part = bytes([random.randint(0,255) for x in range(16)])
  h = hashlib.md5()
  h.update(now + random_part)
  return h.hexdigest()

# 返回格式
# {
#   status:0,
#   result:[
#     {
#       source_name:"笔趣看",
#       // 资源网站网址
#       source_url:"www.baidu.com",
#       // 网站图片网址，可以没有
#       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png",
#       // 表示搜索结果是否为空，如果为空，那么下面的内容都不需要
#       status:0,
#       empty:false,
#       // 表示是否已经达到结束的地方
#       end:false,
#       // 表示搜索结果总数
#       length:100,
#       // 搜索的结果列表
#       content:[
#         {
#           name:"三国演义",
#           introduction:["三国演义"],
#           // 源网页网址
#           download_url:"www.baidu.com",
#           imageList:[
#             "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1592159453680&di=edb8f09c8fb193dbba6bde8dd6f24a6d&imgtype=0&src=http%3A%2F%2Fimage.gqjd.net%2Fimage%2F2009-12%2F72712457221.jpg",
#             "http://image.gqjd.net/image/2009-12/57295513513.jpg"
#           ]
#         }
#       ]
#     },
#     // 搜索为空的结果
#     {
#       source_name:"笔趣看",
#       source_url:"www.biqukan.com",
#       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png",
#       status:0,
#       empty:true,
#       // 显示的福利图片网址
#       url:"http://www.xinhuanet.com/video/2020-01/26/1210452637_15800000011261n.jpg"
#     },
#     // 搜索单项出现错误
#     {
#       source_name:"笔趣看",
#       source_url:"www.baidu.com",
#       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png",
#       status:1,
#       information:"出现错误"
#     }
#   ]
# }
def search(request):
  if request.method != "POST":
    return JsonResponse({
      "status":ERROR,
      "information":"请求方式非POST"
    })
  try:
    name = request.POST["search"]
  except:
    return JsonResponse({
      "status":ERROR,
      "information":"无搜索内容"
    })
  
  names = [x.strip() for x in name.strip().split(" ") if x.strip() != ""]
  # 先看一下最近是否有搜索过相同的东西，如果没有那么再去下载
  content = get_exist_search_result(names)
  if not content:
    content = search_novel(names)
  if (type(content) == list or type(content) == tuple) and len(content) > 1 and content[0] == False:
    # 这种情况下说明有错误信息
    return JsonResponse({
      "status":ERROR,
      "information":content[1]
    })
  if content == False:
    return JsonResponse({
      "status":ERROR,
      "information":"500错误"
    })
  if type(content) != list and type(content) != tuple:
    return JsonResponse({
      "status":ERROR,
      "information":"500错误"
    })

  # 说明没有信息，直接返回
  if len(content) <= 0:
    # 保存结果到搜索缓存中
    save_search_result(names,content)
    length = len(image_list)
    order = math.floor(random.random() * length)
    return JsonResponse({
      "status":SUCCESS,
      "result":{
        "empty":True,
        "url":image_list[order]
      }
    })
  
  # 如果返回数据超过20条那么就只返回20条然后将剩下的数据存储
  save_content = []
  # 是否保存结果到搜索缓存中，只要有一项是出现过错误的，我们就不保存
  save_cache = True
  content_cache = copy.deepcopy(content)
  for index in range(len(content)):
    # 如果下载有问题，那么直接下一条
    if content[index]["status"] == ERROR:
      save_cache = False
      continue
    content[index]["length"] = len(content[index]["content"])
    # 如果搜索结果是空，那么需要附加一张随机福利图片
    if content[index]["length"] <= 0:
      content[index]["empty"] = True
      length = len(image_list)
      order = math.floor(random.random() * length)
      content[index]["url"] = image_list[order]
    else:
      content[index]["empty"] = False
    save = content[index]["content"][20:]
    if save != []:
      save_content.append({
        "source_name":content[index]["source_name"],
        "content":save
      })
      content[index]["end"] = False
    else:
      content[index]["end"] = True
    content[index]["content"] = content[index]["content"][:20]
  if save_cache:
    save_search_result(names,content_cache)
  token = ""
  if save_content != []:
    token = get_token()
    data = json.dumps(save_content)
    search_token = SearchToken(token=token,data=data)
    search_token.save()
  response = JsonResponse({
    "status":SUCCESS,
    "result":content
  })
  if token != "":
    max_age = 24*60*60
    response.set_cookie("novel_download_search_token",token,max_age=max_age)
  return response

# 返回格式
# {
#   "status":SUCCESS,
#   "result":{
#     "source_name":"笔趣看",
#     "content":[],
#     "end":False
#   }
# }
def search_more(request):
  if request.method != "POST":
    return JsonResponse({
      "status":ERROR,
      "information":"请求方式非POST"
    })
  if not request.COOKIES.get("novel_download_search_token"):
    return JsonResponse({
      "status":ERROR,
      "information":"没有更多信息"
    })
  token = request.COOKIES.get("novel_download_search_token")
  name = request.POST.get("name")
  if name == None:
    return JsonResponse({
      "status":ERROR,
      "information":"请求信息不完整"
    })
  try:
    search_token = SearchToken.objects.get(token=token)
  except SearchToken.DoesNotExist:
    logger_backend.exception("token={} 数据库不存在该项".format(token))
    return JsonResponse({
      "status":ERROR,
      "information":"没有更多信息"
    })
  content = json.loads(search_token.data)
  for index in range(len(content)):
    item = content[index]
    if item["source_name"] == name:
      result = {
        "source_name":name,
        "content":item["content"][:20]
      }
      item["content"] = item["content"][20:]
      result["end"] = item["content"] == []
      if item["content"] == []:
        content.pop(index)
      break
  else:
    return JsonResponse({
      "status":ERROR,
      "information":"{}没有更多信息".format(name)
    })
  response = JsonResponse({
    "status":SUCCESS,
    "result":result
  })
  # 修改数据库，如果没有content了，那么删除数据库中信息以及cookies
  if content != []:
    search_token.data = json.dumps(content)
    search_token.save()
  else:
    search_token.delete()
    response.delete_cookie("novel_download_search_token")
  return response

# 判断某个url是否已经下载完成
def downloaded(request):
  if request.method != "POST":
      return JsonResponse({
      "status":ERROR,
      "information":"请求方式非POST"
    })
  try:
    url = request.POST["url"]
  except:
    return JsonResponse({
      "status":ERROR,
      "information":"请求中无url"
    })
  url = url.strip()
  try:
    download_cache = DownloadCache.objects.get(url=url)
  # 说明还没开始下载
  except DownloadCache.DoesNotExist:
    # 这里要异步执行
    t = threading.Thread(target=download,args=(url,))
    t.start()
    return JsonResponse({
      "status":SUCCESS,
      "percent":False
    })
  connect = redis_connect.getConnect()
  if download_cache.downloaded == False:
    percent = connect.get(url)
    if percent == None:
      percent = False
    return JsonResponse({
      "status":SUCCESS,
      "percent":percent
    })
  # 如果download_error=True，那么查询完成之后立刻删除这条记录，也就是下次下载会重新开始而不是直接判定为下载失败
  if download_cache.download_error == True:
    information = download_cache.download_error_info if download_cache.download_error_info != None else "下载出现错误"
    download_cache.delete()
    return JsonResponse({
      "status":ERROR,
      "information":information
    })
  download_url = request.build_absolute_uri(settings.MEDIA_URL + download_cache.data.name)
  return JsonResponse({
    "status":SUCCESS,
    "result":download_url,
    "name":download_cache.data.name
  })

# 下载某个url的小说内容并存入数据库
def download(url):
  download_cache = DownloadCache(url=url,downloaded=False,download_error=False)
  download_cache.save()
  content= download_novel(url)
  if content["status"] == False:
    information = content.get("information")
    if information == None:
      information = "下载过程出现未知错误"
    download_cache.download_error = True
    download_cache.download_error_info = information
  else:
    name = content.get("name")
    if type(content.get("content")) == str:
      data = content.get("content").encode("utf8")
    else:
      data = content.get("content")
    pc_file = getInMemoryUploadedFile_bytes(data,name)
    download_cache.data = pc_file
  download_cache.downloaded = True
  download_cache.save()
