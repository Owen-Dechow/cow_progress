from django.test import TestCase
from base import models
from utils import load_fixture, rand_id, create_authenticated_client


class TestHerdActions(TestCase):
    def setUp(self):
        self.client = create_authenticated_client()

    @load_fixture("class_light.json")
    def test_auto_generate_herd(self):
        herd_name = f"Test herd {rand_id()}"
        response = self.client.post(
            "/auto-generate-herd",
            {
                "name": herd_name,
                "class": 1,
            },
            secure=True,
        )

        self.assertEquals(models.Herd.objects.last().name, herd_name)
        self.assertEquals(response.status_code, 302)

    @load_fixture("class_large.json")
    def test_delete_herd(self):
        _ = self.client.get("/delete-herd/3", secure=True)
        self.assertEquals(models.Herd.objects.count(), 2)

    @load_fixture("class_large.json")
    def test_breed_herd(self):
        bulls = models.Bovine.objects.filter(male=True)[:10]
        start_num = models.Bovine.objects.count()

        _ = self.client.post(
            "/breed-herd/3",
            {f"bull-{idx}": bull.id for idx, bull in enumerate(bulls)},
            secure=True,
        )

        _ = self.client.post(
            "/breed-herd/3",
            {f"bull-0": bulls[0].id},
            secure=True,
        )

        self.assertGreater(models.Bovine.objects.count(), start_num)
        self.assertEquals(models.Herd.objects.get(id=3).breedings, 1)
