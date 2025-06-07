from flask import request, jsonify, Blueprint, current_app, render_template

from server.download_server import parse_url

download_bp = Blueprint("download_router", __name__)


@download_bp.route('/', methods=['GET'])
def home():
    return render_template("download.html")


@download_bp.route('/', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({"msg": "url 参数是必需的"}), 400
    level = request.json.get('level')
    if not level:
        return jsonify({"msg": "level 参数是必需的"}), 400
    current_app.logger.info(f"{url}正在解析下载")
    parse_url(url, level)
    return jsonify({"msg": "下载成功"}), 200
