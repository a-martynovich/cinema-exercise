from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from rest_framework.test import APIClient


class BookingTests(TestCase):
    def setUp(self):
        self.root_url = reverse('booking')
        self.client = APIClient()

    def test_get(self):
        response = self.client.get(self.root_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['rows']), settings.BOOKING_SEATS_ROWS)
        self.assertEqual(len(response.data['rows'][0]), settings.BOOKING_SEATS_PER_ROW)

    def test_book(self):
        response = self.client.get(self.root_url)
        self.assertEqual(response.status_code, 200)

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
        response = self.client.get(self.root_url)
        self.assertEqual(response.status_code, 200)

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


class SignupValidationTests(TestCase):
    def setUp(self):
        self.url = reverse('signup')

    def test_weak_pass(self):
        """
        Short, common, numeric passwords are invalid.
        """
        response = self.client.post(self.url, {
            'username': f'user',
            'password1': '123',
            'password2': '123',
        })
        self.assertEqual(response.status_code, 200)

        form = response.context[0]['form']
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'password2': ['This password is too short. It must contain at least 8 characters.',
                          'This password is too common.', 'This password is entirely numeric.']})

    def test_username_exists(self):
        """
        Signing up with a username which already exists is an error.
        """
        response = self.client.post(self.url, {
            'username': f'user',
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(self.url, {
            'username': f'user',
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)

        form = response.context[0]['form']
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'username': ['A user with that username already exists.']})