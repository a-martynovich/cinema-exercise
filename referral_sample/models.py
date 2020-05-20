from enum import IntEnum
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession


class Booking(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=64)
    phone = models.CharField(max_length=64)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True, unique=True)


class SessionUser(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE)


class SeatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('number')

    def book(self, seat_numbers, b: Booking):
        if super().get_queryset().filter(~Q(booking=b), booking__isnull=False, number__in=seat_numbers).exists():
            return False
        current = super().get_queryset().filter(Q(booking=None) | Q(booking=b))
        for seat in current:
            seat.booking = b if seat.number in seat_numbers else None
        super().bulk_update(current, ['booking'])
        return True

    def populate(self, numbers):
        super().bulk_create([self.model(number=n) for n in numbers], ignore_conflicts=True)

    def serialize(self, b: Booking):
        seats = self.get_queryset().all()
        row_length = settings.BOOKING_SEATS_PER_ROW
        rows = [[{
                'number': s.number,
                'available': s.booking is None or s.booking == b,
                'selected': s.booking is not None and s.booking == b
                } for s in seats[row_i*row_length:row_i*row_length+row_length]]
                for row_i in range(settings.BOOKING_SEATS_ROWS)]
        return rows


class Seat(models.Model):
    number = models.PositiveSmallIntegerField()
    booking = models.ForeignKey(Booking, null=True, on_delete=models.SET_NULL)
    manager = SeatManager()

    def __repr__(self):
        return f'Seat number {self.number} booking {self.booking}'
