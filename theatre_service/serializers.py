from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from theatre_service.models import Actor, Genre, TheatreHall, Performance, Play


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
        fileds = ("id", "play", "theatre_hall", "show_time")