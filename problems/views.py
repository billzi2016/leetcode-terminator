from django.shortcuts import render


def index(request):
    """主页：只渲染页面壳，数据全部由前端通过 API 加载。"""
    return render(request, "problems/index.html")
