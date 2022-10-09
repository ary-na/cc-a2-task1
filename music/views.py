from flask import Blueprint, render_template

music = Blueprint('music', __name__, template_folder="templates/music")


@music.route('/')
def index():
    return render_template('index.html')


@music.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')


@music.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')
