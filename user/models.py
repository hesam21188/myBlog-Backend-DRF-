from django.db import models
from rest_framework.authtoken.admin import User


class ActiveCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
