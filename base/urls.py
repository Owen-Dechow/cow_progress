from django.urls import path
from . import views

urlpatterns = (
    [  ########### Page patterns ###########
        path("", views.home, name="home"),
        path("herds", views.herds, name="herds"),
        path("openherd-<int:herdID>", views.open_herd, name="openherd"),
        path("account", views.account, name="account"),
        path("classes", views.classes, name="classes"),
        path("recessives/<str:traitset>", views.recessives, name="recessives"),
        path("pedigree", views.pedigree, name="pedigree"),
        path("cookies", views.cookies, name="cookies"),
        path("credits", views.app_credits, name="credits"),
    ]
    + [  ########### JSON patterns ###########
        path("herdsummaries", views.herdsummaries),
        path("herdsummary-<int:herdID>", views.herdsummary),
        path("herddata-<int:herdID>", views.get_herd_data),
        path("get-cow-name/<int:classID>/<int:cowID>", views.get_bull_name),
        path("get-pedigree-<int:pedigreeID>", views.get_pedigree),
        path("get-data-<int:cowID>", views.get_cow_data),
    ]
    + [  ########### File patterns ###########
        path("herd-file/<int:herdID>", views.get_herd_file),
        path("classtrend-file/<int:classID>", views.get_class_tendchart),
        path("classdata-file/<int:classID>", views.get_class_datafile),
    ]
    + [  ########### Actions -> success dict ###########
        path("move-cow/<int:cowID>", views.move_cow),
        path("set-cow-name/<int:cowID>/<str:name>", views.change_name),
    ]
    + [  ########### Actions -> redirect ###########
        path("breed-herd/<int:herdID>", views.breed_herd, name="new-herd"),
        path("auto-generate-herd", views.auto_generate_herd, name="autogenerate-herd"),
        path("delete-herd/<int:herdID>", views.delete_herd, name="delete-herd"),
    ]
)
