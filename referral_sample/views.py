import logging

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Booking, Seat, SessionUser
from .serializers import BookingSerializer, MySerializer

logger = logging.getLogger('django')


class RootView(TemplateView):
    template_name = 'index.html'


class BookingView(APIView):
    def booking_data(self, request):
        s: SessionStore = request.session
        b = Booking.objects.filter(session_key=s.session_key).first()
        return {
            'rows': Seat.manager.serialize(b),
            'booking': BookingSerializer(b).data if b else None
        }

    def get(self, request, format=None):
        return Response(self.booking_data(request))

    def post(self, request, format=None):
        serializer = MySerializer(data=request.data)
        response = {}
        if serializer.is_valid():
            data = serializer.validated_data
            seats = data['book_seats']
            s = request.session
            if not s.session_key:
                s.save()
            logger.error('POST key: %s', s.session_key)
            b = serializer.save(session_key=s.session_key)
            if not Seat.manager.book(seats, b):
                response = {'error': 'seat taken'}
            response.update({
                'rows': Seat.manager.serialize(b),
                'booking': BookingSerializer(b).data if b else None
            })
        else:
            logger.error('VALIDATION ERROR')
            response = {'field_errors': serializer.errors}
            response.update(self.booking_data(request))
        return Response(response)
