from flask import Flask
from config import config


def create_app(config_name=None):
    # 创建app并配置
    app = Flask(__name__)
    app.config.from_object(config[config_name or 'development'])

    # 注册蓝图
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api_1_0 import api_1_0 as  api_1_0_blueprint
    app.register_blueprint(main_blueprint, static_folder='static', template_folder='templates')
    app.register_blueprint(auth_blueprint, url_prifix='/auth')
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1_0')

    return app


app = create_app()
