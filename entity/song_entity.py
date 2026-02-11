from datetime import datetime

from extemsions import db


class Song(db.Model):
    # name, album, singer, pic, lyric, music_url, song_fomart, md5_value
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255), nullable=True)
    cover = db.Column(db.Text, nullable=True)
    lyric = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50), nullable=True)  # 新增：记录音乐来源平台
    music_type = db.Column(db.String(30), unique=False, nullable=False)
    md5 = db.Column(db.String(80), unique=True, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)
    size = db.Column(db.String(80), nullable=False)


class PlatformCookie(db.Model):
    """各平台Cookie设置表"""
    __tablename__ = 'platform_cookies'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), unique=True, nullable=False)  # 平台名称，如 'qqMusic', 'wyyMusic'
    cookie = db.Column(db.Text, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PlatformCookie {self.platform}>'
