from django.test import TestCase
from base import models
from ..utils import load_fixture, rand_id, create_authenticated_client, INFO


class TestCowActions(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    @load_fixture("class_personal_herd.json")
    def test_move_cow(self):
        animal = models.Bovine.objects.get(id=311)

        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.PERSONAL_HERD_ID}/animal/{animal.id}/move/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"successful": True})

        animal = models.Bovine.objects.get(id=animal.id)
        self.assertEqual(animal.herd, animal.connectedclass.herd)
        self.assertIn("[John Doe]", animal.name)

    @load_fixture("class_personal_herd.json")
    def test_set_cow_name(self):
        animal = models.Bovine.objects.get(id=311)
        target_name = f"TestName-{rand_id()}"

        response = self.client.get(
            f"/class/{INFO.CLASS_ID}/herds/{INFO.PERSONAL_HERD_ID}/animal/{animal.id}/rename/{target_name}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"successful": True})

        animal = models.Bovine.objects.get(id=animal.id)
        self.assertEqual(animal.name, target_name)
