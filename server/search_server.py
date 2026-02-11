# 处理搜索服务
from utils.qqMusic_parse_util import qq_search_song
from utils.wyyMusic_parse_util import wyy_search_song

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}


def search_song(source, name, page, num):
    if source == 'qq':
        data = qq_search_song(name, page, num)
        return data
    elif source == 'wyy':
        data = wyy_search_song(name, page, num)
        return data
    elif source == 'kugou':
        pass
    elif source == 'kuwo':
        pass
    else:
        pass
