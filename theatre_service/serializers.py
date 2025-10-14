from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField

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
        fields = ("id","play","show_time","play_id","theatre_hall_id","theatre_hall")


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
    cinema_hall_capacity = SlugRelatedField(
        source="cinema_hall",
        read_only=True,
        slug_field="capacity"
    )

    class Meta:
        model = Performance
        fields = ("id", "movie", "cinema_hall_capacity", "movie_title", "cinema_hall_name")