from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from .config import config

# 创建插件对象
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()
moment = Moment()
pagedown = PageDown()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'


def create_app(config_name):
    # 创建app并导入配置
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化插件对象
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    # 注册蓝图
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(
        main_blueprint, static_folder='static', template_folder='templates')
    app.register_blueprint(auth_blueprint, url_prifix='/auth')
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
