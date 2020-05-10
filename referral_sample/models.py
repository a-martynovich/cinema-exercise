from enum import IntEnum
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.http import urlencode


class SessionUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=64)
    phone = models.CharField(max_length=64)


class Seat(models.Model):
    class State(IntEnum):
        FREE = 1
        RESERVED = 2
        BOUGHT = 3
    number = models.PositiveSmallIntegerField()
    taken = models.OneToOneField(SessionUser, null=True, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(default=State.FREE)

