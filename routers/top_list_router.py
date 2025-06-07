from flask import Blueprint, jsonify

from common.response import MyResponse
from entity.song_top_list_entity import SongTopList
from utils.qqMusic_parse_util import get_qq_top_list
from utils.wyyMusic_parse_util import get_wyy_top_list

top_list_bp = Blueprint('top_list_router', __name__, url_prefix='/top_list')


@top_list_bp.route('/', methods=['GET'])
def get_top_list():
    data = []
    # 获取网易云热门歌单
    wyy_top_list = get_wyy_top_list(3778678, 10)
    data.append(SongTopList.from_dict({"source": "wyy", "title": "网易云-热歌榜", "songs": wyy_top_list}))
    wyy_new_list = get_wyy_top_list(3779629, 10)
    data.append(SongTopList.from_dict({"source": "wyy", "title": "网易云-新歌榜", "songs": wyy_new_list}))
    wyy_bs_list = get_wyy_top_list(19723756, 10)
    data.append(SongTopList.from_dict({"source": "wyy", "title": "网易云-飙升榜", "songs": wyy_bs_list}))
    # qq_top_list = get_qq_top_list(26, 10)
    # data.append({"source": "qq", "title": "QQ音乐-热歌榜", "song_list": qq_top_list})
    # qq_popular_list = get_qq_top_list(4, 10)
    # data.append({"source": "qq", "title": "QQ音乐-流行榜", "song_list": qq_popular_list})
    # qq_bs_list = get_qq_top_list(62, 10)
    # data.append({"source": "qq", "title": "QQ音乐-飙升榜", "song_list": qq_bs_list})
    # qq_tgsq_list = get_qq_top_list(67, 10)
    # data.append({"source": "qq", "title": "QQ音乐-听歌识曲榜", "song_list": qq_tgsq_list})
    # qq_new_list = get_qq_top_list(27, 10)
    # data.append({"source": "qq", "title": "QQ音乐-新歌榜", "song_list": qq_new_list})
    return jsonify(MyResponse.ok("获取成功", data=data)), 200
