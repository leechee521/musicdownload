from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# 尝试使用 gevent，如果不存在则使用 threading
try:
    import gevent
    socketio = SocketIO(cors_allowed_origins="*", async_mode='gevent')
except ImportError:
    socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

db = SQLAlchemy()