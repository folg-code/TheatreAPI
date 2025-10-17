from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField
from rest_framework.validators import UniqueTogetherValidator

from theatre_service.models import (
    Actor, Genre, TheatreHall,
    Performance, Play, Ticket, Order)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres")


class PlayDetailSerializer(PlaySerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)


class PlayListSerializer(PlaySerializer):
    genres = SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    actors = SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seat_in_row", "capacity")


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayListSerializer(many=True, read_only=True)
    theatre_hall = TheatreHallSerializer(many=True, read_only=True)
    play_id = PrimaryKeyRelatedField(
        queryset=Play.objects.all(),
        source="play",
        write_only=True,
    )
    theatre_hall_id = PrimaryKeyRelatedField(
        queryset=TheatreHall.objects.all(),
        source="theatre_hall",
        write_only=True,
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "show_time",
                  "play_id", "theatre_hall_id", "theatre_hall"
                  )


class PerformanceListSerializer(PerformanceSerializer):
    play_title = SlugRelatedField(
        source="play",
        read_only=True,
        slug_field="title"
    )
    theatre_hall_name = SlugRelatedField(
        source="theatre_hall",
        read_only=True,
        slug_field="name"
    )
    theatre_hall_capacity = SlugRelatedField(
        source="theatre_hall",
        read_only=True,
        slug_field="capacity"
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall_capacity",
                  "play_title", "theatre_hall_name")


class TicketPerformanceSerializer(serializers.ModelSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)
    show_time = serializers.CharField(read_only=True)
    theatre_hall_name = serializers.CharField(
        source="theatre_hall.name",
        read_only=True,
    )
    cinema_hall_capacity = serializers.IntegerField(
        source="cinema_hall.capacity",
        read_only=True,
    )

    class Meta:
        model = Performance
        fields = ("id", "play_title", "show_time",
                  "theatre_hall_name", "cinema_hall_capacity")


class TicketSerializer(serializers.ModelSerializer):
    performance = TicketPerformanceSerializer(many=True, read_only=True)
    performance_id = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.all(),
        source="performance",
        write_only=True,
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat_in_row", "performance", "performance_id")

        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=["row", "seat_in_row", "performance"],
                message="This ticket already exists."
            ),
        ]


class TicketRowSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat_in_row")

    def validate(self, data):

        performance = data.get('performance')
        row = data.get('row')
        seat_in_row = data.get('seat_in_row')

        if performance:
            hall = performance.theatre_hall

            if not (1 <= row <= hall.rows):
                raise serializers.ValidationError(
                    {"row": f"Row must be between 1 and {hall.rows}."}
                )

            if not (1 <= seat_in_row <= hall.seat_in_row):
                raise serializers.ValidationError(
                    {"seat": f"Seat must be between 1 and {hall.seat_in_row}."}
                )

        return data


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        return order
