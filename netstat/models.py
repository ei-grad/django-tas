from django.db import models
from django.contrib.auth.models import User


class Session(models.Model):
    user = models.ForeignKey(User)
    src = models.IPAddressField(db_index=True)
    dt_start = models.DateTimeField(auto_now=True)
    dt_finish = models.DateTimeField(null=True, db_index=True)


class Record(models.Model):
    session = models.ForeignKey(Session)
    dst = models.CharField(max_length=64, db_index=True)
    traf_in = models.BigIntegerField(default=0)
    traf_out = models.BigIntegerField(default=0)

