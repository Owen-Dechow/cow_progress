from django.test import TestCase
from ..utils import load_fixture, create_authenticated_client


class TestFileRequests(TestCase):
    def setUp(self):
        self.client = create_authenticated_client("client")

    @load_fixture("class.json")
    def test_get_herd_file(self):
        response = self.client.get(f"/herd-file/2", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("attachment; filename=" in response.get("Content-Disposition"))

    @load_fixture("class.json")
    def test_get_class_tendchart(self):
        response = self.client.get(f"/classtrend-file/1", secure=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue("attachment; filename=" in response.get("Content-Disposition"))
