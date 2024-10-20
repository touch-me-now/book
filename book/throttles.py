from django.core.cache import caches
from rest_framework.throttling import UserRateThrottle


class ReviewRateThrottle(UserRateThrottle):
    scope = 'review'
    cache = caches["throttle"]


class ReactionRateThrottle(UserRateThrottle):
    scope = 'review_react'
    cache = caches["throttle"]
