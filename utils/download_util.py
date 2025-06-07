# todo 如果qq音乐下载不成功，就去网易云音乐下载，反之网易云没有版权就去qq音乐查找。
import os
import uuid

import requests
from flask import current_app

from entity.song_entity import Song
from utils.md5_util import md5_hash
from utils.mutagen_util import update_metadata
from extemsions import db


def download_song(name, album, singer, music_url, song_type):
    path = os.path.join(".", "downloads", singer, album)
    os.makedirs(path, exist_ok=True)
    final_path = os.path.join(path, "{}.{}".format(name, song_type))
    response = requests.get(music_url)
    if response.status_code == 200:
        with open(final_path, 'wb') as f:
            f.write(response.content)
            return final_path
    else:
        return None


def download_cover(url, temp_dir):
    """
    从 URL 下载封面图片并保存为临时文件。
    每个线程使用唯一的临时文件名。
    """
    try:
        # 确保临时目录存在
        os.makedirs(temp_dir, exist_ok=True)

        # 生成唯一的临时文件名
        temp_file = os.path.join(temp_dir, f"cover_{uuid.uuid4().hex}.jpg")

        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return temp_file
    except Exception as e:
        current_app.logger.info(f"下载封面时出错: {e}")
        return None


# 主要下载工具类
def download_song_main(name, album, singer, pic, lyric, music_url, song_fomart, md5_value, size):
    # 查询数据库
    if md5_value is not None:
        if Song.query.filter_by(md5=md5_value).first() is not None:
            current_app.logger.info(f"文件《{name}-{singer}.{song_fomart}》已存在")
            return
    song = Song.query.filter_by(name=name, artist=singer).first()
    if song is not None:
        #  比较文件大小（优先下载高品质）
        if int(song.size) > size:
            current_app.logger.info(f"高品质文件《{name}-{singer}.{song.music_type}》已存在")
            return
        else:
            path = os.path.join(".","downloads", song.artist, song.album)
            os.remove(os.path.join(path, "{}.{}".format(name, song.music_type)))
    # 下载文件
    file_path = None
    try:
        file_path = download_song(name, album, singer, music_url, song_fomart)
        if md5_value is None:
            md5_value = md5_hash(file_path)
        if size == 0:
            size = os.stat(file_path).st_size
    except Exception as e:
        current_app.logger.info(e)
    if file_path is None:
        return
    # 下载封面
    cover_path = None
    try:
        temp_dir = os.path.join(os.path.join(".", "temp"))
        cover_path = download_cover(pic, temp_dir)
    except Exception as e:
        current_app.logger.info(e)

    # 写入元数据
    update_metadata(file_path, name, singer, album, lyric, cover_path)

    # 写入数据库
    if song is None:
        # 新增
        db.session.add(
            Song(name=name, artist=singer, album=album, cover=pic, lyric=lyric, url=music_url,
                 music_type=song_fomart, md5=md5_value, size=size))
        current_app.logger.info(f"《{name}-{singer}.{song_fomart}》文件已下载")
    else:
        # 更新
        song.name = name
        song.artist = singer
        song.album = album
        song.cover = pic
        song.lyric = lyric
        song.music_url = music_url
        song.music_type = song_fomart
        song.md5 = md5_value
        song.size = size
    db.session.commit()
