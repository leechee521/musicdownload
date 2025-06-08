# QQ音乐下载工具类
import base64
import json
import re
from datetime import timedelta

import requests
from flask import current_app

from entity.song_info_entity import SongInfo
from utils.artist_uril import getArtists
from utils.config_util import cookie_Config
from utils.lrc_util import merge_lyrics
from utils.time_util import sft

file_config = {
    '128': {'s': 'M500', 'e': '.mp3', 'bitrate': '128kbps'},
    '320': {'s': 'M800', 'e': '.mp3', 'bitrate': '320kbps'},
    'flac': {'s': 'F000', 'e': '.flac', 'bitrate': 'FLAC'},
}
base_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def set_cookies(cookie_str):
    cookies = {}
    for cookie in cookie_str.split('; '):
        key, value = cookie.split('=', 1)
        cookies[key] = value
    return cookies


def get_music_lyric_new(songid):
    config = cookie_Config()
    cookies = set_cookies(config.qq_cookie)
    """从QQ音乐电脑客户端接口获取歌词

    参数:
        songID (str): 音乐id

    返回值:
        dict: 通过['lyric']和['trans']来获取base64后的歌词内容

        其中 lyric为原文歌词 trans为翻译歌词
    """
    # url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    payload = {
        "music.musichallSong.PlayLyricInfo.GetPlayLyricInfo": {
            "module": "music.musichallSong.PlayLyricInfo",
            "method": "GetPlayLyricInfo",
            "param": {
                "trans_t": 0,
                "roma_t": 0,
                "crypt": 0,  # 1 define to encrypt
                "lrc_t": 0,
                "interval": 208,
                "trans": 1,
                "ct": 6,
                "singerName": "",
                "type": 0,
                "qrc_t": 0,
                "cv": 80600,
                "roma": 1,
                "songID": songid,
                "qrc": 0,  # 1 define base64 or compress Hex
                "albumName": "",
                "songName": "",
            },
        },
        "comm": {
            "wid": "",
            "tmeAppID": "qqmusic",
            "authst": "",
            "uid": "",
            "gray": "0",
            "OpenUDID": "",
            "ct": "6",
            "patch": "2",
            "psrf_qqopenid": "",
            "sid": "",
            "psrf_access_token_expiresAt": "",
            "cv": "80600",
            "gzip": "0",
            "qq": "",
            "nettype": "2",
            "psrf_qqunionid": "",
            "psrf_qqaccess_token": "",
            "tmeLoginType": "2",
        },
    }

    # 发送请求获取歌词
    try:
        res = requests.post(base_url, json=payload, cookies=cookies, headers=headers)  # 确保使用 POST 请求
        res.raise_for_status()  # 检查请求是否成功
        d = res.json()  # 解析返回的 JSON 数据

        # 提取歌词数据
        lyric_data = d["music.musichallSong.PlayLyricInfo.GetPlayLyricInfo"]["data"]
        # 处理歌词内容
        if 'lyric' in lyric_data and lyric_data['lyric']:
            # 解码歌词
            lyric = base64.b64decode(lyric_data['lyric']).decode('utf-8')
            tylyric = base64.b64decode(lyric_data['trans']).decode('utf-8')
        else:
            lyric = ''  # 没有歌词的情况下返回空字符串
            tylyric = ''  # 没有歌词的情况下返回空字符串
        return {'lyric': lyric, 'tylyric': tylyric}  # 返回包含歌词的字典

    except Exception as e:
        current_app.logger.info(f"Error fetching lyrics: {e}")
        return {'error': '无法获取歌词'}


def get_music_song(mid, sid):
    """
    获取歌曲信息
    """
    config = cookie_Config()
    cookies = set_cookies(config.qq_cookie)
    if sid != 0:
        # 如果有 songid（sid），使用 songid 进行请求
        req_data = {
            'songid': sid,
            'platform': 'yqq',
            'format': 'json',
        }
    else:
        # 如果没有 songid，使用 songmid 进行请求
        req_data = {
            'songmid': mid,
            'platform': 'yqq',
            'format': 'json',
        }
    song_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg'
    # 发送请求并解析返回的 JSON 数据
    response = requests.post(song_url, data=req_data, cookies=cookies, headers=headers)
    data = response.json()
    # return data
    # 确保数据结构存在，避免索引错误
    if 'data' in data and len(data['data']) > 0:
        song_info = data['data'][0]
        album_info = song_info.get('album', {})
        singers = song_info.get('singer', [])
        singer_names = ', '.join([singer.get('name', 'Unknown') for singer in singers])

        # 获取专辑封面图片 URL
        album_mid = album_info.get('mid')
        img_url = f'https://y.qq.com/music/photo_new/T002R800x800M000{album_mid}.jpg?max_age=2592000' if album_mid else 'https://axidiqolol53.objectstorage.ap-seoul-1.oci.customer-oci.com/n/axidiqolol53/b/lusic/o/resources/cover.jpg'
        # 返回处理后的歌曲信息
        return {
            'name': song_info.get('name', 'Unknown'),
            'album': album_info.get('name', 'Unknown'),
            'singer': singer_names,
            'pic': img_url,
            'mid': song_info.get('mid', mid),
            'id': song_info.get('id', sid)
        }
    else:
        return {'msg': '信息获取错误/歌曲不存在'}


def get_music_url(songmid, level):
    config = cookie_Config()
    cookies = set_cookies(config.qq_cookie)
    """
    获取音乐播放URL
    """
    file_info = file_config[level]
    file = f"{file_info['s']}{songmid}{songmid}{file_info['e']}"

    req_data = {
        'req_1': {
            'module': 'vkey.GetVkeyServer',
            'method': 'CgiGetVkey',
            'param': {
                'filename': [file],
                'guid': '10000',
                'songmid': [songmid],
                'songtype': [0],
                'uin': '0',
                'loginflag': 1,
                'platform': '20',
            },
        },
        'loginUin': '0',
        'comm': {
            'uin': '0',
            'format': 'json',
            'ct': 24,
            'cv': 0,
        },
    }

    response = requests.post(base_url, json=req_data, cookies=cookies, headers=headers)
    data = response.json()
    purl = data['req_1']['data']['midurlinfo'][0]['purl']
    if purl == '':
        # VIP
        return None

    url = data['req_1']['data']['sip'][1] + purl
    prefix = purl[:4]
    bitrate = next((info['bitrate'] for key, info in file_config.items() if info['s'] == prefix), '')

    return {'url': url.replace("http://", "https://"), 'bitrate': bitrate}


# 单首解析 name, album, singer, pic, lyric, music_url, song_fomart, md5_value
def qq_parse_songs(id):
    try:
        # 如果 songmid 是数字，视为 songid (sid)
        sid = int(id)
        mid = 0
    except ValueError:
        # 否则视为 songmid (mid)
        sid = 0
        mid = id
    # 获取歌曲信息
    info = get_music_song(mid, sid)
    lrc = get_music_lyric_new(info['id'])
    lyric = lrc["lyric"]
    tylyric = lrc["tylyric"]
    if tylyric != '' or tylyric is not None:
        lyric = merge_lyrics(lyric, tylyric)

    file_types = ['flac', '320', '128']
    result = []
    for file_type in file_types:
        result = get_music_url(info['mid'], file_type)
        if result is not None:
            break
    try:
        if result['bitrate'].upper() == "FLAC":
            song_fomart = "flac"
        else:
            song_fomart = "mp3"
    except Exception as e:
        return info['name']
    singer = info['singer'].replace(", ", ",")
    if "邓紫棋" in singer:
        singer = singer.replace(". ", ".")
    return info['name'], info['album'], singer, info['pic'], lyric, result['url'], song_fomart


# 歌单解析
def get_song(song_num, playlistid):
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    data = {'comm': {'format': 'json',
                     'inCharset': 'utf-8',
                     'outCharset': 'utf-8',
                     'platform': 'h5', },
            'req_0': {'method': 'uniform_get_Dissinfo',
                      'module': 'music.srfDissInfo.aiDissInfo',
                      'param': {'disstid': int(playlistid),
                                'song_begin': 0,
                                'song_num': song_num}}
            }
    response = requests.post('https://u.y.qq.com/cgi-bin/musicu.fcg', headers=headers, data=json.dumps(data))
    json_txt = json.loads(response.text)
    songs = json_txt["req_0"]["data"]["songlist"]
    playlist_title = json_txt["req_0"]["data"]['dirinfo']['title']
    playlist_id = json_txt["req_0"]["data"]['dirinfo']['id']
    return playlist_id, playlist_title, songs


def get_qq_top_list(id, num):
    url = f"https://i.y.qq.com/n2/m/share/details/toplist.html?ADTAG=ryqq.toplist&type=0&id={id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154'
    }
    resp = requests.get(url, headers)
    text = resp.text
    json_text = json.loads(re.compile('firstPageData\\s=(.*?)\n').findall(text)[0])
    songInfoList = json_text["songInfoList"]
    top_list = []
    for item in songInfoList[0:num]:
        artists = getArtists(item['singer'])
        album_mid = item["album"]["mid"]
        cover = f"https://y.qq.com/music/photo_new/T002R800x800M000{album_mid}.jpg?max_age=2592000"
        song = SongInfo(
            id=item["mid"],
            title=item["name"],
            artist=artists,
            album=item["album"]["name"],
            duration=None,
            source="qq",
            cover_url=cover,
            url=None,
            lyric=None
        )
        top_list.append(song)

    return top_list


def qq_search_song(name, pageNow: int, pageSize: int):
    '''

    :param name:
    :param pageNow:
    :param pageSize:
    :return:
    '''
    url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
    data = {
        "p": int(pageNow),
        'n': int(pageSize),
        "w": name
    }
    response = requests.get(url, params=data)
    if response.status_code != 200:
        return
    html = response.text
    music_json = html[9:-1]
    music_data = json.loads(music_json)  # 转换成 字典
    music_list = music_data['data']['song']['list']
    songs = []
    songCount = 0
    for item in music_list:
        artists = getArtists(item['singer'])
        cover_url = f"https://y.qq.com/music/photo_new/T002R800x800M000{item['albummid']}.jpg?max_age=2592000"
        size = [{"level": "standard", "size": item['size128']}, {"level": "exhigh", "size": item['size320']},
                {"level": "lossless", "size": item['sizeflac']}, ]
        song = SongInfo(
            id=item['songmid'],
            title=item['songname'],
            artist=artists,
            album=item['albumname'],
            duration=item['interval'],
            source="qq",
            cover_url=cover_url,
            url=None,
            lyric=None,
            metadata={"pubtime": sft(item['pubtime']), "size": size}
        )
        songs.append(song.to_dict())
    data = {"songCount": songCount, "songs": songs}
    return data
