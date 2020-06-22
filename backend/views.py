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
#   "status":ERROR,
#   "information":"未知错误"
# }
# {
#   "status":SUCCESS,
#   "result":{
#     "empty":True,
#     "url":"www.bingoz.cn"
#   }
# }
# {
#   "status":SUCCESS,
#   "result":{
#     "empty":False,
#     "length":300,
#     "end":True, # 或者False，看这次是否返回全部内容了
#     "content":[
#       {
#         "name":"三国演义",
#         "introduction":"巴拉巴拉",
#         "download_url":"www.bingoz.cn",
#         # 可以是[]或者没有这一项
#         "imageList":[
#           "www.bingoz.cn",
#           "www.bingoz.cn"
#         ],
#         "source_name":"笔趣看",
#         "source_url":"www.bingoz.cn",
#         # 可以没有这一项
#         "source_img_url":"www.bingoz.cn"
#       }
#     ]
#   }
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
  # 先看一下最近是否有搜索过类似的结果，如果没有那么再去下载
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
      "information":"服务器错误"
    })
  # 保存结果到搜索缓存中
  save_search_result(names,content)

  # 说明没有信息，直接返回
  if (type(content) != list and type(content) != tuple) or len(content) <= 0:
    length = len(image_list)
    order = math.floor(random.random() * length)
    return JsonResponse({
      "status":SUCCESS,
      "result":{
        "empty":True,
        "url":image_list[order]
      }
    })

  content_return = content[:20]
  content_save = content[20:]
  # 如果返回数据超过20条那么就只返回20条然后将剩下的数据存储
  token = ""
  if content_save != []:
    token = get_token()
    data = json.dumps(content_save)
    search_token = SearchToken(token=token,data=data)
    search_token.save()

  response = JsonResponse({
    "status":SUCCESS,
    "result":{
      "empty":False,
      "end":content_save == [],
      "length":len(content),
      "content":content_return
    }
  })
  if token != "":
    max_age = 24*60*60
    response.set_cookie("novel_download_search_token",token,max_age=max_age)
  return response

# 返回格式
# {
#   "status":ERROR,
#   "information":"巴拉巴拉"
# }
# {
#   "status":SUCCESS,
#   "result":{
#     "end":True, # or False
#     "content":[] # 格式与上面一样，如果没有了就是[]
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
  try:
    search_token = SearchToken.objects.get(token=token)
  except SearchToken.DoesNotExist:
    logger_backend.exception("token={} 数据库不存在该项".format(token))
    return JsonResponse({
      "status":ERROR,
      "information":"没有更多信息"
    })
  content = json.loads(search_token.data)
  content_return = content[:20]
  content_save = content[20:]
  response = JsonResponse({
    "status":SUCCESS,
    "result":{
      "end":content_save == [],
      "content":content_return
    }
  })
  # 修改数据库，如果没有content_save了，那么删除数据库中信息以及cookies
  if content_save != []:
    search_token.data = json.dumps(content_save)
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
  if download_cache.download_error == True:
    information = download_cache.download_error_info if download_cache.download_error_info != None else "下载出现错误"
    return JsonResponse({
      "status":ERROR,
      "information":information
    })
  download_url = request.build_absolute_uri(settings.MEDIA_URL + download_cache.data.name)
  return JsonResponse({
    "status":SUCCESS,
    "result":download_url
  })

# 下载某个url的小说内容并存入数据库
def download(url):
  download_cache = DownloadCache(url=url,downloaded=False,download_error=False)
  download_cache.save()
  content= download_novel(url)
  if (type(content) == list or type(content) == tuple) and len(content) > 1 and content[0] == False:
    # 这种情况下说明有错误信息
    download_cache.download_error = True
    download_cache.download_error_info = content[1]
  elif content == False:
    download_cache.download_error = True
  else:
    # 对下载到的内容采用utf8进行编码
    name = content[1]
    content = content[0]
    data = content.encode("utf8")
    pc_file = getInMemoryUploadedFile_bytes(data,name)
    download_cache.data = pc_file
  download_cache.downloaded = True
  download_cache.save()
