# 处理url
import os
import re
from datetime import datetime

import requests
from flask import current_app

from extemsions import socketio
from utils.download_util import download_song_main
from utils.m3u_util import SimpleM3UGenerator
from utils.qqMusic_parse_util import get_song, qq_parse_songs
from utils.url_util import extract_url, redirect_url, ids
from utils.wyyMusic_parse_util import wyy_parse_playlist, wyy_parse_songs

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
    'Referer': '',
}


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
            sg = SimpleM3UGenerator()
            playlist_id, playlist_title, songs = get_song(2000, playlist_id)
            sg.playlist_title = playlist_title
            sg.playlist_id = playlist_id
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
                    path = os.path.join("/", "music", singer, album, name + "." + song_fomart)
                    sg.add_song(singer, name, path)
            sg.save("qq")
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
            sg = SimpleM3UGenerator()
            playlist_id, playlist_title, songs = get_song(2000, playlist_id)
            sg.playlist_title = playlist_title
            sg.playlist_id = playlist_id
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
                    path = os.path.join("/", "music", singer, album, name + "." + song_fomart)
                    sg.add_song(singer, name, path)
            sg.save("qq")
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
            id = ids(url)
            sg = SimpleM3UGenerator()
            sg.playlist_id = id
            sg.playlist_title = re.search(r"<title>(.+)</title>", requests.get(f"http://music.163.com/playlist?id={id}",
                                                                               headers=headers).text).group(1)[:-13]
            playlist = wyy_parse_playlist(id, level)
            # sg.playlist_title = playlist_title
            # sg.playlist_id = playlist_id

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
                path = os.path.join("/", "music", singer, album, name + "." + song_fomart)
                sg.add_song(singer, name, path)
            sg.save("wyy")
