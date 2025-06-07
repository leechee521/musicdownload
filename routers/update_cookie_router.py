from flask import Blueprint, request, jsonify

from utils.config_util import cookie_Config

cookie_bp = Blueprint('cookie_router', __name__)


@cookie_bp.route('/update', methods=['POST'])
def update_cookie():
    platform = request.json.get('platform')
    cookie = request.json.get('cookie')
    if not platform:
        return jsonify({"msg": "platform 参数是必需的"}), 400
    level = request.json.get('cookie')
    if not level:
        return jsonify({"msg": "cookie 参数是必需的"}), 400
    config = cookie_Config()
    flat = config.update_cookie(platform, cookie)
    if flat:
        return jsonify({"msg": "修改成功"}), 200
    else:
        return jsonify({"msg": "修改失败"}), 200
