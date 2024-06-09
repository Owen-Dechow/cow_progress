from django.test import TestCase
from base import models
from ..utils import load_fixture, create_authenticated_client, INFO
from base.models import NET_MERIT_KEY


class TestBovineModel(TestCase):
    def setUp(self):
        # Create teacher
        self.teacher = create_authenticated_client("teacher")

        # Create students
        self.students = [
            create_authenticated_client(f"student-{idx}") for idx in range(3)
        ]

    @load_fixture("class_personal_herd.json")
    def test_create_from_breeding(self):
        dam = models.Bovine.objects.get(id=INFO.PUBLIC_F_ID)
        sire = models.Bovine.objects.get(id=INFO.PUBLIC_M_ID)
        herd = models.Herd.objects.get(id=INFO.PERSONAL_HERD_ID)

        male = models.Bovine.create_from_breeding(sire, dam, herd, True)
        female = models.Bovine.create_from_breeding(sire, dam, herd, False)

        self.assertTrue(male)

        self.assertTrue(male.male)
        self.assertFalse(female.male)

        self.assertEqual(male.herd, herd)
        self.assertEqual(male.sire, sire)
        self.assertEqual(male.dam, dam)
        self.assertEqual(male.pedigree, INFO.BRED_PEDIGREE)
        self.assertEqual(male.generation, herd.breedings)
        self.assertEqual(male.connectedclass, herd.connectedclass)
        self.assertNotEqual(male.inbreeding, None)

    @load_fixture("class_no_cows.json")
    def test_auto_generate(self):
        herd = models.Herd.objects.get(id=INFO.PUBLIC_HERD_ID)

        male = models.Bovine.auto_generate(herd, True)
        female = models.Bovine.auto_generate(herd, False)

        self.assertTrue(male)

        self.assertTrue(male.male)
        self.assertFalse(female.male)

        self.assertEqual(male.herd, herd)
        self.assertEqual(male.sire, None)
        self.assertEqual(male.dam, None)
        self.assertEqual(male.pedigree, None)
        self.assertEqual(male.generation, 0)
        self.assertEqual(male.connectedclass, herd.connectedclass)
        self.assertEqual(male.inbreeding, 0)

    @load_fixture("class.json")
    def test_set_phenotypes(self):
        animal = models.Bovine.objects.select_related("connectedclass").get(
            id=INFO.PUBLIC_F_ID
        )
        initial = animal.phenotype

        animal.set_phenotypes()

        self.assertNotEqual(animal.phenotype, initial)

        for trait in INFO.TRAITSET.traits:
            self.assertIn(trait.name, animal.phenotype)

    @load_fixture("class.json")
    def test_get_dict(self):
        connectedclass = models.Class.objects.get(id=INFO.CLASS_ID)
        dicts = (
            models.Bovine.objects.select_related("connectedclass").get(
                id=INFO.PUBLIC_F_ID
            ),
            models.Bovine.objects.select_related("connectedclass").get(
                id=INFO.PUBLIC_F_ID + 1
            ),
        )

        dicts = dicts[0].get_dict(), dicts[1].get_dict(connectedclass)

        for _dict in dicts:
            self.assertIn("name", _dict)
            self.assertIn("Generation", _dict)
            self.assertIn("Sire", _dict)
            self.assertIn("Dam", _dict)
            self.assertIn("Inbreeding Coefficient", _dict)
            self.assertIn("traits", _dict)
            self.assertIn("recessives", _dict)

            for trait, show in connectedclass.viewable_traits.items():
                if not show:
                    continue

                self.assertIn(trait, _dict["traits"])

            for rec, show in connectedclass.viewable_recessives.items():
                if not show:
                    continue

                self.assertIn(rec, _dict["recessives"])

    @load_fixture("class.json")
    def test_set_net_merit(self):
        animal = models.Bovine.objects.get(id=INFO.PUBLIC_F_ID)

        animal.set_net_merit()

        self.assertIn(NET_MERIT_KEY, animal.genotype)
        self.assertNotEqual(animal.genotype[NET_MERIT_KEY], 0)

    @load_fixture("class.json")
    def test_auto_generate_name(self):
        animal = models.Bovine.objects.select_related("herd").get(id=INFO.PUBLIC_F_ID)
        herd = animal.herd

        name = animal.auto_generate_name(herd)
        self.assertEqual(name, INFO.BOVINE_1_NAME)

    @load_fixture("class_personal_herd.json")
    def test_auto_generate_pedigree(self):
        dam = models.Bovine.objects.get(id=INFO.PUBLIC_F_ID)
        sire = models.Bovine.objects.get(id=INFO.PUBLIC_M_ID)
        herd = models.Herd.objects.get(id=INFO.PERSONAL_HERD_ID)
        animal = models.Bovine.create_from_breeding(sire, dam, herd, True)

        self.assertEqual(animal.pedigree, INFO.BRED_PEDIGREE)

    @load_fixture("class_bred_herd.json")
    def test_get_inbreeding(self):
        animal1 = models.Bovine.objects.get(id=INFO.BRED_F_ID)
        animal1.get_inbreeding()

        animal2 = models.Bovine.objects.get(id=INFO.BRED_F_ID + 1)
        animal2.pedigree = INFO.INBRED_PEDIGREE
        animal2.get_inbreeding()

        self.assertEqual(animal1.inbreeding, 0)
        self.assertEqual(animal2.inbreeding, INFO.INBRED_PEDIGREE_COEFFICIENT)
