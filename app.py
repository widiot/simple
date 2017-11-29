import os, sys
import click
from simple import create_app
from simple.models import db, User, Role, Post

# coverage的配置
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='simple/*')
    COV.start()

# 创建simpleblog实例
app = create_app(os.getenv('FLASK_CONFIG') or 'development')


# shell上下文
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


# 测试的命令
@app.cli.command()
@click.option(
    '--coverage/--no-coverage',
    default=False,
    help='run tests under code coverage')
def test(coverage):
    # 设置coverage的环境变量
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    # 启动单元测试
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


# 分析源码运行时间
@app.cli.command()
@click.option(
    '--length',
    default=25,
    help='Number of functions to include in the profiler report')
@click.option(
    '--profile-dir',
    default=None,
    help='Directory where profiler data files are saved')
def profile(length, profile_dir):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


# 升级程序的操作
@app.cli.command()
def deploy():
    from flask_migrate import upgrade
    from simple.models import Role

    # 数据库迁移
    upgrade()

    # 创建角色
    Role.insert_roles()
