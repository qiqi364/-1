"""Vercel Serverless Function 入口"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def handler(request):
    """处理 HTTP 请求"""
    from streamlit.web.cli import run as st_run
    return {
        "statusCode": 200,
        "body": "<h1>请使用 Streamlit Cloud 部署</h1><p>访问: https://dronelog-analyzer.streamlit.app</p>"
    }