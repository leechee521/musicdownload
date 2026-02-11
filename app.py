import os.path
from logging.config import dictConfig

from flask import Flask, render_template, redirect, url_for

import config
from extemsions import socketio, db
from routers.download_routes import download_bp
from routers.home_router import home_bp
from routers.play_router import play_bp
from routers.search_router import search_bp
from routers.top_list_router import top_list_bp
from routers.update_cookie_router import cookie_bp
from routers.api_router import api_bp

if os.path.exists("log") is False:
    os.mkdir("log")

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            "encoding": 'utf-8',
            'filename': 'log/flask.log',
            'maxBytes': 1024 * 1024 * 5,  # 5Mb
            'backupCount': 10,  # 10 备份
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
})

app = Flask(__name__)

# 配置Jinja2不处理Vue.js的模板语法
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

flask_env = config.get_config()
app.config.from_object(flask_env)
socketio.init_app(app)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(
    home_bp,
    url_prefix='/home',
    static_folder='static',
    template_folder='templates'
)

app.register_blueprint(
    cookie_bp,
    url_prefix='/cookie',
    static_folder='static',
    template_folder='templates'
)

app.register_blueprint(
    download_bp,
    url_prefix='/download',
    static_folder='static',
    template_folder='templates'
)

app.register_blueprint(
    search_bp,
    url_prefix='/search',
    static_folder='static',
    template_folder='templates'
)
app.register_blueprint(play_bp)
app.register_blueprint(top_list_bp)
app.register_blueprint(api_bp)


@socketio.on('connect')
def handle_connect():
    print('客户端已连接')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/')
def root():
    return render_template("index.html")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
