from django.core.management import call_command
from django.test import Client
from random import randint, random
from django.contrib.auth.models import User
from ..traitinfo.traitsets import TraitSet


class Info:
    PUBLIC_F_ID = 1
    PUBLIC_M_ID = 151
    BRED_F_ID = 313
    CLASS_HERD_ID = 1
    PUBLIC_HERD_ID = 2
    PERSONAL_HERD_ID = 3
    BRED_PEDIGREE = {
        "id": -1,
        "sire": {"id": PUBLIC_M_ID},
        "dam": {"id": PUBLIC_F_ID},
    }
    TRAITSET = TraitSet("NM_2021")
    CLASS_ID = 1
    BOVINE_1_NAME = "[Test Class] Public Herd's 1"
    INBRED_PEDIGREE = {
        "id": 314,
        "sire": {"id": 151},
        "dam": {"id": 161, "sire": {"id": 151}, "dam": {"id": -1}},
    }
    INBRED_PEDIGREE_COEFFICIENT = 0.25


INFO = Info()


def create_authenticated_client(username) -> Client:
    client = Client()
    User.objects.create_user(
        username=username, password="password", first_name="John", last_name="Doe"
    )
    client.login(username=username, password="password")

    return client


def load_fixture(fixture: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            call_command("loaddata", fixture, verbosity=0)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def rand_id():
    return randint(1, 99999)


def rand_from_sd(sd):
    return random() * sd
