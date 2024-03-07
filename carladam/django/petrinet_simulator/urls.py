# Pip imports
from django.urls import path

# Internal imports
from carladam.django.petrinet_simulator import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:net_name>/", views.simulator, name="simulator"),
]
