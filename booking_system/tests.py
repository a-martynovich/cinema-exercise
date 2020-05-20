from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from rest_framework.test import APIClient


class BookingTests(TestCase):
    def setUp(self):
        self.root_url = reverse('booking')
        self.client = APIClient()
        response = self.client.get(self.root_url)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        response = self.client.get(self.root_url)
        self.assertEqual(len(response.data['rows']), settings.BOOKING_SEATS_ROWS)
        self.assertEqual(len(response.data['rows'][0]), settings.BOOKING_SEATS_PER_ROW)

    def test_book(self):
        booking_info = {
            'first_name': 'a',
            'last_name': 'b',
            'email': 'a@b.com',
            'phone': '1234'
        }
        seats = [1, 2]
        response = self.client.post(self.root_url, {
            'book_seats': seats,
            'booking': booking_info
        }, format='json')
        self.assertDictEqual(response.data['booking'], booking_info)
        self.assertListEqual(seats, [seat['number'] for seat in response.data['rows'][0]][:len(seats)])

        response = self.client.get(self.root_url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data['booking'], booking_info)
        self.assertListEqual(seats, [seat['number'] for seat in response.data['rows'][0]][:len(seats)])

    def test_book_seat_taken(self):
        booking_info = {
            'first_name': 'a',
            'last_name': 'b',
            'email': 'a@b.com',
            'phone': '1234'
        }
        seats = [1, 2]
        response = self.client.post(self.root_url, {
            'book_seats': seats,
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)

        client = APIClient()
        response = client.get(self.root_url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data['rows'][0][0], {
            'number': 1,
            'available': False,
            'selected': False
        })
        response = client.post(self.root_url, {
            'book_seats': [1],
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], 'seat taken')

    def test_unbook(self):
        booking_info = {
            'first_name': 'a',
            'last_name': 'b',
            'email': 'a@b.com',
            'phone': '1234'
        }
        response = self.client.post(self.root_url, {
            'book_seats': [1, 2],
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.root_url, {
            'book_seats': [],
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data['rows'][0][0], {
            'number': 1,
            'available': True,
            'selected': False
        })


class ValidationTests(TestCase):
    def setUp(self):
        self.root_url = reverse('booking')
        self.client = APIClient()
        response = self.client.get(self.root_url)
        self.assertEqual(response.status_code, 200)

    def test_validate_seats(self):
        booking_info = {
            'first_name': 'a',
            'last_name': 'b',
            'email': 'a@b.com',
            'phone': '1234'
        }
        seats = [settings.BOOKING_SEATS_ROWS*settings.BOOKING_SEATS_PER_ROW+2]
        response = self.client.post(self.root_url, {
            'book_seats': seats,
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['field_errors']['book_seats'][0][0].code, 'max_value')

    def test_validate_missing_field(self):
        booking_info = {
            'last_name': 'b',
            'email': 'a@b.com',
            'phone': '1234'
        }
        seats = [1]
        response = self.client.post(self.root_url, {
            'book_seats': seats,
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['field_errors']['booking']['first_name'][0].code, 'required')

    def test_validate_email(self):
        booking_info = {
            'first_name': 'a',
            'last_name': 'b',
            'email': 'abcdef',
            'phone': '1234'
        }
        seats = [settings.BOOKING_SEATS_ROWS * settings.BOOKING_SEATS_PER_ROW + 2]
        response = self.client.post(self.root_url, {
            'book_seats': seats,
            'booking': booking_info
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['field_errors']['booking']['email'][0].code, 'invalid')

    def test_validate_missing_booking(self):
        seats = [1]
        response = self.client.post(self.root_url, {
            'book_seats': seats
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['field_errors']['non_field_errors'][0].code, 'invalid')
