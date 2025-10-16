from django.db.models import Expression, ExpressionWrapper, F, Count, IntegerField
from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from theatre_service.models import Genre, Actor, Play, TheatreHall, Performance, Order
from theatre_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre_service.serializers import GenreSerializer, ActorSerializer, PlaySerializer, TheatreHallSerializer, \
    PerformanceSerializer, PlayListSerializer, PlayDetailSerializer, OrderSerializer, PerformanceListSerializer, \
    PerformanceDetailSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlayListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return PlayListSerializer
        elif self.action == 'retrieve':
            return PlayDetailSerializer
        return PlaySerializer



class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return PerformanceListSerializer

        elif self.action == 'retrieve':
            return PerformanceDetailSerializer

        return PerformanceSerializer

    def get_queryset(self):
        if self.action == 'list':
            qs = Performance.objects.all().select_related('theatre_hall')
            qs = qs.annotate(
                taken=Count("tickets"),
                capacity=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seat_in_row"),
                    output_field=IntegerField()
                ),
                available=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seat_in_row")
                    - Count("tickets"),
                    output_field=IntegerField()
                )
            )

            play_filter = self.request.query_params.get('play')
            if play_filter:
                qs = qs.filter(play_filter)

            date_filter = self.request.query_params.get('date')
            if date_filter:
                date_obj = parse_date(date_filter)
                if date_obj:
                    qs = qs.filter(show_time__date=date_obj)
            return qs
        elif self.action == 'retrieve':
            return Performance.objects.all().select_related('theatre_hall')
        return Performance.objects.all()


class OrderPagination(PageNumberPagination):
    page_size = 10


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    p
    ermission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

