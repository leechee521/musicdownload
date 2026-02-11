from flask import render_template, Blueprint, current_app, jsonify


home_bp = Blueprint('home_router', __name__)


@home_bp.route('/')
def home():
    current_app.logger.info("主页被访问")
    return render_template('index.html')

@home_bp.route('/playlist')
def playlist():
    return render_template('playlist.html')