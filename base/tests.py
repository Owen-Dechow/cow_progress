from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from base import models
from random import random


# Create your tests here.
class TestClassSystem(TransactionTestCase):
    disable_db_flush = True

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

    # def test_1_addclass(self):
    #     response = self.teacher.post(
    #         "/classes",
    #         {
    #             "connectedclass": "test class name",
    #             "info": "test class info",
    #             "formid": "addclass",
    #         },
    #         secure=True,
    #     )

    #     self.assertTemplateUsed(response, "base/classes.html")

    # def test_2_joinclass(self):
    #     self.teacher.post(
    #         "/classes",
    #         {
    #             "connectedclass": "test class name",
    #             "info": "test class info",
    #             "formid": "addclass",
    #         },
    #         secure=True,
    #     )

    #     classcode = models.Class.objects.first().classcode

    #     for student in self.students:
    #         response = student.post(
    #             "/classes",
    #             {
    #                 "connectedclass": classcode,
    #                 "formid": "joinclass",
    #             },
    #         )

    #         self.assertEquals(response.status_code, 200)
    #         self.assertTemplateUsed("base/classes.html")

    #     self.assertEquals(models.Enrollment.objects.count(), len(self.students) + 1)

    # def test_3_exitclass(self):
    #     self.teacher.post(
    #         "/classes",
    #         {
    #             "connectedclass": "test class name",
    #             "info": "test class info",
    #             "formid": "addclass",
    #         },
    #         secure=True,
    #     )

    #     connectedclass = models.Class.objects.first()
    #     classcode = connectedclass.classcode

    #     for student in self.students:
    #         _ = student.post(
    #             "/classes",
    #             {
    #                 "connectedclass": classcode,
    #                 "formid": "joinclass",
    #             },
    #         )

    #         response = student.post(
    #             "/classes",
    #             {
    #                 "connectedclass": connectedclass.id,
    #                 "formid": "exitclass",
    #             },
    #         )

    #         self.assertEquals(response.status_code, 200)
    #         self.assertTemplateUsed("base/classes.html")

    #     self.assertEquals(models.Enrollment.objects.count(), 1)

    # def test_4_deleteclass(self):
    #     self.teacher.post(
    #         "/classes",
    #         {
    #             "connectedclass": "test class name",
    #             "info": "test class info",
    #             "formid": "addclass",
    #         },
    #         secure=True,
    #     )

    #     self.teacher.post(
    #         "/classes",
    #         {
    #             "connectedclass": 1,
    #             "formid": "deleteclass",
    #         },
    #         secure=True,
    #     )

    #     self.assertTemplateUsed("base/classes.html")
    #     self.assertEquals(models.Class.objects.count(), 0)

    def test_3_premoteclass(self):
        self.teacher.post(
            "/classes",
            {
                "connectedclass": "test class name",
                "info": "test class info",
                "formid": "addclass",
            },
            secure=True,
        )

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
            )

            response = student.post(
                "/classes",
                {
                    "connectedclass": connectedclass.id,
                    "classcode": teacherclasscode,
                    "formid": "premoteclass",
                },
            )

            self.assertTrue(models.Enrollment.objects.last().teacher)
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed("base/classes.html")

        self.assertEquals(models.Enrollment.objects.count(), 1)
