from flask import render_template, request, jsonify
from . import main


# 如果请求接收JSON并不接收HTML，则返回JSON的错误格式；否则返回HTML模板
@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404
