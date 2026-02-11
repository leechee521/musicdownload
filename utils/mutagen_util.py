import io
import os
import threading

from PIL import Image
from flask import current_app
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, TIT2, TPE1, TALB, USLT, APIC, ID3NoHeaderError, TRCK, TDRC, TPOS

# 线程锁，用于保护共享资源（如果需要）
lock = threading.Lock()


def compress_image_if_needed(image_path, max_size_bytes=16 * 1024 * 1024 - 1024):  # 16MB - 1KB 缓冲
    """压缩图片使其不超过 max_size_bytes，返回压缩后的二进制数据"""
    try:
        img = Image.open(image_path)

        # 如果图片是 RGBA（带透明通道），转换为 RGB（JPEG 不支持透明）
        if img.mode == 'RGBA':
            img = img.convert('RGB')  # 移除 Alpha 通道

        # 如果图片已经小于限制，直接返回
        original_size = os.path.getsize(image_path)
        if original_size <= max_size_bytes:
            with open(image_path, "rb") as f:
                return f.read()

        # 图片格式处理（JPEG 压缩率更高，优先使用）
        format = "JPEG"  # 默认用 JPEG
        if image_path.lower().endswith(".png"):
            format = "PNG"

        # 初始压缩质量（JPEG 质量 0-100，PNG 压缩级别 0-9）
        quality = 85 if format == "JPEG" else 6

        # 逐步降低质量，直到图片大小符合要求
        while True:
            buffer = io.BytesIO()

            if format == "JPEG":
                img.save(buffer, format=format, quality=quality, optimize=True)
            else:  # PNG
                img.save(buffer, format=format, compress_level=quality)

            # 检查大小
            if buffer.tell() <= max_size_bytes or quality <= 10:
                break

            # 降低质量继续尝试
            quality = max(10, quality - 10)  # 最低不低于10

        return buffer.getvalue()

    except Exception as e:
        current_app.logger.info(f"图片压缩失败: {e}")
        return None


def update_flac_metadata(file_path, title=None, artist=None, album=None, lyrics=None, cover_path=None,
                         publish_time=None, no=None):
    """
    更新 FLAC 文件的元数据，包括标题、艺术家、专辑、歌词、封面、发布时间、音轨号和光盘号。

    参数:
        file_path (str): FLAC文件路径
        title (str, optional): 歌曲标题
        artist (str, optional): 艺术家
        album (str, optional): 专辑名称
        lyrics (str, optional): 歌词
        cover_path (str, optional): 封面图片路径
        publish_time (str, optional): 发布时间/年份
        no (int, optional): 音轨号

    返回:
        bool: 是否成功更新
    """
    try:
        if not os.path.exists(file_path):
            current_app.logger.error(f"FLAC文件不存在: {file_path}")
            return False

        audio = FLAC(file_path)

        # 更新文本元数据
        if title is not None:
            audio["title"] = title
        if artist is not None:
            audio["artist"] = artist
        if album is not None:
            audio["album"] = album
        if lyrics is not None:
            audio["lyrics"] = lyrics
        if publish_time is not None or publish_time != '1970' or publish_time != 1970:
            audio["date"] = str(publish_time)
        if no is not None:
            audio["tracknumber"] = str(no)

        # 更新封面
        if cover_path:
            if not os.path.exists(cover_path):
                current_app.logger.warning(f"封面文件不存在: {cover_path}")
            else:
                try:
                    cover_data = compress_image_if_needed(cover_path)
                    if not cover_data:
                        current_app.logger.warning("封面处理失败，跳过更新")
                        return False

                    picture = Picture()
                    picture.data = cover_data
                    picture.type = 3  # 3 表示封面图片

                    # 自动检测图片类型
                    if cover_path.lower().endswith((".jpg", ".jpeg")):
                        picture.mime = "image/jpeg"
                    elif cover_path.lower().endswith(".png"):
                        picture.mime = "image/png"
                    else:
                        picture.mime = "image/jpeg"  # 默认

                    picture.desc = "Cover"
                    audio.clear_pictures()
                    audio.add_picture(picture)

                except Exception as e:
                    current_app.logger.error(f"更新封面时出错: {e}", exc_info=True)
                    return False
                finally:
                    # 无论成功与否都尝试删除临时文件
                    try:
                        os.remove(cover_path)
                    except OSError as e:
                        current_app.logger.debug(f"删除临时封面文件失败: {e}")

        # 保存文件时确保使用 UTF-8 编码
        audio.save()
        current_app.logger.info(f"成功更新FLAC元数据: {file_path}")
        return True

    except Exception as e:
        current_app.logger.error(f"更新FLAC元数据时出错: {e}", exc_info=True)
        return False


def update_mp3_metadata(file_path, title=None, artist=None, album=None, lyrics=None, cover_path=None,
                        publish_time=None, no=None):
    """
    更新 MP3 文件的元数据，包括标题、艺术家、专辑、歌词、封面、发布时间、音轨号和光盘号。

    参数:
        file_path (str): MP3文件路径
        title (str, optional): 歌曲标题
        artist (str, optional): 艺术家
        album (str, optional): 专辑名称
        lyrics (str, optional): 歌词
        cover_path (str, optional): 封面图片路径
        publish_time (str, optional): 发布时间/年份
        no (int, optional): 音轨号
        cd (int, optional): 光盘号

    返回:
        bool: 是否成功更新
    """
    try:
        if not os.path.exists(file_path):
            current_app.logger.error(f"MP3文件不存在: {file_path}")
            return False

        cover_data = None
        if cover_path and os.path.exists(cover_path):
            cover_data = compress_image_if_needed(cover_path)
            if not cover_data:
                current_app.logger.warning("封面处理失败，跳过更新")

        # 尝试读取现有的ID3标签，如果没有则创建新的
        try:
            audio = ID3(file_path)
        except ID3NoHeaderError:
            audio = ID3()

        # 更新标题
        if title is not None:
            audio["TIT2"] = TIT2(encoding=3, text=title)

        # 更新艺术家
        if artist is not None:
            audio["TPE1"] = TPE1(encoding=3, text=artist)

        # 更新专辑
        if album is not None:
            audio["TALB"] = TALB(encoding=3, text=album)

        # 更新歌词
        if lyrics is not None:
            audio.delall("USLT")  # 删除所有现有歌词帧
            audio["USLT"] = USLT(encoding=3, lang='eng', desc='Lyrics', text=lyrics)
        # 更新发布时间
        if publish_time is not None or publish_time != '1970' or publish_time != 1970:
            audio["TDRC"] = TDRC(encoding=3, text=str(publish_time))

        # 更新音轨号
        if no is not None:
            audio["TRCK"] = TRCK(encoding=3, text=str(no))

        # 更新封面
        if cover_data:
            audio.delall("APIC")  # 删除所有现有封面
            # 自动检测图片类型
            mime = "image/jpeg"  # 默认
            if cover_path.lower().endswith(".png"):
                mime = "image/png"

            audio["APIC"] = APIC(
                encoding=3,
                mime=mime,
                type=3,  # 3表示封面图片
                desc='Cover',
                data=cover_data
            )

        # 保存更改
        audio.save(file_path, v2_version=3)  # 使用ID3v2.3版本确保兼容性
        current_app.logger.info(f"成功更新MP3元数据: {file_path}")
        return True

    except Exception as e:
        current_app.logger.error(f"更新MP3元数据时出错: {e}", exc_info=True)
        return False
    finally:
        # 无论成功与否都尝试删除临时文件
        if cover_path and os.path.exists(cover_path):
            try:
                os.remove(cover_path)
            except OSError as e:
                current_app.logger.debug(f"删除临时封面文件失败: {e}")


def update_metadata(file_path, title=None, artist=None, album=None, lyrics=None, cover_url=None, publish_time=None,
                    no=None):
    """
    根据文件类型调用相应的元数据更新函数。
    """
    if not os.path.exists(file_path):
        current_app.logger.info(f"文件不存在: {file_path}")
        return
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == ".flac":
            update_flac_metadata(file_path, title, artist, album, lyrics, cover_url, publish_time, no)
        elif file_ext == ".mp3":
            update_mp3_metadata(file_path, title, artist, album, lyrics, cover_url, publish_time, no)
        else:
            current_app.logger.info(f"不支持的文件类型: {file_ext}")
    except Exception as e:
        current_app.logger.info(f"更新元数据时出错: {e}")
        #     os.remove(file_path)  # 如果 FLAC 文件损坏，删除文件
