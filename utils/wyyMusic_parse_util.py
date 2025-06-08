# 网易云下载工具类
import json
import urllib
from datetime import timedelta
from hashlib import md5
from random import randrange

import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import current_app

from entity.song_info_entity import SongInfo
from utils.artist_uril import getArtists
from utils.config_util import cookie_Config
from utils.lrc_util import merge_lyrics
from utils.time_util import sft


def HexDigest(data):
    return "".join([hex(d)[2:].zfill(2) for d in data])


def HashDigest(text):
    return md5(text.encode("utf-8")).digest()


def HashHexDigest(text):
    return HexDigest(HashDigest(text))


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
    'Referer': '',
}


# 解析cookie
def parse_cookie(text: str):
    try:
        cookie_ = [item.strip().split('=', 1) for item in text.strip().split(';') if item]
        return {k.strip(): v.strip() for k, v in cookie_}
    except Exception as e:
        current_app.logger.info("网易云Cookie 解析错误")
        current_app.logger.info(e)


def post(url, params, cookie):
    cookies = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!"
    }
    cookies.update(cookie)
    response = requests.post(url, headers=headers, cookies=cookies, data={"params": params})
    return response.text


def url_v1(id, level, cookies):
    url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    AES_KEY = b"e82ckenh8dichen8"
    config = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!",
        "requestId": str(randrange(20000000, 30000000))
    }

    payload = {
        'ids': [id],
        'level': level,
        'encodeType': 'flac',
        'header': json.dumps(config),
    }

    if level == 'sky':
        payload['immerseType'] = 'c51'

    url2 = urllib.parse.urlparse(url).path.replace("/eapi/", "/api/")
    digest = HashHexDigest(f"nobody{url2}use{json.dumps(payload)}md5forencrypt")
    params = f"{url2}-36cd479b6b5-{json.dumps(payload)}-36cd479b6b5-{digest}"
    padder = padding.PKCS7(algorithms.AES(AES_KEY).block_size).padder()
    padded_data = padder.update(params.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB())
    encryptor = cipher.encryptor()
    enc = encryptor.update(padded_data) + encryptor.finalize()
    params = HexDigest(enc)
    response = post(url, params, cookies)
    return json.loads(response)


def name_v1(id):
    urls = "https://interface3.music.163.com/api/v3/song/detail"
    data = {'c': json.dumps([{"id": id, "v": 0}])}
    response = requests.post(url=urls, data=data)
    return response.json()


def lyric_v1(id, cookies):
    url = "https://interface3.music.163.com/api/song/lyric"
    data = {'id': id, 'cp': 'false', 'tv': '0', 'lv': '0', 'rv': '0', 'kv': '0', 'yv': '0', 'ytv': '0', 'yrv': '0'}
    response = requests.post(url=url, data=data, cookies=cookies)
    return response.json()


# 获取歌单id
def get_playlist(id):
    url_api = "https://oiapi.net/API/NeteasePlaylistDetail?id=" + id
    id_list = []

    response = requests.get(url_api, headers)
    playlist = json.loads(response.text)
    if playlist["code"] == 1:
        data = playlist["data"]
        for item in data:
            id_list.append(item["id"])
    return id_list


# 歌单解析
def wyy_parse_playlist(playlist_id, level):
    id_list = get_playlist(playlist_id)
    playlist = []
    for id in id_list:
        song = wyy_parse_songs(id, level)
        if song is not None:
            playlist.append(song)
    return playlist


# https://music.163.com/song?id=1367333358
# 解析出 name, album, singer, pic, lyric, music_url, song_fomart, md5_value
def wyy_parse_songs(id, level):
    config = cookie_Config()
    cookies = parse_cookie(config.wyy_cookie)
    urlv1 = url_v1(id, level, cookies)
    # 判断code是否为200
    if urlv1['code'] == 200:
        namev1 = name_v1(urlv1['data'][0]['id'])
    else:
        # 解析异常
        return
    lyricv1 = lyric_v1(urlv1['data'][0]['id'], cookies)
    if urlv1['data'][0]['url'] is not None:
        if namev1['songs']:
            song_url = urlv1['data'][0]['url']
            song_name = namev1['songs'][0]['name']
            song_album = namev1['songs'][0]['al']['name']
            song_md5 = urlv1['data'][0]['md5']

            song_fomart = urlv1['data'][0]['type']
            song_picUrl = namev1['songs'][0]['al']['picUrl']
            size = urlv1['data'][0]['size']

            lyric = lyricv1['lrc']['lyric'],
            lyric = lyric[0]
            translated_lyrics = lyricv1.get('tlyric', {}).get('lyric', None)
            if translated_lyrics is not None:
                lyric = merge_lyrics(lyric, translated_lyrics)

            artist_names = []
            song_artist = None
            for song in namev1['songs']:
                ar_list = song['ar']
                if len(ar_list) > 0:
                    artist_names.append(','.join(ar['name'] for ar in ar_list))
                song_artist = ', '.join(artist_names)
            return song_name, song_album, song_artist, song_picUrl, lyric, song_url, song_fomart, song_md5, size


def wyy_search_song(id):
    config = cookie_Config()
    cookies = parse_cookie(config.wyy_cookie)
    urlv1 = url_v1(id, "lossless", cookies)
    # 判断code是否为200
    if urlv1['code'] == 200:
        namev1 = name_v1(urlv1['data'][0]['id'])
    else:
        # 解析异常
        return
    if urlv1['data'][0]['url'] is not None:
        if namev1['songs']:
            song_url = urlv1['data'][0]['url']
            song_picUrl = namev1['songs'][0]['al']['picUrl']
            size = urlv1['data'][0]['size']
            return song_picUrl, song_url, size


def get_wyy_top_list(id, num):
    url_api = f"https://oiapi.net/API/NeteasePlaylistDetail?id={id}"

    top_list = []

    response = requests.get(url_api, headers)
    playlist = json.loads(response.text)
    if playlist["code"] == 1:
        data = playlist["data"]
        for item in data[0:num]:
            artists = getArtists(item['artists'])
            song = SongInfo(
                id=item["id"],
                title=item["name"],
                artist=artists,
                album=item["album"]["name"],
                duration=None,
                source="wyy",
                cover_url=item["album"]["cover"],
                url=item["url"],
                lyric=None
            )
            top_list.append(song)
    return top_list


def wyy_search_song(name, pageSize):
    '''

    :param name:
    :param pageSize:
    :return:
    '''

    url = 'https://music.163.com/api/cloudsearch/pc'
    data = {'s': name, 'type': 1, 'limit': pageSize}
    response = requests.post(url, data=data, headers=headers)
    result = response.json()
    songCount = result['result']['songCount']
    songs = []
    for item in result.get('result', {}).get('songs', []):
        seconds, milliseconds = divmod(item['dt'], 1000)
        size = []
        if item.get('l') is not None:
            if item['l'].get('size') is not None:
                size.append({"level": "standard", "size": item['l']["size"]})
        if item.get('h') is not None:
            if item['h'].get('size') is not None:
                size.append({"level": "exhigh", "size": item['h']["size"]})
        if item.get('sq') is not None:
            if item['sq'].get('size') is not None:
                size.append({"level": "lossless", "size": item['sq']["size"]})

        song = SongInfo(
            id=item['id'],
            title=item['name'],
            artist='/'.join(artist['name'] for artist in item['ar']),
            album=item['al']['name'],
            duration=seconds,
            source="wyy",
            cover_url=item['al']['picUrl'],
            url=None,
            lyric=None,
            metadata={"pubtime": sft(item['publishTime'] / 1000), "size": size}
        )
        songs.append(song.to_dict())
    data = {"songCount": songCount, "songs": songs}
    return data
