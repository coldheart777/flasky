flasky
参考自  https://github.com/miguelgrinberg/flasky 用的是当前一些包的最新版本。
# 源码分析不可用！
*manage.py:*
```python
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()
```
> * Ignoring a call to 'app.run()' that would block the current 'flask' CLI command.
   Only call 'app.run()' in an 'if __name__ == "__main__"' guard.

# Selenium 单元测试出问题！
test_admin_home_page
# api测试出问题！
```python
FAIL: test_anonymous (test_api.APITestCase.test_anonymous)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Desktop\code\Python\flasky\tests\test_api.py", line 93, in test_anonymous
    self.assertEqual(response.status_code, 401)
AssertionError: 200 != 401

======================================================================
FAIL: test_no_auth (test_api.APITestCase.test_no_auth)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Desktop\code\Python\flasky\tests\test_api.py", line 42, in test_no_auth
    self.assertEqual(response.status_code, 401)
AssertionError: 200 != 401

======================================================================
FAIL: test_token_auth (test_api.APITestCase.test_token_auth)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Desktop\code\Python\flasky\tests\test_api.py", line 78, in test_token_auth
    self.assertEqual(response.status_code, 200)
AssertionError: 404 != 200
```
