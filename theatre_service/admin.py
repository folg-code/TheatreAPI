from django.contrib import admin

from theatre_service.models import Genre, Actor, Play, TheatreHall, Performance, Ticket, Order
from user.models import User

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Play)
admin.site.register(TheatreHall)
admin.site.register(Performance)
admin.site.register(Order)
admin.site.register(Ticket)
