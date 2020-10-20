from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from config.config import SUCCESS,ERROR,once_return_count,download_process
from spider.spider import download_novel,search_novel,search_novel_more
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
  if content["status"] == False:
    information = content.get("information") or "未知错误"
    return JsonResponse({
      "status":ERROR,
      "information":information
    })

  # 如果只是单个数据，依然先转换为列表进行处理
  if type(content["result"]) == dict:
    content["result"] = [content["result"]]
  result = content["result"]
  # 说明没有内容，并且也没有错误
  if len(result) <= 0:
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
  
  # 如果返回数据超过once_return_count条那么就只返回once_return_count条然后将剩下的数据存储
  save_content = []
  # 是否保存结果到搜索缓存中，只要有一项是出现过错误的，我们就不保存
  save_cache = True
  # 记录其中没有内容的源在result中的位置
  empty_content = []
  content_cache = copy.deepcopy(content)
  for index in range(len(result)):
    # 如果下载有问题，那么直接下一条
    if result[index]["status"] == ERROR:
      save_cache = False
      continue
    # 如果搜索结果是空，那么需要附加一张随机福利图片
    if result[index]["length"] == 0:
      # result[index]["empty"] = True
      # length = len(image_list)
      # order = math.floor(random.random() * length)
      # result[index]["url"] = image_list[order]
      empty_content.append(index)
      continue
    else:
      result[index]["empty"] = False
    save = result[index]["content"][once_return_count:]
    pointer = result[index].get("pointer")
    saver = {}
    if pointer != None:
      saver["pointer"] = pointer
      # 爬虫指示器不需要返回到前端去
      del result[index]["pointer"]
    if save != []:
      saver["content"] = save
    if saver != {}:
      saver["source_name"] = result[index]["source_name"]
      save_content.append(saver)
      result[index]["end"] = False
    else:
      result[index]["end"] = True
    result[index]["content"] = result[index]["content"][:once_return_count]
  # 将内容为空的网站源从result中删除
  if len(empty_content) > 0:
    result = [result[x] for x in range(len(result)) if x not in empty_content]
    content_cache["result"] = [content_cache["result"][x] for x in range(len(content_cache["result"])) if x not in empty_content]
  if save_cache:
    save_search_result(names,content_cache)
  # 说明result中所有网站源都是空的
  if len(result) <= 0:
    length = len(image_list)
    order = math.floor(random.random() * length)
    response = JsonResponse({
      "status":SUCCESS,
      "result":{
        "empty":True,
        "url":image_list[order]
      }
    })
  else:
    response = JsonResponse({
      "status":SUCCESS,
      "result":result
    })
  token = ""
  if save_content != []:
    token = get_token()
    data = json.dumps(save_content)
    search_token = SearchToken(token=token,data=data)
    search_token.save()
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
  # 返回的内容
  result = {
    "source_name":name
  }
  for index in range(len(content)):
    item = content[index]
    if item["source_name"] == name:
      pointer = item.get("pointer")
      remain_content = item.get("content")
      result_more = None
      if remain_content == None or len(remain_content) == 0:
        if pointer == None:
          # 这种情况正常不会出现
          logger_backend.error("search_more 无content和pointer source_name={}".format(item["source_name"]))
          content.pop(index)
          search_token.data = json.dumps(content)
          search_token.save()
          return JsonResponse({
            "status":ERROR,
            "information":"没有更多信息"
          })
        result_more = search_novel_more(pointer)
      elif len(remain_content) < once_return_count:
        if pointer != None:
          result_more = search_novel_more(pointer)
      if result_more != None:
        if result_more["status"] == False:
          # 如果没能进一步爬取更多信息，并且原来的内容是空，那么返回错误信息，此时数据库不需要进行修改
          if remain_content == None or len(remain_content) == 0:
            return JsonResponse({
              "status":ERROR,
              "information":result_more["information"]
            })
        else:
          result_more_content = result_more["content"]
          if result_more_content["status"] == ERROR:
            # 如果没能进一步爬取更多信息，并且原来的内容是空，那么返回错误信息，此时数据库不需要进行修改
            if remain_content == None or len(remain_content) == 0:
              return JsonResponse({
                "status":ERROR,
                "information":result_more_content["information"]
              })
          else:
            new_pointer = result_more_content.get("pointer")
            new_content = result_more_content.get("content")
            new_length = result_more_content.get("length")
            if new_pointer == None:
              del item["pointer"]
            else:
              item["pointer"] = new_pointer
            if remain_content == None:
              item["content"] = new_content
            else:
              item["content"] += new_content
            remain_content = item["content"]
            result["length"] = new_length
      if remain_content == None:
        result["content"] = []
      else:
        result["content"] = remain_content[:once_return_count]
        item["content"] = remain_content[once_return_count:]
        if len(item["content"]) == 0:
          del item["content"]
      if not item.get("content") and not item.get("pointer"):
        content.pop(index)
        result["end"] = True
      else:
        result["end"] = False
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
    redis_item = connect.hget(download_process,url)
    if redis_item == None:
      return JsonResponse({
        "status":SUCCESS,
        "percent":False
      })
    else:
      redis_item = json.loads(redis_item)
      percent = redis_item.get("percent") or False
      detail = redis_item.get("detail")
      return_response = {
        "status":SUCCESS,
        "percent":percent
      }
      if detail:
        return_response["detail"] = detail
      return JsonResponse(return_response)
  # 如果download_error=True，那么查询完成之后立刻删除这条记录，也就是下次下载会重新开始而不是直接判定为下载失败
  if download_cache.download_error == True:
    information = download_cache.download_error_info if download_cache.download_error_info != None else "下载出现错误"
    download_cache.delete()
    return JsonResponse({
      "status":ERROR,
      "information":information
    })
  data_url = download_cache.data_url
  if data_url != None:
    download_url = data_url
    name = download_cache.data_name
    open_page = True
  else:
    download_url = request.build_absolute_uri(settings.MEDIA_URL + download_cache.data.name)
    name = download_cache.data.name
    open_page = False
  return_response = {
    "status":SUCCESS,
    "result":download_url,
    "name":name,
    "open_page":open_page
  }
  data_detail = download_cache.data_detail
  if data_detail != None:
    return_response["detail"] = json.loads(data_detail)
  return JsonResponse(return_response)

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
    data_content = content.get("content")
    data_url = content.get("url")
    data_detail = content.get("detail")
    if data_content != None:
      if type(data_content) == str:
        data = data_content.encode("utf8")
      else:
        data = data_content
      pc_file = getInMemoryUploadedFile_bytes(data,name)
      download_cache.data = pc_file
    elif data_url != None:
      download_cache.data_url = data_url
      download_cache.data_name = name
    else:
      download_cache.download_error = True
      download_cache.download_error_info = "download_novel没有返回下载内容"
    if data_detail != None:
      download_cache.data_detail = json.dumps(data_detail)
  download_cache.downloaded = True
  download_cache.save()
