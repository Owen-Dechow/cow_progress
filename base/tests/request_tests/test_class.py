from django.test import TestCase
from base import models
from ..utils import load_fixture, rand_id, create_authenticated_client, INFO


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
            "/class/new/",
            {
                "classname": f"Test Class {rand_id()}",
                "info": f"Test Class Info {rand_id()}",
                "traitset": "NM_2021",
            },
            secure=True,
        )

        self.assertEqual(models.Class.objects.count(), 1)

    @load_fixture("class_no_cows.json")
    def test_joinclass(self):
        classcode = models.Class.objects.first().classcode

        for student in self.students:
            _ = student.post(
                f"/class/join/",
                {
                    "connectedclass": classcode,
                },
                secure=True,
            )

        self.assertEqual(models.Enrollment.objects.count(), len(self.students) + 1)

    @load_fixture("class_no_cows.json")
    def test_exitclass(self):
        connectedclass = models.Class.objects.first()
        for student in self.students:
            models.Enrollment(
                connectedclass=connectedclass, user=student.user, teacher=False
            ).save()

        for student in self.students:
            _ = student.post(
                f"/class/{INFO.CLASS_ID}/exit/",
                {},
                secure=True,
            )

        self.assertEqual(models.Enrollment.objects.count(), 1)

    @load_fixture("class_no_cows.json")
    def test_deleteclass(self):
        self.teacher.post(
            f"/class/{INFO.CLASS_ID}/delete/",
            {},
            secure=True,
        )

        self.assertEqual(models.Class.objects.count(), 0)

    @load_fixture("class_no_cows.json")
    def test_premoteclass(self):
        connectedclass = models.Class.objects.first()
        teacherclasscode = connectedclass.teacherclasscode
        student = self.students[0]
        models.Enrollment(
            connectedclass=connectedclass, user=student.user, teacher=False
        ).save()

        _ = student.post(
            f"/class/{INFO.CLASS_ID}/promote/",
            {
                "classcode": teacherclasscode,
            },
            secure=True,
        )

        self.assertTrue(models.Enrollment.objects.get(user=student.user).teacher)

    @load_fixture("class_no_cows.json")
    def test_updateclass(self):
        classinfo = f"Updated Info {rand_id()}"
        maxgen = rand_id()
        viewable_ptas = ["MILK", "PROT", "FAT"]

        _ = self.teacher.post(
            f"/class/{INFO.CLASS_ID}/update/",
            {
                "classinfo": classinfo,
                "maxgen": maxgen,
            }
            | {f"trait-{pta.upper()}": True for pta in viewable_ptas},
            secure=True,
        )

        connectedclass = models.Class.objects.first()
        self.assertEqual(connectedclass.info, classinfo)
        self.assertEqual(connectedclass.breeding_limit, maxgen)

        for key, val in connectedclass.viewable_traits.items():
            self.assertEqual(val, key in viewable_ptas)
