from django.conf import settings
from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'email', 'phone']


class MySerializer(serializers.Serializer):
    booking = BookingSerializer(required=False)
    book_seats = serializers.ListField(
        child=serializers.IntegerField(min_value=1,
                                       max_value=settings.BOOKING_SEATS_ROWS * settings.BOOKING_SEATS_PER_ROW))

    def save(self, session_key):
        book_instance, _ = Booking.objects.get_or_create(session_key=session_key)
        booking_data = self.validated_data.get('booking')
        if booking_data is not None:
            book_serializer = BookingSerializer()
            book_serializer.update(book_instance, booking_data)
        return book_instance