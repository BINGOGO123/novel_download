from django.db import models

# Create your models here.

class SearchToken(models.Model):
  # 每次搜索都会分配一个32字节的随机token
  token = models.CharField(max_length=32,null=False,blank=False,primary_key=True)
  data = models.TextField(null=False,blank=False)
  date_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.token

# 搜索缓存
class SearchCache(models.Model):
  search = models.CharField(max_length=120,null=False,blank=False,primary_key=True)
  data = models.TextField(null=False,blank=False)
  date_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.search

class DownloadCache(models.Model):
  url = models.TextField(null=False,blank=False)
  # 下载的文件信息
  data = models.FileField(null=True,blank=True)
  # 文件网址，也就是没有下载到我们的服务器
  data_url = models.TextField(null=True,blank=True)
  # 文件名称，当没有下载到服务器时，文件名称就这样保存
  data_name = models.TextField(null=True,blank=True)
  # 详情信息，该下载页面的详情信息，json字符串，可以无
  data_detail = models.TextField(null=True,blank=True)
  # 标记文件是否已经下载完成
  downloaded = models.BooleanField(default=False)
  # 标记是否出现错误
  download_error = models.BooleanField(default=False)
  # 记录错误信息，可以没有
  download_error_info = models.CharField(max_length=128,blank=True,null=True)
  date_time = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.url
