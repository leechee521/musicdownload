from flask import Blueprint, render_template, jsonify

from utils.search_util import search_song

search_bp = Blueprint("search_router", __name__)

@search_bp.route('/<source>/<name>/<pageNow>/<pageSize>', methods=['GET', 'POST'])
def search_name(source, name, pageNow, pageSize):
    data = search_song(source, name, pageNow, pageSize)
    if data is not None:
        return jsonify({"msg": "搜索成功", "data": data})
    else:
        return jsonify({"msg": "搜索失败", "data": None})
