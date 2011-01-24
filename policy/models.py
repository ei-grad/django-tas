from django.db import models
from django.contrib.auth.models import User


class Departament(models.Model):
    name = models.CharField(max_length=256)
    admin = models.ForeignKey(User)

class UserDepartament(models.Model):
    user = models.ForeignKey(User, unique=True)
    departament = models.ForeignKey(Departament)


class UserQuotaPolicy(models.Model):
    user = models.ForeignKey(User, unique=True)
    full = models.BigIntegerField()
    used = models.BigIntegerField()
    renewed = models.DateTimeField()
    interval = models.IntegerField()

class DepartamentQuotaPolicy(models.Model):
    departament = models.ForeignKey(Departament, unique=True)
    full = models.BigIntegerField()
    used = models.BigIntegerField()
    renewed = models.DateTimeField()
    interval = models.IntegerField()

