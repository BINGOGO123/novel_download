from .module.Downloader import Downloader

# 搜索目录，names是str或者list，例如：
# "三国演义"
# ["三国演义","水浒传"]
def search_novel(names):
  downloader = Downloader()
  content = downloader.download_catalog(names)
  return content

def download_novel(url):
  downloader = Downloader()
  content = downloader.download_novel(url)
  return content
