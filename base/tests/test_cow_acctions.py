from django.test import TestCase
from base import models
from .utils import load_fixture, rand_id, create_authenticated_client


class TestCowActions(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    @load_fixture("class_large.json")
    def test_move_cow(self):
        animal = models.Bovine.objects.get(id=777)

        response = self.client.get(f"/move-cow/{animal.id}")
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content, {"successful": True})

        animal = models.Bovine.objects.get(id=animal.id)
        self.assertEquals(animal.herd, animal.connectedclass.herd)
        self.assertIn("[John Doe]", animal.name)

    @load_fixture("class_large.json")
    def test_set_cow_name(self):
        animal = models.Bovine.objects.get(id=777)
        target_name = f"TestName-{rand_id()}"

        response = self.client.get(f"/set-cow-name/{animal.id}/{target_name}")
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content, {"successful": True})

        animal = models.Bovine.objects.get(id=animal.id)
        self.assertEquals(animal.name, target_name)
