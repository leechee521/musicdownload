import re
import requests
# 从分享链接中提取出url
def extract_url(text):
    # 正则表达式模式，用于匹配常见的URL
    url_pattern = re.compile(r'https?://(?:www\.)?\S+|www\.\S+')
    urls = re.findall(url_pattern, text)
    return urls[0]


def redirect_url(url):
    response = requests.get(url, allow_redirects=False)
    url = response.headers.get('Location')  # 获取重定向的URL
    return url


def ids(ids):
    index = ids.find('id=') + 3
    ids = ids[index:].split('&')[0]
    return ids
