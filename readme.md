# 说明

多站小说下载器，使用实时爬虫搜索和下载多个网站的小说内容，每次搜索和下载都会进行多次爬取，因此能够实时抓取小说网站的内容，且不占用服务器的硬盘空间，但搜索和下载速度较慢。

前端通过@vue/cli搭建脚手架实现

后端使用django框架开发，使用mysql数据库和redis内存数据库

## 文件说明

```
novel_download
│   readme.md
│   manage.py
|
└───novel_download -- django初始配置目录
|   |   ...
│
└───backend -- 后端api应用
│   │   ...
|
└───spider -- 爬虫代码
│   │   ...
│   
└───frontpage -- 前端app代码，即@vue/cli脚手架目录
|   |   ...
|   └───dist -- 根据配置文件，打包后的文件必须直接放在这个目录下
|
└───config -- 所有配置文件
|   |   config.py
|   |   logger.py -- 日志类
|   |   Redis.py -- redis连接管理
|
└───logs -- 日志目录
|   |   ...
|
└───media -- 媒体文件目录，存放临时下载的小说
	|   ...
```

## 快速开始

确保安装了**python3** **@vue/cli**，同时启动mysql服务器和redis服务器

修改**novel_download/novel_download/settings.py**中的**DATABASES**项以更改数据库相关配置

修改**novel_download/config/Redis.py**以更改redis数据库相关配置

1. clone并运行django服务器
   
   ```shell
   $ git clone ...
   $ cd novel_download
   $ pip install -r requirements.txt
   
   $ python manage.py makemigrations
   $ python manage.py migrade
   $ python manage.py runserver
   ```

2. 运行vue服务器
   
   ``` shell
   $ cd frontpage
   $ npm install
   $ npm run serve
   ```

3. 打开网址<http://127.0.0.1:8080/novel_download_static/#/>进行访问
   
   > 注意不能访问<http://localhost:8080/novel_download_static/#/>，这种方式访问不能正常设置cookie，暂时不清楚原因

## 部署

若要部署到服务器，需要修改前后端各个接口以及配置，打包前端app等。

该应用目前尚未部署。

## 错误问题记录

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

### flex-shrink和flex-grow

关于这两个属性一定要好好注意一下，`flex-shrink`不指定的话，当父亲元素在主轴上溢出时，该元素就会缩小，即使设定了该元素的大小依然会缩小，因此会导致一些意外的情况，出现这个问题就要考虑是否设置了`flex-shrink:0`了。

`flex-grow`与它相反是扩充的意思，这个倒是问题不大。

### python models的问题

blob或者text不能作为primary_key
> 参考：<https://stackoverflow.com/questions/40646098/django-migration-error-with-mysql-blob-text-column-id-used-in-key-specificati>

## 接口说明

1. search

   ```javascript
   // 搜索正确
   {
     status:0,
     //如果没有多个网站源信息，result可以是单项而不是Array
     result:[
       {
         source_name:"笔趣看",
         // 资源网站网址
         source_url:"www.baidu.com",
         // 网站图片网址，可以没有
         source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png",
         // 表示搜索结果是否为空，如果为空，那么下面的内容都不需要
         status:0,
         empty:false,
         // 表示是否已经达到结束的地方
         end:false,
         // 表示搜索结果总数
         length:100,
         // 搜索的结果列表
         content:[
           {
             name:"三国演义",
             introduction:["name:三国演义","introduction:三国演义"],
             // 源网页网址
             download_url:"www.baidu.com",
             imageList:[
               "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1592159453680&di=edb8f09c8fb193dbba6bde8dd6f24a6d&imgtype=0&src=http%3A%2F%2Fimage.gqjd.net%2Fimage%2F2009-12%2F72712457221.jpg",
               "http://image.gqjd.net/image/2009-12/57295513513.jpg"
             ]
           }
         ]
       },
       // 搜索为空的结果
       {
         source_name:"笔趣看",
         source_url:"www.biqukan.com",
         source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png",
         status:0,
         empty:true,
         // 显示的福利图片网址
         url:"http://www.xinhuanet.com/video/2020-01/26/1210452637_15800000011261n.jpg"
       },
       // 搜索单项出现错误
       {
         source_name:"笔趣看",
         source_url:"www.baidu.com",
         source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png",
         status:1,
         information:"出现错误"
       }
     ]
   }
   // 搜索错误
   {
     status:1,
     information:"出现错误"
   }
   //没有任何信息
   {
     status:1,
     // 显示的福利图片网址
     result:{
       "empty":false,
       "url":"www.bingoz.cn"
     }
   }
   ```

2. getMore

   ```javascript
   {
     status:0,
     result:{
       "source_name":"笔趣看",
       "end":false,
       // 与search的content格式相同
       "content"[]
     }
   }
   // 出现错误
   {
     status:1,
     information:"错误原因"
   }
   ```

3. download

   ```javascript
   // 正在下载，尚不清楚进度
   {
     status:0,
     percent:false
   }
   // 正在下载，清楚进度
   {
      status:0,
      percent:"37/183"
   }
   // 下载完毕
   {
      status:0,
      // 文件临时网址
      result:"www.bingoz.cn"
   }
   // 出现错误
    {
      status:1,
      information:"错误原因"
    }
   ```
