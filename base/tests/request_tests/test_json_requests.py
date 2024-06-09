from django.test import TestCase
from ..utils import load_fixture, create_authenticated_client, INFO
from base import models


class TestJSONRequests(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    @load_fixture("class.json")
    def test_get_herdsummaries(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/summaries/", secure=True
        )
        self.assertEqual(response.status_code, 200)

        json = response.json()
        self.assertIn("public", json)
        self.assertIn("private", json)

    @load_fixture("class.json")
    def test_get_herdsummary(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.PUBLIC_HERD_ID}/summary/", secure=True
        )
        self.assertEqual(response.status_code, 200)

        json = response.json()
        self.assertIn("FLC", json)
        self.assertIn("ph: FLC", json)

        self.assertEqual(json["ph: FLC"], 0.074)
        self.assertEqual(json["FLC"], 0.074)

    @load_fixture("class.json")
    def test_get_herddata(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.PUBLIC_HERD_ID}/data/", secure=True
        )
        self.assertEqual(response.status_code, 200)

        json = response.json()
        self.assertIn("cows", json)
        self.assertIn("bulls", json)
        self.assertIn(f"{1}", json["cows"])
        self.assertIn("traits", json["cows"][f"{1}"])

    @load_fixture("class.json")
    def test_get_bull_name(self):

        response = self.client.get(
            f"/class/{INFO.CLASS_HERD_ID}/bullname/{INFO.PUBLIC_M_ID}/", secure=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"name": models.Bovine.objects.get(id=INFO.PUBLIC_M_ID).name},
        )

    @load_fixture("class_bred_herd.json")
    def test_get_pedigree(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/pedigree/{INFO.BRED_F_ID}/get/", secure=True
        )
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            response.content, models.Bovine.objects.get(id=INFO.BRED_F_ID).pedigree
        )

    @load_fixture("class")
    def test_get_cow_data(self):
        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/pedigree/{INFO.PUBLIC_F_ID}/data/", secure=True
        )
        self.assertEqual(response.status_code, 200)

        json = response.json()
        self.assertIn("successful", json)
        self.assertIn("Generation", json)
        self.assertIn("recessives", json)
        self.assertIn(f"BLAD", json["recessives"])
