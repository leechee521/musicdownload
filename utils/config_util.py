import json
import os.path

from flask import current_app


class cookie_Config():
    def __init__(self):
        try:
            self.configPath = os.path.join(".", "config", "config.json")
            with open(self.configPath, "r") as f:
                config = json.load(f)
            self.qq_cookie = config['qqMusic']['COOKIE']
            self.wyy_cookie = config['wyyMusic']['COOKIE']

        except FileNotFoundError:
            current_app.logger.info("Config file not found")

    def get_qq_cookie(self):
        return self.qq_cookie

    def get_wyy_cookie(self):
        return self.wyy_cookie

    def update_cookie(self, platform, new_cookie):
        if platform == "qqMusic":
            self.qq_cookie = new_cookie
        elif platform == "wyyMusic":
            self.wyy_cookie = new_cookie
        else:
            return
        """
        修改config.json文件中的COOKIE值

        :param new_cookie: 新的COOKIE值
        :param config_path: config.json文件路径，默认为'config.json'
        """
        try:
            # 读取现有配置文件
            with open(self.configPath, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 更新COOKIE值
            config[platform]['COOKIE'] = new_cookie

            # 写回文件
            with open(self.configPath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            current_app.logger.info("COOKIE更新成功！")
            return True

        except FileNotFoundError:
            current_app.logger.info(f"错误：配置文件 {self.configPath} 未找到")
        except json.JSONDecodeError:
            current_app.logger.info("错误：配置文件格式不正确")
        except KeyError:
            current_app.logger.info("错误：配置文件中没有COOKIE字段")
        except Exception as e:
            current_app.logger.info(f"发生未知错误：{str(e)}")

        return False