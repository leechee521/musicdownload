from flask import Blueprint, request, jsonify
from server.download_server import parse_by_id
from utils.qqMusic_parse_util import get_music_url, qq_parse_songs, get_music_lyric_new
from utils.wyyMusic_parse_util import url_v1, get_wyy_cookie, parse_cookie, lyric_v1
from utils.lrc_util import merge_lyrics

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
            result = get_music_url(song_id, '320')
            if result and result.get('url'):
                return jsonify({"url": result['url']}), 200
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

@api_bp.route('/get_lyric', methods=['GET'])
def get_lyric():
    """
    获取歌词

    参数:
        song_id: 歌曲ID
        source: 音乐来源 (wyy, qq)
    返回:
        包含歌词的JSON对象
    """
    song_id = request.args.get('song_id')
    source = request.args.get('source')

    if not song_id or not source:
        return jsonify({"error": "缺少必要参数"}), 400

    try:
        if source == 'qq':
            # 获取QQ音乐歌词
            lrc = get_music_lyric_new(song_id)
            if 'error' in lrc:
                return jsonify({"lyric": ""}), 200

            lyric = lrc.get("lyric", "")
            tylyric = lrc.get("tylyric", "")

            # 合并原文和翻译歌词
            if tylyric:
                lyric = merge_lyrics(lyric, tylyric)

            return jsonify({"lyric": lyric}), 200

        elif source == 'wyy':
            # 获取网易云音乐歌词
            cookies = parse_cookie(get_wyy_cookie())
            lyricv1 = lyric_v1(song_id, cookies)

            if lyricv1.get('lrc'):
                lyric = lyricv1['lrc'].get('lyric', '')
                translated_lyrics = lyricv1.get('tlyric', {}).get('lyric', '')

                # 合并原文和翻译歌词
                if translated_lyrics:
                    lyric = merge_lyrics(lyric, translated_lyrics)

                return jsonify({"lyric": lyric}), 200
            else:
                return jsonify({"lyric": ""}), 200
        else:
            return jsonify({"error": "不支持的音乐来源"}), 400
    except Exception as e:
        print(f"获取歌词失败: {str(e)}")
        return jsonify({"lyric": ""}), 200
