import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'leechee_ii')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///music.db')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    WTF_CSRF_ENABLED = False  # 测试时通常禁用CSRF保护


class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///music.db')
    DEBUG = False


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    evn = os.getenv("EVN", 'production')
    return config[evn]
