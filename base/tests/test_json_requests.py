from django.test import TestCase
from .utils import load_fixture, rand_id, create_authenticated_client
from ..traitinfo.traits import Trait


class TestJSONRequests(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    def test_traitnames(self):
        response = self.client.get("/traitnames")
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {t.name: t.net_merit_dollars for t in Trait.get_all()} | {"Net Merit": 0},
        )

    @load_fixture("class_light.json")
    def test_herdsummaries(self):
        response = self.client.get("/herdsummaries")
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("public", json)
        self.assertIn("private", json)

    @load_fixture("class.json")
    def test_herdsummary(self):
        response = self.client.get(f"/herdsummary-{2}")
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("Net Merit", json)
        self.assertIn("MILK", json)

        self.assertEquals(json["Net Merit"], -22.571)
        self.assertEquals(json["FLC"], 0.03)

    @load_fixture("class.json")
    def test_herddata(self):
        response = self.client.get(f"/herddata-{2}")
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("cows", json)
        self.assertIn("bulls", json)
        self.assertIn(f"{482}", json["cows"])
        self.assertIn("traits", json["cows"][f"{482}"])

    @load_fixture("class.json")
    def test_get_cow_name(self):
        response = self.client.get(f"/get-cow-name/{1}/{481}")
        self.assertEquals(response.status_code, 200)

        self.assertJSONEqual(response.content, {"name": "Test Class' SCS Star"})

    @load_fixture("class_largeplus.json")
    def test_get_pedigree(self):
        response = self.client.get(f"/get-pedigree-{909}")
        self.assertEquals(response.status_code, 200)

        self.assertJSONEqual(
            response.content, {"id": 909, "sire": None, "dam": {"id": 696}}
        )

    @load_fixture("class")
    def test_get_cow_data(self):
        response = self.client.get(f"/get-data-{555}")
        self.assertEquals(response.status_code, 200)

        json = response.json()
        self.assertIn("successful", json)
        self.assertIn("Generation", json)
        self.assertIn("recessives", json)
        self.assertIn(f"BLAD", json["recessives"])