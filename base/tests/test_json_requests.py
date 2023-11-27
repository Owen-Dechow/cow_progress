from django.test import TestCase
from .utils import load_fixture, create_authenticated_client


class TestJSONRequests(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    @load_fixture("class_no_cows.json")
    def test_herdsummaries(self):
        response = self.client.get("/herdsummaries", secure=True)
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("public", json)
        self.assertIn("private", json)

    @load_fixture("class.json")
    def test_herdsummary(self):
        response = self.client.get(f"/herdsummary-{2}", secure=True)
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("FLC", json)
        self.assertIn("ph: FLC", json)

        self.assertEquals(json["ph: FLC"], 0.074)
        self.assertEquals(json["FLC"], 0.074)

    @load_fixture("class.json")
    def test_herddata(self):
        response = self.client.get(f"/herddata-{2}", secure=True)
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("cows", json)
        self.assertIn("bulls", json)
        self.assertIn(f"{1}", json["cows"])
        self.assertIn("traits", json["cows"][f"{1}"])

    @load_fixture("class.json")
    def test_get_cow_name(self):
        response = self.client.get(f"/get-cow-name/{1}/{152}", secure=True)
        self.assertEquals(response.status_code, 200)

        self.assertJSONEqual(response.content, {"name": "Test Class' 152"})

    @load_fixture("class_bred_herd.json")
    def test_get_pedigree(self):
        response = self.client.get(f"/get-pedigree-{314}", secure=True)
        self.assertEquals(response.status_code, 200)

        self.assertJSONEqual(
            response.content, {"id": 314, "sire": {"id": 151}, "dam": {"id": 161}}
        )

    @load_fixture("class")
    def test_get_cow_data(self):
        response = self.client.get(f"/get-data-{1}", secure=True)
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("successful", json)
        self.assertIn("Generation", json)
        self.assertIn("recessives", json)
        self.assertIn(f"BLAD", json["recessives"])
