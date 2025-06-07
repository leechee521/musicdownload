import re
from datetime import datetime

import requests
from flask import current_app

from utils.download_util import download_song_main
from utils.qqMusic_parse_util import qq_parse_songs, get_song, get_music_song
from utils.wyyMusic_parse_util import wyy_parse_songs, wyy_parse_playlist
from extemsions import socketio


# 从分享链接中提取出url
def extract_url(text):
    # 正则表达式模式，用于匹配常见的URL
    url_pattern = re.compile(r'https?://(?:www\.)?\S+|www\.\S+')
    urls = re.findall(url_pattern, text)
    return urls[0]


def redirect_url(url):
    response = requests.get(url, allow_redirects=False)
    url = response.headers.get('Location')  # 获取重定向的URL
    return url


def ids(ids):
    index = ids.find('id=') + 3
    ids = ids[index:].split('&')[0]
    return ids


# 判单链接是哪个平台的
def parse_url(url, level):
    url = extract_url(url)

    # QQ
    # 如果URL中包含 'c6.y.qq.com'，则发送请求获取重定向后的URL
    if 'c6.y.qq.com' in url:
        url = redirect_url(url)

    # 检查重定向后的URL中是否包含 'y.qq.com'，并根据情况提取 id
    # https://y.qq.com/n/ryqq/songDetail/001NgljR0RUhy1
    if 'y.qq.com' in url:
        current_app.logger.info(f"qq音乐正在下载{url}")
        socketio.emit('activities', {
            "content": 'QQ音乐收到下载',
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": 'success',
            "icon": 'el-icon-check'
        })
        if '/songDetail/' in url:
            # 单曲下载
            index = url.find('/songDetail/') + len('/songDetail/')
            song_id = url[index:].split('/')[0]  # 提取 '/songDetail/' 后面的部分
            name, album, singer, pic, lyric, music_url, song_fomart = qq_parse_songs(song_id)
            socketio.emit('activities', {
                "content": f"《{name}-{singer}》正在下载...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'primary',
                "icon": 'el-icon-download'
            })
            download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, None, 0)
            socketio.emit('activities', {
                "content": f"《{name}-{singer}.{song_fomart}》下载成功",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'success',
                "icon": 'el-icon-download'
            })
            return

        # 歌单 处理 /playlist/ 形式的 URL
        if '/playlist/' in url:
            socketio.emit('activities', {
                "content": '正在解析QQ音乐歌单...',
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'primary',
                "icon": 'el-icon-loading'
            })
            index = url.find('/playlist/') + len('/playlist/')
            playlist_id = url[index:].split('/')[0]  # 提取 '/songDetail/' 后面的部分
            songs = get_song(2000, playlist_id)
            if len(songs) == 0:
                return

            playlist_len = len(songs)
            socketio.emit('activities', {
                "content": f'歌单解析成功,歌单包含{playlist_len}首音乐',
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'success',
                "icon": 'el-icon-check'
            })
            for index, song in enumerate(songs):
                name = album = singer = pic = lyric = music_url = song_fomart = None
                try:
                    name, album, singer, pic, lyric, music_url, song_fomart = qq_parse_songs(song["id"])
                except Exception as e:
                    name = qq_parse_songs(song["id"])
                    socketio.emit('activities', {
                        "content": f"《{name}-{singer}》下载失败",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 'primary',
                        "icon": 'el-icon-close'
                    })
                if music_url is not None:
                    socketio.emit('activities', {
                        "content": f"《{name}-{singer}》正在下载...",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 'primary',
                        "icon": 'el-icon-download'
                    })
                    download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, None, 0)
                    # 发送进度
                    progress = (index + 1) / playlist_len
                    progress = round(progress * 100, 2)

                    socketio.emit('progress_update', {'progress': progress})
                    socketio.emit('activities', {
                        "content": f"《{name}-{singer}.{song_fomart}》下载成功",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 'success',
                        "icon": 'el-icon-download'
                    })
            return
        # 歌单 处理 /details/的url
        if "/details/" in url:
            socketio.emit('activities', {
                "content": '正在解析QQ音乐歌单...',
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'primary',
                "icon": 'el-icon-loading'
            })
            index = url.find('id=') + 3
            playlist_id = url[index:].split('&')[0]  # 提取 'id' 的值
            songs = get_song(2000, playlist_id)
            if len(songs) == 0:
                return

            playlist_len = len(songs)
            socketio.emit('activities', {
                "content": f'歌单解析成功,歌单包含{playlist_len}首音乐',
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'success',
                "icon": 'el-icon-check'
            })
            for index, song in enumerate(songs):
                name = album = singer = pic = lyric = music_url = song_fomart = None
                try:
                    name, album, singer, pic, lyric, music_url, song_fomart = qq_parse_songs(song["id"])
                except Exception as e:
                    name = qq_parse_songs(song["id"])
                    socketio.emit('activities', {
                        "content": f"《{name}-{singer}》下载失败",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 'primary',
                        "icon": 'el-icon-close'
                    })
                if music_url is not None:
                    socketio.emit('activities', {
                        "content": f"《{name}-{singer}》正在下载...",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 'primary',
                        "icon": 'el-icon-download'
                    })
                    download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, None, 0)
                    # 发送进度
                    progress = (index + 1) / playlist_len
                    progress = round(progress * 100, 2)

                    socketio.emit('progress_update', {'progress': progress})
                    socketio.emit('activities', {
                        "content": f"《{name}-{singer}.{song_fomart}》下载成功",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 'success',
                        "icon": 'el-icon-download'
                    })
            return
        if 'songmid=' in url:
            index = url.find('songmid=') + 8
            song_id = url[index:].split('&')[0]  # 提取 'id' 的值
            if "#" in song_id:
                song_id = song_id[:song_id.index("#")]
            name, album, singer, pic, lyric, music_url, song_fomart = qq_parse_songs(song_id)
            socketio.emit('activities', {
                "content": f"《{name}-{singer}》正在下载...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'primary',
                "icon": 'el-icon-download'
            })
            download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, None, 0)
            socketio.emit('activities', {
                "content": f"《{name}-{singer}.{song_fomart}》下载成功",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'success',
                "icon": 'el-icon-download'
            })
            return
        if 'id=' in url:
            index = url.find('id=') + 3
            song_id = url[index:].split('&')[0]  # 提取 'id' 的值
            if "#" in song_id:
                song_id = song_id[:song_id.index("#")]
            name, album, singer, pic, lyric, music_url, song_fomart = qq_parse_songs(song_id)
            download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, None, 0)
            return

    if "163cn.tv" in url:
        url = redirect_url(url)
    if "music.163.com" in str(url):
        current_app.logger.info(f"网易云正在下载{url}")
        socketio.emit('activities', {
            "content": '网易云收到下载',
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": 'success',
            "icon": 'el-icon-check'
        })
        if "song" in url:
            # 单曲下载
            name, album, singer, pic, lyric, music_url, song_fomart, md5_value, size = wyy_parse_songs(ids(url), level)
            socketio.emit('activities', {
                "content": f"《{name}-{singer}》正在下载...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'primary',
                "icon": 'el-icon-download'
            })
            download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, md5_value, size)
            socketio.emit('activities', {
                "content": f"《{name}-{singer}.{song_fomart}》下载成功",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'success',
                "icon": 'el-icon-download'
            })
        elif "id" in url:
            socketio.emit('activities', {
                "content": '正在解析网易云歌单...',
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'primary',
                "icon": 'el-icon-loading'
            })
            playlist = wyy_parse_playlist(ids(url), level)
            socketio.emit('activities', {
                "content": f'歌单解析成功,歌单包含{len(playlist)}首音乐',
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": 'success',
                "icon": 'el-icon-check'
            })
            current_app.logger.info(f"{url}解析完成")
            playlist_len = len(playlist)
            for index, song in enumerate(playlist):
                name, album, singer, pic, lyric, music_url, song_fomart, md5_value, size = song
                socketio.emit('activities', {
                    "content": f"《{name}-{singer}》正在下载...",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": 'primary',
                    "icon": 'el-icon-download'
                })
                download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, md5_value, size)
                # 发送进度
                progress = (index + 1) / playlist_len
                progress = round(progress * 100, 2)

                socketio.emit('progress_update', {'progress': progress})
                socketio.emit('activities', {
                    "content": f"《{name}-{singer}.{song_fomart}》下载成功",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": 'success',
                    "icon": 'el-icon-download'
                })
