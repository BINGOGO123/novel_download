# 错误问题记录一下

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
> 
> `http://127.0.0.1:8000/api/search/` 跨域请求正确

## 需要解决的问题

1. 每一项前面加上标号
2. 加上回到顶部按钮
3. 文本字体调整

## 小错误

blob或者text不能作为primary_key
> 参考：<https://stackoverflow.com/questions/40646098/django-migration-error-with-mysql-blob-text-column-id-used-in-key-specificati>