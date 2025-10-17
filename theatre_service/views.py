from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, F, IntegerField, ExpressionWrapper
from django.utils.dateparse import parse_date
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
)
from .models import Genre, Actor, Play, TheatreHall, Performance, Order
from .serializers import (
    GenreSerializer,
    ActorSerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PlaySerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    OrderSerializer,
)
from .permissions import IsAdminOrIfAuthenticatedReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List all genres",
        tags=["Genres"],
        responses={200: GenreSerializer},
        examples=[
            OpenApiExample("Genre list example",
                           value=[{"id": 1,
                                   "name": "Drama"}
                                  ]
                           )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve genre",
        tags=["Genres"],
        responses={200: GenreSerializer},
        examples=[
            OpenApiExample("Genre detail example",
                           value={"id": 1,
                                  "name": "Comedy"})
        ],
    ),
    create=extend_schema(
        summary="Create genre",
        tags=["Genres"],
        request=GenreSerializer,
        responses={201: GenreSerializer},
        examples=[
            OpenApiExample(
                "Create genre example",
                request_only=True,
                value={"name": "Romance"},
            )
        ],
    ),
    update=extend_schema(
        summary="Update genre",
        tags=["Genres"],
        request=GenreSerializer,
        responses={200: GenreSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update genre",
        tags=["Genres"],
        request=GenreSerializer,
        responses={200: GenreSerializer},
    ),
    destroy=extend_schema(
        summary="Delete genre",
        tags=["Genres"],
        responses={204: None},
    ),
)
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


@extend_schema_view(
    list=extend_schema(summary="List all actors",
                       tags=["Actors"],
                       responses={200: ActorSerializer}
                       ),
    retrieve=extend_schema(summary="Retrieve actor",
                           tags=["Actors"],
                           responses={200: ActorSerializer}
                           ),
    create=extend_schema(
        summary="Create actor",
        tags=["Actors"],
        request=ActorSerializer,
        responses={201: ActorSerializer},
        examples=[OpenApiExample("Create actor",
                                 value={"first_name": "Tom",
                                        "last_name": "Hanks"}
                                 )
                  ],
    ),
    update=extend_schema(summary="Update actor",
                         tags=["Actors"],
                         request=ActorSerializer,
                         responses={200: ActorSerializer}
                         ),
    partial_update=extend_schema(summary="Partially update actor",
                                 tags=["Actors"],
                                 request=ActorSerializer,
                                 responses={200: ActorSerializer}
                                 ),
    destroy=extend_schema(summary="Delete actor",
                          tags=["Actors"],
                          responses={204: None}
                          ),
)
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


@extend_schema_view(
    list=extend_schema(
        summary="List all plays",
        tags=["Plays"],
        responses={200: PlayListSerializer},
    ),
    retrieve=extend_schema(
        summary="Retrieve play",
        tags=["Plays"],
        responses={200: PlayDetailSerializer},
    ),
    create=extend_schema(
        summary="Create play",
        tags=["Plays"],
        request=PlaySerializer,
        responses={201: PlaySerializer},
        examples=[
            OpenApiExample(
                "Create play example",
                value={
                    "title": "Macbeth",
                    "description": "A Shakespearean tragedy.",
                    "genres": [1],
                    "actors": [2, 3],
                },
            )
        ],
    ),
    update=extend_schema(summary="Update play",
                         tags=["Plays"],
                         request=PlaySerializer,
                         responses={200: PlaySerializer}
                         ),
    partial_update=extend_schema(summary="Partially update play",
                                 tags=["Plays"],
                                 request=PlaySerializer,
                                 responses={200: PlaySerializer}
                                 ),
    destroy=extend_schema(summary="Delete play",
                          tags=["Plays"],
                          responses={204: None}
                          ),
)
class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlayListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


@extend_schema_view(
    list=extend_schema(summary="List theatre halls",
                       tags=["Theatre Halls"],
                       responses={200: TheatreHallSerializer}
                       ),
    retrieve=extend_schema(summary="Retrieve theatre hall",
                           tags=["Theatre Halls"],
                           responses={200: TheatreHallSerializer}
                           ),
    create=extend_schema(
        summary="Create theatre hall",
        tags=["Theatre Halls"],
        request=TheatreHallSerializer,
        responses={201: TheatreHallSerializer},
        examples=[
            OpenApiExample(
                "Create theatre hall",
                value={"name": "Grand Hall", "rows": 20, "seat_in_row": 30},
            )
        ],
    ),
    update=extend_schema(summary="Update theatre hall",
                         tags=["Theatre Halls"],
                         request=TheatreHallSerializer,
                         responses={200: TheatreHallSerializer}
                         ),
    partial_update=extend_schema(summary="Partially update theatre hall",
                                 tags=["Theatre Halls"],
                                 request=TheatreHallSerializer,
                                 responses={200: TheatreHallSerializer}
                                 ),
    destroy=extend_schema(summary="Delete theatre hall",
                          tags=["Theatre Halls"],
                          responses={204: None}
                          ),
)
class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


@extend_schema_view(
    list=extend_schema(
        summary="List performances",
        tags=["Performances"],
        parameters=[
            OpenApiParameter(name="play",
                             description="Filter by play ID",
                             type=int,
                             required=False
                             ),
            OpenApiParameter(name="date",
                             description="Filter by date (YYYY-MM-DD)",
                             type=str,
                             required=False
                             ),
        ],
        responses={200: PerformanceListSerializer},
    ),
    retrieve=extend_schema(summary="Retrieve performance",
                           tags=["Performances"],
                           responses={200: PerformanceDetailSerializer}
                           ),
    create=extend_schema(
        summary="Create performance",
        tags=["Performances"],
        request=PerformanceSerializer,
        responses={201: PerformanceSerializer},
        examples=[
            OpenApiExample(
                "Create performance",
                value={
                    "play": 1,
                    "theatre_hall": 2,
                    "show_time": "2025-10-16T19:00:00Z",
                },
            )
        ],
    ),
    update=extend_schema(summary="Update performance",
                         tags=["Performances"],
                         request=PerformanceSerializer,
                         responses={200: PerformanceSerializer}
                         ),
    partial_update=extend_schema(summary="Partially update performance",
                                 tags=["Performances"],
                                 request=PerformanceSerializer,
                                 responses={200: PerformanceSerializer}),
    destroy=extend_schema(summary="Delete performance",
                          tags=["Performances"],
                          responses={204: None}
                          ),
)
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer

    def get_queryset(self):
        if self.action == "list":
            qs = Performance.objects.all().select_related("theatre_hall")
            qs = qs.annotate(
                taken=Count("tickets"),
                capacity=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seat_in_row"),
                    output_field=IntegerField(),
                ),
                available=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seat_in_row")
                    - Count("tickets"),
                    output_field=IntegerField(),
                ),
            )

            play_filter = self.request.query_params.get("play")
            if play_filter:
                qs = qs.filter(play_id=play_filter)

            date_filter = self.request.query_params.get("date")
            if date_filter:
                date_obj = parse_date(date_filter)
                if date_obj:
                    qs = qs.filter(show_time__date=date_obj)
            return qs
        elif self.action == "retrieve":
            return Performance.objects.all().select_related("theatre_hall")
        return Performance.objects.all()


class OrderPagination(PageNumberPagination):
    page_size = 10


@extend_schema_view(
    list=extend_schema(summary="List user orders",
                       tags=["Orders"],
                       responses={200: OrderSerializer}
                       ),
    retrieve=extend_schema(summary="Retrieve order",
                           tags=["Orders"],
                           responses={200: OrderSerializer}
                           ),
    create=extend_schema(
        summary="Create order",
        tags=["Orders"],
        request=OrderSerializer,
        responses={201: OrderSerializer},
        examples=[
            OpenApiExample(
                "Create order",
                value={
                    "tickets": [
                        {"performance_id": 1, "row": 5, "seat_in_row": 10},
                        {"performance_id": 1, "row": 5, "seat_in_row": 11},
                    ]
                },
            )
        ],
    ),
    update=extend_schema(summary="Update order",
                         tags=["Orders"],
                         request=OrderSerializer,
                         responses={200: OrderSerializer}
                         ),
    partial_update=extend_schema(summary="Partially update order",
                                 tags=["Orders"], request=OrderSerializer,
                                 responses={200: OrderSerializer}
                                 ),
    destroy=extend_schema(summary="Delete order",
                          tags=["Orders"],
                          responses={204: None}
                          ),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
