from django.test import TestCase
from base import models
from ..utils import load_fixture, rand_id, create_authenticated_client, INFO


class TestHerdActions(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    @load_fixture("class_no_cows.json")
    def test_auto_generate_herd(self):
        herd_name = f"Test herd {rand_id()}"
        response = self.client.post(
            f"/class/{INFO.CLASS_ID}/herds/generate/",
            {
                "name": herd_name,
            },
            secure=True,
        )

        self.assertEqual(models.Herd.objects.last().name, herd_name)
        self.assertEqual(response.status_code, 302)

    @load_fixture("class_personal_herd.json")
    def test_delete_herd(self):
        _ = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.PERSONAL_HERD_ID}/delete/", secure=True
        )
        self.assertEqual(models.Herd.objects.count(), 2)

    @load_fixture("class_personal_herd.json")
    def test_breed_herd(self):
        bulls = models.Bovine.objects.filter(male=True)[:10]
        start_num = models.Bovine.objects.count()

        _ = self.client.post(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.PERSONAL_HERD_ID}/breed/",
            {f"bull-{idx}": bull.id for idx, bull in enumerate(bulls)},
            secure=True,
        )

        self.assertGreater(models.Bovine.objects.count(), start_num)
        self.assertEqual(models.Herd.objects.get(id=INFO.PERSONAL_HERD_ID).breedings, 1)
