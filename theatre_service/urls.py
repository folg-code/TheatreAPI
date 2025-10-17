from django.urls import path, include
from rest_framework.routers import DefaultRouter

from theatre_service.views import (
    PerformanceViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    ActorViewSet,
    GenreViewSet,
    OrderViewSet)

app_name = 'theatre_service'

router = DefaultRouter()

router.register('performers', PerformanceViewSet, basename='performers')
router.register('halls', TheatreHallViewSet, basename='halls')
router.register('plays', PlayViewSet, basename='plays')
router.register('actors', ActorViewSet, basename='actors')
router.register('genres', GenreViewSet, basename='genres')
router.register('orders', OrderViewSet, basename='orders')


urlpatterns = [
    path('', include(router.urls))
]
