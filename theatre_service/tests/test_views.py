from datetime import datetime
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from theatre_service.models import (
    Genre, Actor, Play, TheatreHall, Performance, Order, Ticket
)

User = get_user_model()


class ViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.client = APIClient()

        self.genre = Genre.objects.create(name="Drama")
        self.actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.play = Play.objects.create(title="Hamlet", description="Shakespeare")
        self.play.genres.add(self.genre)
        self.play.actors.add(self.actor)
        self.hall = TheatreHall.objects.create(name="Main Hall", rows=5, seat_in_row=5)
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=datetime.now()
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            performance=self.performance, order=self.order, row=1, seat_in_row=1
        )

    def test_genre_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("genres-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_genre_create_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("genres-list")
        data = {"name": "Comedy"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Genre.objects.filter(name="Comedy").exists())

    def test_actor_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("actors-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_actor_create_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("actors-list")
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Actor.objects.filter(first_name="Jane").exists())

    def test_play_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("plays-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Hamlet", str(response.data))

    def test_play_retrieve(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("plays-detail", args=[self.play.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Hamlet")

    def test_theatre_hall_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("halls-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_performance_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("performers-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_performance_filter_by_play(self):
        self.client.force_authenticate(user=self.user)
        url = f"{reverse('performers-list')}?play={self.play.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all("play" in p for p in response.data))

    def test_order_list_for_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_order_create_with_tickets(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")
        data = {
            "tickets": [
                {"performance_id": self.performance.id, "row": 2, "seat_in_row": 2},
                {"performance_id": self.performance.id, "row": 3, "seat_in_row": 3}
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 2)
        new_order = Order.objects.latest("id")
        self.assertEqual(new_order.tickets.count(), 2)