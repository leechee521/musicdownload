from flask import current_app
from entity.song_entity import PlatformCookie
from extemsions import db

class cookie_Config():
    """
    Cookie配置管理类，已重构为使用数据库存储。
    """
    def __init__(self):
        pass

    def get_qq_cookie(self):
        """获取QQ音乐Cookie"""
        try:
            config = PlatformCookie.query.filter_by(platform='qqMusic').first()
            return config.cookie if config else ""
        except Exception as e:
            # 记录错误但不崩溃，返回空字符串
            return ""

    def get_wyy_cookie(self):
        """获取网易云音乐Cookie"""
        try:
            config = PlatformCookie.query.filter_by(platform='wyyMusic').first()
            return config.cookie if config else ""
        except Exception as e:
            return ""

    def update_cookie(self, platform, new_cookie):
        """
        更新或插入指定平台的Cookie
        
        :param platform: 平台名称 ('qqMusic' 或 'wyyMusic')
        :param new_cookie: 新的COOKIE值
        """
        try:
            cookie_obj = PlatformCookie.query.filter_by(platform=platform).first()
            if cookie_obj:
                cookie_obj.cookie = new_cookie
            else:
                cookie_obj = PlatformCookie(platform=platform, cookie=new_cookie)
                db.session.add(cookie_obj)
            
            db.session.commit()
            current_app.logger.info(f"{platform} COOKIE更新成功！")
            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新Cookie发生错误：{str(e)}")
            return False
