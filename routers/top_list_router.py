from flask import Blueprint, jsonify, request

from common.response import MyResponse
from entity.song_top_list_entity import SongTopList
from utils.qqMusic_parse_util import get_qq_top_list
from utils.wyyMusic_parse_util import get_wyy_top_list

top_list_bp = Blueprint('top_list_router', __name__, url_prefix='/top_list')

wyy_list = [
    {"name": "网易云-热歌榜", "id": 3778678},
    {"name": "网易云-新歌榜", "id": 3779629},
    {"name": "网易云-飙升榜", "id": 19723756}
]
qq_list = [
    {"name": "QQ音乐-热歌榜", "id": 26},
    {"name": "QQ音乐-新歌榜", "id": 27},
    {"name": "QQ音乐-飙升榜", "id": 62}
]


@top_list_bp.route('/wyy', methods=['GET'])
def get_wyy_list():
    data = []
    # 获取网易云热门歌单
    for item in wyy_list:
        data.append(
            SongTopList.from_dict(
                {"source": "wyy", "title": item["name"], "songs": get_wyy_top_list(item["id"], 10), "id": item["id"]}))
    return jsonify(MyResponse.ok("获取成功", data=data)), 200


@top_list_bp.route('/qq', methods=['GET'])
def get_qq_list():
    data = []
    for item in qq_list:
        data.append({"source": "qq", "title": item["name"], "songs": get_qq_top_list(item["id"], 10), "id": item["id"]})
    return jsonify(MyResponse.ok("获取成功", data=data)), 200
@top_list_bp.route('/playlist/more', methods=['GET'])
def get_more_playlist():
    data = []
    id = request.args.get('id')
    source = request.args.get('source')
    if source == 'wyy':
        data.append({"source": "wyy", "songs": get_wyy_top_list(id, 200)})
    elif source == 'qq':
        data.append({"source": "qq", "songs": get_qq_top_list(id, 100)})
    return jsonify(MyResponse.ok("获取成功", data=data)), 200


@top_list_bp.route('/kugou', methods=['GET'])
def get_kugou_list():
    data = []
    for item in qq_list:
        data.append({"source": "qq", "title": item["name"], "songs": get_qq_top_list(item["id"], 10)})
    return jsonify(MyResponse.ok("获取成功", data=data)), 200


@top_list_bp.route('/kuwo', methods=['GET'])
def get_kuwo_list():
    data = []
    for item in qq_list:
        data.append({"source": "qq", "title": item["name"], "songs": get_qq_top_list(item["id"], 10)})
    return jsonify(MyResponse.ok("获取成功", data=data)), 200