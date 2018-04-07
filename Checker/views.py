from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

from .tasks import check
from .models import Bark, Code, access_type, UserInfo, make_cmd, Result
from .forms import BarkForm

import os
import time
import shutil


def index(request):
    return render(request, 'Checker/header.html')


@login_required
def check_list(request):
    checks = Bark.objects.filter(user=request.user)[::-1]
    return render(request, 'Checker/check_list.html', {'checks': checks})


@login_required
def delete_check(request, pk):
    if request.method != 'POST':
        return render(request, 'Checker/message.html', {'message': '403'})
    bark = Bark.objects.get(user=request.user, id=pk)
    codes = Code.objects.filter(bark=bark)
    for code in codes:
        code.code.delete()
        code.delete()
    if os.path.exists('Checker/result/check_%d' % bark.id):
        shutil.rmtree('Checker/result/check_%d' % bark.id)
    bark.delete()
    return render(request, 'Checker/message.html', {'message': '删除成功', 'url': '/check/'})


@login_required
def delete_code(request, pk1, pk2):
    if request.method != 'POST':
        return render(request, 'Checker/message.html', {'message': '403'})
    bark = Bark.objects.get(user=request.user, id=pk1)
    code = Code.objects.get(bark=bark, id=pk2)
    code.code.delete()
    code.delete()
    return render(request, 'Checker/message.html', {'message': '删除成功'})


@login_required
def code_list(request, pk):
    if request.method != 'POST':
        bark = Bark.objects.get(user=request.user, id=pk)
        codes = Code.objects.filter(bark=bark)[::-1]
        return render(request, 'Checker/code_list.html', {'codes': codes, 'check_id': pk})
    else:
        files = request.FILES.getlist('file')
        bark = Bark.objects.get(user=request.user, id=pk)
        cnt = Code.objects.filter(bark=bark).count()
        if len(files) + cnt > bark.max_code_cnt:
            return render(request, 'Checker/message.html',
                          {'message': '您上传的文件数量超过了限制 ( {0} / {1} ) ，全部数据回滚'.format(len(files) + cnt,
                                                                                   bark.max_code_cnt)})
        # 检查文件大小与后缀
        for file in files:
            if file.size > 64 * 1024:
                return render(request, 'Checker/message.html', {'message': '文件 "{0}" 过大，全部数据回滚'.format(file.name)})
            if file.name.split('.')[-1] not in access_type:
                return render(request, 'Checker/message.html', {'message': '文件 "{0}" 的后缀名未通过，全部数据回滚'.format(file.name)})
        for file in files:
            code = Code(bark=bark, code=file)
            code.save()
        return render(request, 'Checker/message.html', {'message': '上传成功', 'url': '/check/%d/code/' % bark.id})


@login_required
def create_check(request):
    bark_cnt = Bark.objects.filter(user=request.user).count()
    # 检查 UserInfo ，如果没有则创建
    user_info = UserInfo.objects.filter(user=request.user)
    if not user_info:
        user_info = UserInfo(user=request.user)
        user_info.save()
    else:
        user_info = user_info[0]
    max_bark_cnt = user_info.max_bark_cnt
    if bark_cnt >= max_bark_cnt:
        return render(request, 'Checker/message.html', {'message': '查重个数已达上限'})
    if request.method != 'POST':
        form = BarkForm()
    else:
        form = BarkForm(data=request.POST)
        if form.is_valid():
            bark = Bark(user=request.user, title=form.cleaned_data['title'], language=form.cleaned_data['language'])
            bark.max_code_cnt = UserInfo.objects.get(user=request.user).max_code_cnt
            bark.save()
            return render(request, 'Checker/message.html', {'message': '新建成功', 'url': '/check/%d/code/' % bark.id})
    return render(request, 'Checker/create_check.html', {'form': form})


@login_required
def check_start(request, pk):
    if request.method != 'POST':
        return render(request, 'Checker/message.html', {'message': '403'})
    bark = Bark.objects.get(user=request.user, id=pk)
    percent = request.POST.get('percent', '80%')
    check_type = request.POST.get('check_type', 'jplag')
    if check_type == 'jplag' and not request.user.has_perm('Checker.jplag'):
        return render(request, 'Checker/message.html', {'message': '权限不足'})
    if check_type == 'moss' and not request.user.has_perm('Checker.moss'):
        return render(request, 'Checker/message.html', {'message': '权限不足'})

    # 检查有无 result
    result = Result.objects.filter(bark=bark)
    if result:
        return render(request, 'Checker/message.html',
                      {'message': '之前已经查重过，请在代码页面查看', 'url': '/check/%d/result/' % bark.id})

    this_time = str(int(time.time()))
    r = check.delay(make_cmd(bark.id, this_time, bark.language, percent, check_type))
    result = Result(bark=bark, name=r.id, rid=this_time)
    result.save()

    return render(request, 'Checker/message.html', {'message': '开始查重', 'url': '/check/%d/result/' % bark.id})


@login_required
def check_result(request, pk):
    bark = Bark.objects.get(user=request.user, id=pk)
    result = Result.objects.get(bark=bark)
    if result.get_state() is False:
        return render(request, 'Checker/message.html', {'message': '查重中……', 'url': '/check/%d/result/' % bark.id})
    return render(request, 'Checker/message.html',
                  {'message': '查重结束，请点击查看', 'url': '/result/%s/index.html' % result.rid})


def login(request):
    redirect_to = request.GET.get('next', '/')
    if request.method != 'POST':
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.user_cache)
            return HttpResponseRedirect(redirect_to)
    return render(request, 'Checker/login.html', {'form': form})


def register(request):
    return render(request, 'Checker/message.html', {'message': '请先登录后注册'})


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('Checker:index'))
