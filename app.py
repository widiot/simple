from simpleblog import create_app
import os

# 创建simpleblog实例
app = create_app(os.getenv('FLASK_CONFIG') or 'development')
