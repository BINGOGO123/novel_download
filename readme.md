# 说明

多站小说下载器，使用实时爬虫搜索和下载多个网站的小说内容，每次搜索和下载都会进行多次爬取，因此能够实时抓取小说网站的内容，且不占用服务器的硬盘空间，但搜索和下载速度较慢。

## 错误问题记录一下

### 跨域访问失败

django的`settings.py`已经添加如下内容：

```python
INSTALLED_APPS = [
    'corsheaders',
]
MIDDLEWARE = [
    # 允许跨域请求
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 取消csrf验证
]
# 允许所有网站跨域访问
CORS_ORIGIN_ALLOW_ALL = True
```

> `http://localhost:8000/api/search/` 跨域请求错误
> `http://127.0.0.1:8000/api/search/` 跨域请求正确

### python models的问题

blob或者text不能作为primary_key
> 参考：<https://stackoverflow.com/questions/40646098/django-migration-error-with-mysql-blob-text-column-id-used-in-key-specificati>

### 还需解决的问题
