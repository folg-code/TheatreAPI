from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase

from theatre_service.models import Actor, Genre, Play, TheatreHall, Performance, Order, Ticket

User = get_user_model()


class ActorModelTest(TestCase):
    def test_full_name_property(self):
        actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.assertEqual(actor.full_name, "John Doe")
        self.assertEqual(str(actor), "John Doe")


class GenreModelTest(TestCase):
    def test_str_method(self):
        genre = Genre.objects.create(name="Comedy")
        self.assertEqual(str(genre), "Comedy")


class PlayModelTest(TestCase):
    def test_str_method(self):
        play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.assertEqual(str(play), "Hamlet")

    def test_many_to_many_fields(self):
        play = Play.objects.create(title="Macbeth", description="Shakespeare")
        actor = Actor.objects.create(first_name="Alice", last_name="Smith")
        genre = Genre.objects.create(name="Drama")
        play.actors.add(actor)
        play.genres.add(genre)
        self.assertIn(actor, play.actors.all())
        self.assertIn(genre, play.genres.all())


class TheatreHallModelTest(TestCase):
    def test_capacity_property_and_str(self):
        hall = TheatreHall.objects.create(name="Main Hall", rows=10, seat_in_row=20)
        self.assertEqual(hall.capacity, 200)
        self.assertEqual(str(hall), "Main Hall")


class PerformanceModelTest(TestCase):
    def setUp(self):
        self.play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.hall = TheatreHall.objects.create(name="Main Hall", rows=5, seat_in_row=5)

    def test_str_method(self):
        show_time = timezone.now()
        performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=show_time
        )
        self.assertIn("Hamlet", str(performance))
        self.assertIn(str(show_time), str(performance))


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass")

    def test_order_creation_and_str(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.user, self.user)
        self.assertIsNotNone(order.created_at)
        self.assertEqual(str(order), str(order.created_at))


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.hall = TheatreHall.objects.create(name="Hall", rows=5, seat_in_row=5)
        self.play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=timezone.now()
        )
        self.order = Order.objects.create(user=self.user)

    def test_ticket_valid(self):
        ticket = Ticket(performance=self.performance, order=self.order, row=1, seat_in_row=1)
        ticket.full_clean()
        ticket.save()
        self.assertEqual(ticket.row, 1)
        self.assertEqual(ticket.seat_in_row, 1)

    def test_ticket_invalid_row(self):
        ticket = Ticket(performance=self.performance, order=self.order, row=6, seat_in_row=1)
        with self.assertRaises(ValidationError) as cm:
            ticket.full_clean()
        self.assertIn("row", cm.exception.message_dict)

    def test_ticket_invalid_seat(self):
        ticket = Ticket(performance=self.performance, order=self.order, row=1, seat_in_row=6)
        with self.assertRaises(ValidationError) as cm:
            ticket.full_clean()
        self.assertIn("seat", cm.exception.message_dict)

    def test_ticket_str_method(self):
        ticket = Ticket.objects.create(performance=self.performance, order=self.order, row=2, seat_in_row=3)
        self.assertIn("row: 2", str(ticket))
        self.assertIn("seat: 3", str(ticket))