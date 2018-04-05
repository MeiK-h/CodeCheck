from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

from .tasks import add
from .models import Bark, Code
from .forms import BarkForm


def index(request):
    return render(request, 'Checker/header.html')


@login_required
def check_list(request):
    checks = Bark.objects.filter(user=request.user)
    return render(request, 'Checker/check_list.html', {'checks': checks})


@login_required
def code_list(request, pk):
    bark = Bark.objects.get(user=request.user, id=pk)
    codes = Code.objects.filter(bark=bark)
    return render(request, 'Checker/code_list.html', {'codes': codes})


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


@login_required
def create_check(request):
    if request.method != 'POST':
        form = BarkForm()
    else:
        form = BarkForm(data=request.POST)
        if form.is_valid():
            bark = Bark(user=request.user, title=form.cleaned_data['title'])
            bark.save()
            return render(request, 'Checker/message.html', {'message': '新建成功'})
    return render(request, 'Checker/create_check.html', {'form': form})
