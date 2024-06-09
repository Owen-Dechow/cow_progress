from django.test import TestCase
from ..utils import load_fixture, create_authenticated_client, INFO


class TestPages(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    def general_assertions(self, response, template):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def test_home(self):
        response = self.client.get("/", secure=True)
        self.general_assertions(response, "base/home.html")

    @load_fixture("class_no_cows.json")
    def test_herds(self):
        response = self.client.get(f"/class/{INFO.CLASS_ID}/herds/", secure=True)
        self.general_assertions(response, "base/herds.html")

    @load_fixture("class_no_cows.json")
    def test_openherd(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.CLASS_HERD_ID}/", secure=True
        )
        self.general_assertions(response, "base/open_herd.html")

    def test_account(self):
        response = self.client.get("/account/", secure=True)
        self.general_assertions(response, "auth/account.html")

    @load_fixture("class_no_cows.json")
    def test_classes(self):
        response = self.client.get(f"/class/{INFO.CLASS_ID}/", secure=True)
        self.general_assertions(response, "base/class.html")

    @load_fixture("class_no_cows.json")
    def test_recessives(self):
        response = self.client.get(f"/class/{INFO.CLASS_ID}/recessives/", secure=True)
        self.general_assertions(response, "base/recessives.html")

    @load_fixture("class.json")
    def test_pedigree(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/pedigree/{INFO.PUBLIC_M_ID}/", secure=True
        )
        self.general_assertions(response, "base/pedigree.html")

    def test_cookies(self):
        response = self.client.get("/cookies/", secure=True)
        self.general_assertions(response, "base/cookies.html")

    def test_credits(self):
        response = self.client.get("/credits/", secure=True)
        self.general_assertions(response, "base/credits.html")
