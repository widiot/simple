from simpleblog import create_app, db
from flask_migrate import Migrate
import os

# 创建simpleblog实例
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

# 初始化数据库迁移插件
migrate = Migrate(app, db)
