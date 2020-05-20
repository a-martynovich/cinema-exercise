import logging

from django.apps import AppConfig


logger = logging.getLogger('django')


class BookingSystemConfig(AppConfig):
    name = 'booking_system'
