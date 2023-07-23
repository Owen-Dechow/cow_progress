from django.test import TestCase
from .utils import load_fixture, create_authenticated_client


class TestPages(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    def general_assertions(self, response, template):
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def test_home(self):
        response = self.client.get("/", secure=True)
        self.general_assertions(response, "base/home.html")

    def test_herds(self):
        response = self.client.get("/herds", secure=True)
        self.general_assertions(response, "base/herds.html")

    @load_fixture("class_light.json")
    def test_openherd(self):
        response = self.client.get(f"/openherd-{1}", secure=True)
        self.general_assertions(response, "base/open_herd.html")

    def test_account(self):
        response = self.client.get("/account", secure=True)
        self.general_assertions(response, "auth/account.html")

    def test_classes(self):
        response = self.client.get("/classes", secure=True)
        self.general_assertions(response, "base/classes.html")

    def test_recessives(self):
        response = self.client.get("/recessives", secure=True)
        self.general_assertions(response, "base/recessives.html")

    def test_pedigree(self):
        response = self.client.get("/pedigree", secure=True)
        self.general_assertions(response, "base/pedigree.html")

    def test_cookies(self):
        response = self.client.get("/cookies", secure=True)
        self.general_assertions(response, "base/cookies.html")

    def test_credits(self):
        response = self.client.get("/credits", secure=True)
        self.general_assertions(response, "base/credits.html")
