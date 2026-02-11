from flask import Blueprint, request, jsonify
from server.download_server import parse_by_id
from utils.qqMusic_parse_util import get_music_url, qq_parse_songs
from utils.wyyMusic_parse_util import url_v1, get_wyy_cookie, parse_cookie

api_bp = Blueprint('api_router', __name__, url_prefix='/api', static_folder='static', template_folder='templates')

@api_bp.route('/parse_song_url', methods=['GET'])
def parse_song_url():
    """
    解析歌曲真实播放地址
    
    参数:
        song_id: 歌曲ID
        source: 音乐来源 (wyy, qq)
    返回:
        包含音乐URL的JSON对象
    """
    song_id = request.args.get('song_id')
    source = request.args.get('source')
    
    if not song_id or not source:
        return jsonify({"error": "缺少必要参数"}), 400
    
    try:
        if source == 'qq':
            # 解析QQ音乐
            music_url = get_music_url(song_id, '320')
            if music_url:
                return jsonify({"url": music_url}), 200
            else:
                return jsonify({"error": "获取QQ音乐URL失败，可能是VIP歌曲"}), 400
        elif source == 'wyy':
            # 解析网易云音乐
            cookies = parse_cookie(get_wyy_cookie())
            urlv1 = url_v1(song_id, 'standard', cookies)
            if urlv1['code'] == 200 and urlv1['data'][0]['url']:
                return jsonify({"url": urlv1['data'][0]['url']}), 200
            else:
                return jsonify({"error": "获取网易云音乐URL失败"}), 400
        else:
            return jsonify({"error": "不支持的音乐来源"}), 400
    except Exception as e:
        print(f"解析歌曲URL失败: {str(e)}")
        return jsonify({"error": "解析歌曲URL失败"}), 500
