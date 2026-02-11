from flask import Blueprint, request, jsonify

from entity.song_entity import PlatformCookie
from extemsions import db

cookie_bp = Blueprint('cookie_router', __name__)


@cookie_bp.route('/get', methods=['GET'])
def get_cookies():
    """获取所有平台的Cookie配置"""
    try:
        qq_config = PlatformCookie.query.filter_by(platform='qqMusic').first()
        wyy_config = PlatformCookie.query.filter_by(platform='wyyMusic').first()
        
        return jsonify({
            "qqMusic": qq_config.cookie if qq_config else "",
            "wyyMusic": wyy_config.cookie if wyy_config else ""
        }), 200
    except Exception as e:
        return jsonify({"msg": f"获取Cookie失败: {str(e)}"}), 500


@cookie_bp.route('/update', methods=['POST'])
def update_cookie():
    """更新指定平台的Cookie"""
    platform = request.json.get('platform')
    cookie = request.json.get('cookie')
    
    if not platform:
        return jsonify({"msg": "platform 参数是必需的"}), 400
    if not cookie:
        return jsonify({"msg": "cookie 参数是必需的"}), 400
    
    try:
        # 查找或创建Cookie配置
        cookie_obj = PlatformCookie.query.filter_by(platform=platform).first()
        if cookie_obj:
            cookie_obj.cookie = cookie
        else:
            cookie_obj = PlatformCookie(platform=platform, cookie=cookie)
            db.session.add(cookie_obj)
        
        db.session.commit()
        return jsonify({"msg": "修改成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"修改失败: {str(e)}"}), 500
