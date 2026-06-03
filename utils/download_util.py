import os
import tempfile
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


def download_cover(url, temp_dir=None):
    """
    从 URL 下载封面图片并保存为临时文件。

    参数:
        url (str): 封面图片的URL
        temp_dir (str, optional): 临时目录路径。如果为None，则使用系统默认临时目录

    返回:
        str: 临时文件路径。如果失败则返回None
    """
    try:
        # 确保临时目录存在
        if temp_dir:
            os.makedirs(temp_dir, exist_ok=True)

        # 创建临时文件（自动生成唯一文件名）
        with tempfile.NamedTemporaryFile(
                suffix=".jpg",
                prefix="cover_",
                dir=temp_dir,
                delete=False  # 不自动删除，因为我们还要使用这个文件
        ) as temp_file:
            temp_path = temp_file.name

        # 下载封面图片
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()  # 检查请求是否成功

        # 写入临时文件
        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤掉保持连接的新块
                    f.write(chunk)

        current_app.logger.debug(f"封面下载成功，保存到临时文件: {temp_path}")
        return temp_path

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"下载封面请求失败: {e}")
        # 如果创建了临时文件但下载失败，尝试删除
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                current_app.logger.warning(f"删除临时封面文件失败: {e}")
        return None
    except Exception as e:
        current_app.logger.error(f"下载封面时发生意外错误: {e}", exc_info=True)
        # 同上，清理临时文件
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                current_app.logger.warning(f"删除临时封面文件失败: {e}")
        return None


def download_singer_image(url, singer):
    path = os.path.join(".", "downloads", singer)
    os.makedirs(path, exist_ok=True)
    final_path = os.path.join(path, "artist.jpg")
    if os.path.exists(final_path):
        return
    if url is None:
        return
    response = requests.get(url)
    if response.status_code == 200:
        with open(final_path, 'wb') as f:
            f.write(response.content)
    current_app.logger.debug(f"歌手封面下载成功: {final_path}")


# 服务器主要下载工具类
def download_song_main(sde):
    # 添加歌手封面
    if len(sde.singer_img) > 0:
        for index, url in enumerate(sde.singer_img):
            download_singer_image(url, sde.singer[index])
    # 查询数据库
    if sde.md5_value is not None:
        if Song.query.filter_by(md5=sde.md5_value).first() is not None:
            current_app.logger.info(f"文件《{sde.name}-{sde.singer_name1()}.{sde.song_fomart}》已存在")
            return
    song = Song.query.filter_by(name=sde.name, artist=sde.singer_name1()).first()
    if song is not None:
        #  比较文件大小（优先下载高品质）
        if int(song.size) > sde.size:
            current_app.logger.info(f"高品质文件《{sde.name}-{sde.singer_name1()}.{song.music_type}》已存在")
            return
        else:
            path = os.path.join(".", "downloads", song.artist, song.album)
            os.remove(os.path.join(path, "{}.{}".format(sde.name, song.music_type)))
    # 下载文件
    file_path = None
    try:
        file_path = download_song(sde.name, sde.album, sde.singer_name1(), sde.music_url, sde.song_fomart)
        if sde.md5_value is None:
            sde.md5_value = md5_hash(file_path)
        if sde.size == 0:
            sde.size = os.stat(file_path).st_size
    except Exception as e:
        current_app.logger.info(e)
    if file_path is None:
        return
    # 下载封面
    cover_path = None
    try:
        temp_dir = os.path.join(os.path.join(".", "temp"))
        cover_path = download_cover(sde.pic, temp_dir)
    except Exception as e:
        current_app.logger.info(e)

    # 写入元数据
    update_metadata(file_path, sde.name, sde.singer_name2(), sde.album, sde.lyric, cover_path, sde.publish_time, sde.no)
    # 写入数据库
    if song is None:
        # 新增
        db.session.add(
            Song(name=sde.name, artist=sde.singer_name1(), album=sde.album, cover=sde.pic, lyric=sde.lyric,
                 url=sde.music_url,
                 music_type=sde.song_fomart, md5=sde.md5_value, size=sde.size))
        current_app.logger.info(f"《{sde.name}-{sde.singer_name1()}.{sde.song_fomart}》文件已下载")
    else:
        # 更新
        song.name = sde.name
        song.artist = sde.singer_name1()
        song.album = sde.album
        song.cover = sde.pic
        song.lyric = sde.lyric
        song.music_url = sde.music_url
        song.music_type = sde.song_fomart
        song.md5 = sde.md5_value
        song.size = sde.size
    db.session.commit()
