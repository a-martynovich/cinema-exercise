import logging

from django.apps import AppConfig


logger = logging.getLogger('django')


class ReferralSampleConfig(AppConfig):
    name = 'referral_sample'
