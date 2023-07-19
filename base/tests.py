from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from base import models
from django.core.management import call_command
from random import randint


def load_fixture(fixture: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            call_command("loaddata", fixture, verbosity=0)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def rand_id():
    return randint(1, 99999)


class TestClassSystem(TestCase):
    def setUp(self):
        # Create teacher
        self.teacher = Client()
        User.objects.create_user(username="teacher", password="password")
        self.teacher.login(username="teacher", password="password")

        # Create students
        self.students = [Client() for _ in range(3)]
        for idx, student in enumerate(self.students):
            User.objects.create_user(username=f"student_{idx}", password="password")
            student.login(username=f"student_{idx}", password="password")

    def test_addclass(self):
        response = self.teacher.post(
            "/classes",
            {
                "connectedclass": f"Test Class {rand_id()}",
                "info": f"Test Class Info {rand_id()}",
                "formid": "addclass",
            },
            secure=True,
        )

        self.assertEquals(models.Class.objects.count(), 1)

    @load_fixture("class_light.json")
    def test_joinclass(self):
        classcode = models.Class.objects.first().classcode

        for student in self.students:
            _ = student.post(
                "/classes",
                {
                    "connectedclass": classcode,
                    "formid": "joinclass",
                },
                secure=True,
            )

        self.assertEquals(models.Enrollment.objects.count(), len(self.students) + 1)

    @load_fixture("class_light.json")
    def test_exitclass(self):
        connectedclass = models.Class.objects.first()
        classcode = connectedclass.classcode

        for student in self.students:
            _ = student.post(
                "/classes",
                {
                    "connectedclass": classcode,
                    "formid": "joinclass",
                },
                secure=True,
            )

            _ = student.post(
                "/classes",
                {
                    "connectedclass": connectedclass.id,
                    "formid": "exitclass",
                },
                secure=True,
            )

        self.assertEquals(models.Enrollment.objects.count(), 1)

    @load_fixture("class_light.json")
    def test_deleteclass(self):
        self.teacher.post(
            "/classes",
            {
                "connectedclass": 1,
                "formid": "deleteclass",
            },
            secure=True,
        )

        self.assertEquals(models.Class.objects.count(), 0)

    @load_fixture("class_light.json")
    def test_premoteclass(self):
        connectedclass = models.Class.objects.first()
        classcode = connectedclass.classcode
        teacherclasscode = connectedclass.teacherclasscode

        for student in self.students:
            _ = student.post(
                "/classes",
                {
                    "connectedclass": classcode,
                    "formid": "joinclass",
                },
                secure=True,
            )

            _ = student.post(
                "/classes",
                {
                    "connectedclass": connectedclass.id,
                    "classcode": teacherclasscode,
                    "formid": "promoteclass",
                },
                secure=True,
            )

            self.assertTrue(models.Enrollment.objects.last().teacher)

    @load_fixture("class_light.json")
    def test_updateclass(self):
        classinfo = f"Updated Info {rand_id()}"
        maxgen = rand_id()
        viewable_ptas = ["MILK", "PROT", "FAT"]

        _ = self.teacher.post(
            "/classes",
            {
                "connectedclass": 1,
                "classinfo": classinfo,
                "maxgen": maxgen,
                "formid": "updateclass",
            }
            | {f"trait-{pta.upper()}": True for pta in viewable_ptas},
            secure=True,
        )

        connectedclass = models.Class.objects.first()
        self.assertEquals(connectedclass.info, classinfo)
        self.assertEquals(connectedclass.breeding_limit, maxgen)

        for key, val in connectedclass.viewable_traits.items():
            self.assertEquals(val, key in viewable_ptas)


class TestFileRequests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username="client", password="password")
        self.client.login(username="client", password="password")

    @load_fixture("class.json")
    def test_get_herd_file(self):
        response = self.client.get(f"/herd-file/2", secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("attachment; filename=" in response.get("Content-Disposition"))

    @load_fixture("class.json")
    def test_get_class_tendchart(self):
        response = self.client.get(f"/classtrend-file/1")
        self.assertEquals(response.status_code, 200)
        self.assertTrue("attachment; filename=" in response.get("Content-Disposition"))


class TestHerdActions(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username="client", password="password")
        self.client.login(username="client", password="password")

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
