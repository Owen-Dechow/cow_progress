from django.test import TestCase
from base import models
from .utils import load_fixture, rand_id, create_authenticated_client


class TestClassSystem(TestCase):
    def setUp(self):
        # Create teacher
        self.teacher = create_authenticated_client("teacher")

        # Create students
        self.students = [
            create_authenticated_client(f"student-{idx}") for idx in range(3)
        ]

    def test_addclass(self):
        _ = self.teacher.post(
            "/classes",
            {
                "classname": f"Test Class {rand_id()}",
                "info": f"Test Class Info {rand_id()}",
                "formid": "addclass",
                "traitset": "NM_2021",
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
