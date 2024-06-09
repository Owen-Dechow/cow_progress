from django.urls import path
from . import views

urlpatterns = [  ########### Page patterns ###########
    path("", views.home, name="home"),
    path("account/", views.account, name="account"),
    path("cookies/", views.cookies, name="cookies"),
    path("credits/", views.app_credits, name="credits"),
    # New class based
    path("class/new/", views.new_class),
    path("class/join/", views.join_class),
    path("class/<int:class_id>/", views.open_class),
    path("class/<int:class_id>/", views.open_class),
    path("class/<int:class_id>/recessives/", views.recessives),
    path("class/<int:class_id>/update/", views.update_class),
    path("class/<int:class_id>/delete/", views.delete_class),
    path("class/<int:class_id>/exit/", views.exit_class),
    path("class/<int:class_id>/promote/", views.promote_class),
    path("class/<int:class_id>/trendfile/", views.get_class_tendchart),
    path("class/<int:class_id>/datafile/", views.get_class_datafile),
    path("class/<int:class_id>/herds/", views.herds),
    path("class/<int:class_id>/herds/generate/", views.auto_generate_herd),
    path("class/<int:class_id>/herds/summaries/", views.herdsummaries),
    path("class/<int:class_id>/herds/<int:herd_id>/", views.open_herd),
    path("class/<int:class_id>/herds/<int:herd_id>/file/", views.get_herd_file),
    path("class/<int:class_id>/herds/<int:herd_id>/breed/", views.breed_herd),
    path("class/<int:class_id>/herds/<int:herd_id>/summary/", views.herdsummary),
    path("class/<int:class_id>/herds/<int:herd_id>/data/", views.herddata),
    path("class/<int:class_id>/herds/<int:herd_id>/delete/", views.delete_herd),
    path(
        "class/<int:class_id>/herds/<int:herd_id>/animal/<int:animal_id>/move/",
        views.move_animal,
    ),
    path(
        "class/<int:class_id>/herds/<int:herd_id>/animal/<int:animal_id>/rename/<str:name>/",
        views.rename,
    ),
    path("class/<int:class_id>/bullname/<int:bull_id>/", views.get_bull_name),
    path("class/<int:class_id>/pedigree/<int:animal_id>/", views.pedigree),
    path("class/<int:class_id>/pedigree/<int:animal_id>/get/", views.get_pedigree),
    path("class/<int:class_id>/pedigree/<int:animal_id>/data/", views.get_cow_data),
]
