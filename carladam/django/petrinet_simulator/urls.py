from django.urls import path

from carladam.django.petrinet_simulator import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:net_name>/", views.simulator, name="simulator"),
]
