# coding=utf-8
from __future__ import absolute_import, unicode_literals

import os
import time

from celery import shared_task


@shared_task
def check(cmd):
    os.system(cmd)
    time.sleep(10)
    return True
