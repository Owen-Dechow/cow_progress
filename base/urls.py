from django.urls import path
from . import views

urlpatterns = [
    # HTML Responses
    path("", views.home, name="home"),
    path("herds", views.herds, name="herds"),
    path("open-herd/<int:herdID>", views.open_herd, name="openherd"),
    path("breed-herd/<int:herdID>", views.breed_herd, name="new-herd"),
    path("auto-generate-herd", views.auto_generate_herd, name="autogenerate-herd"),
    path("delete-herd/<int:herdID>", views.delete_herd, name="delete-herd"),
    path("account", views.account, name="account"),
    path("classes", views.classes, name="classes"),
    # JSON Responses
    path("move-cow/<int:cowID>/<str:gender>", views.move_cow),
    path("traitnames", views.traitnames),
    path("herdsummaries", views.herdsummaries),
    path("herd-data/<int:herdID>", views.get_herd_data),
    path("get-cow-name/<int:cowID>", views.get_bull_name),
    path("set-cow-name/<int:cowID>/<str:gender>/<str:name>", views.change_name),
    path("set-classinfo/<int:classID>/<str:info>", views.setclassinfo),
    path("delete-enrollment/<int:enrollmentID>", views.delete_enrollment),
    # Other
    path("herd-file/<int:herdID>", views.get_herd_file),
]
