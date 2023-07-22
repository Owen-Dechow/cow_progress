from django.core.management import call_command
from django.test import Client
from random import randint
from django.contrib.auth.models import User


def create_authenticated_client(username) -> Client:
    client = Client()
    User.objects.create_user(username=username, password="password")
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
