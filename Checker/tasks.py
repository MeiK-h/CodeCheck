# coding=utf-8
from celery import Celery
import time

app = Celery('tasks', backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')


@app.task
def add(x, y):
    time.sleep(5)
    return x + y
