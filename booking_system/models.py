from django.conf import settings
from django.db import models
from django.db.models import Q


class Booking(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=64)
    phone = models.CharField(max_length=64)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True, unique=True)


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
        seats = self.get_queryset().select_related('booking')
        row_length = settings.BOOKING_SEATS_PER_ROW
        seats_count = row_length*settings.BOOKING_SEATS_ROWS
        if seats.count() < seats_count:
            self.populate(range(1, seats_count+1))
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
