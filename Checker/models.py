from django.db import models
from django.contrib.auth import get_user_model
from celery.result import AsyncResult


class UserInfo(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    max_code_cnt = models.IntegerField(default=50, verbose_name='最大代码数量')
    max_bark_cnt = models.IntegerField(default=3, verbose_name='最大查重数量')


class Bark(models.Model):
    language_set = (
        ('cpp', 'C/C++'),
        ('java', 'Java'),
        ('py', 'Python'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=200, choices=language_set)
    max_code_cnt = models.IntegerField(default=50)
    c_time = models.DateTimeField(auto_now_add=True)
    u_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ("moss", "可以使用 moss 查重系统"),
            ("jplag", "可以使用 jplag 查重系统"),
        )


def directory_path(instance, filename):
    return 'check_{0}/{1}'.format(instance.bark.id, filename)


class Code(models.Model):
    bark = models.ForeignKey(Bark, on_delete=models.CASCADE)
    code = models.FileField(upload_to=directory_path)
    c_time = models.DateTimeField(auto_now_add=True)
    u_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code.name


access_type = ['c', 'cpp', 'cc', 'java', 'py']
moss_user_id = 987654321


class Result(models.Model):
    bark = models.ForeignKey(Bark, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rid = models.CharField(max_length=200)

    def get_state(self):
        result = AsyncResult(self.name)
        return result.ready()


def make_cmd(bark_id, result_dir, language, percent, check_type):
    cmd = None
    if check_type == 'jplag':
        if language == 'cpp':
            language = 'c/c++'
        if language == 'java':
            language = 'java17'
        if language == 'py':
            language = 'python3'
        cmd = 'java -jar Checker/jplag.jar -l {0} -m {1} -r {2} -s {3}'.format(language, percent,
                                                                               'Checker/result/%s' % result_dir,
                                                                               'Checker/uploads/check_%d' % bark_id)
    elif check_type == 'moss':
        if language == 'cpp':
            language = 'cc'
        if language == 'java':
            language = 'java'
        if language == 'py':
            language = 'python'
        cmd = 'python3 Checker/check_moss.py {0} {1} {2} {3}'.format(language,
                                                                     'Checker/result/%s/' % result_dir,
                                                                     'Checker/uploads/check_%d' % bark_id,
                                                                     moss_user_id)
    return cmd
