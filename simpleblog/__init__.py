from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import config

# 创建插件对象
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name):
    # 创建app并导入配置
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化插件对象
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api_1_0 import api_1_0 as  api_1_0_blueprint
    app.register_blueprint(main_blueprint, static_folder='static', template_folder='templates')
    app.register_blueprint(auth_blueprint, url_prifix='/auth')
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1_0')

    return app
