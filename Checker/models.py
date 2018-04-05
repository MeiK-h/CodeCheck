from django.db import models
from django.contrib.auth import get_user_model


class Bark(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    c_time = models.DateTimeField(auto_now_add=True)
    u_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Code(models.Model):
    bark = models.ForeignKey(Bark, on_delete=models.CASCADE)
    code = models.FileField(upload_to='code/')
    c_time = models.DateTimeField(auto_now_add=True)
    u_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code.name
