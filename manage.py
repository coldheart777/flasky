import os

import click
from flask_login import login_required

from app import create_app, db
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.cli.command("test")
@click.argument("test_file", required=False)  # 可选参数，用于指定测试文件
def test(test_file=None):
    """Run the unit tests."""
    import unittest
    if test_file:
        # 从指定的测试文件加载并运行测试
        tests = unittest.TestLoader().discover('tests', pattern=f"{test_file}.py")
    else:
        # 加载并运行所有测试
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'
