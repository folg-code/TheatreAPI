from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from theatre_service.models import (
    Actor, Genre, Play, TheatreHall, Performance, Ticket, Order
)
from theatre_service.serializers import (
    ActorSerializer, GenreSerializer, PlaySerializer, PlayDetailSerializer,
    PlayListSerializer, TheatreHallSerializer, PerformanceSerializer,
    PerformanceDetailSerializer, PerformanceListSerializer,
    TicketSerializer, TicketRowSeatSerializer, OrderSerializer
)

User = get_user_model()


class ActorSerializerTest(TestCase):
    def test_actor_serialization(self):
        actor = Actor.objects.create(first_name="John", last_name="Doe")
        serializer = ActorSerializer(actor)
        self.assertEqual(serializer.data["first_name"], "John")
        self.assertEqual(serializer.data["last_name"], "Doe")


class GenreSerializerTest(TestCase):
    def test_genre_serialization(self):
        genre = Genre.objects.create(name="Comedy")
        serializer = GenreSerializer(genre)
        self.assertEqual(serializer.data["name"], "Comedy")


class PlaySerializerTest(TestCase):
    def setUp(self):
        self.actor = Actor.objects.create(first_name="Alice", last_name="Smith")
        self.genre = Genre.objects.create(name="Drama")

    def test_play_serialization(self):
        play = Play.objects.create(title="Macbeth", description="Shakespeare")
        play.actors.add(self.actor)
        play.genres.add(self.genre)
        serializer = PlaySerializer(play)
        self.assertEqual(serializer.data["title"], "Macbeth")
        self.assertIn(self.actor.id, serializer.data["actors"])
        self.assertIn(self.genre.id, serializer.data["genres"])


class TheatreHallSerializerTest(TestCase):
    def test_hall_serialization(self):
        hall = TheatreHall.objects.create(name="Main Hall", rows=10, seat_in_row=20)
        serializer = TheatreHallSerializer(hall)
        self.assertEqual(serializer.data["capacity"], 200)


class PerformanceSerializerTest(TestCase):
    def setUp(self):
        self.play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.hall = TheatreHall.objects.create(name="Main Hall", rows=5, seat_in_row=5)

    def test_performance_serialization(self):
        show_time = datetime.now()
        performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=show_time
        )
        serializer = PerformanceSerializer(performance)
        self.assertEqual(serializer.data["play"], self.play.id)
        self.assertEqual(serializer.data["theatre_hall"], self.hall.id)


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.hall = TheatreHall.objects.create(name="Hall", rows=5, seat_in_row=5)
        self.play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=datetime.now()
        )
        self.order = Order.objects.create(user=self.user)

    def test_ticket_valid_serializer(self):
        ticket = Ticket.objects.create(
            performance=self.performance, order=self.order, row=1, seat_in_row=1
        )
        serializer = TicketSerializer(ticket)
        self.assertEqual(serializer.data["row"], 1)
        self.assertEqual(serializer.data["seat_in_row"], 1)

    def test_ticket_row_seat_validation(self):
        data = {
            "performance": self.performance,
            "row": 6,
            "seat_in_row": 1
        }
        serializer = TicketRowSeatSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        data = {
            "performance": self.performance,
            "row": 1,
            "seat_in_row": 6
        }
        serializer = TicketRowSeatSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class OrderSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.hall = TheatreHall.objects.create(name="Hall", rows=5, seat_in_row=5)
        self.play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=datetime.now()
        )

    def test_order_creation_with_tickets(self):
        data = {
            "user_id": self.user.id,
            "tickets": [
                {"performance_id": self.performance.id, "row": 1, "seat_in_row": 1},
                {"performance_id": self.performance.id, "row": 2, "seat_in_row": 2}
            ]
        }
        print(data)
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.tickets.count(), 2)
        self.assertEqual(order.tickets.first().row, 1)