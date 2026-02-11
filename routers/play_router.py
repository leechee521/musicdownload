from flask import Blueprint, render_template

play_bp = Blueprint('play_router', __name__, url_prefix='/player', static_folder='static', template_folder='templates')


@play_bp.route('/')
def play():
    return render_template('play.html')
