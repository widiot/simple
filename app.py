import os
from simpleblog import create_app

# 创建simpleblog实例
app = create_app(os.getenv('FLASK_CONFIG') or 'development')


# 测试的命令
@app.cli.command()
def test():
    """测试代码"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
