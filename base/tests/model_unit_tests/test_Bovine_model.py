from django.test import TestCase
from base import models
from ..utils import load_fixture, create_authenticated_client, INFO


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

        self.assertEquals(male.herd, herd)
        self.assertEquals(male.sire, sire)
        self.assertEquals(male.dam, dam)
        self.assertEquals(male.pedigree, INFO.BRED_PEDIGREE)
        self.assertEquals(male.generation, herd.breedings)
        self.assertEquals(male.connectedclass, herd.connectedclass)
        self.assertNotEquals(male.inbreeding, None)

    @load_fixture("class_no_cows.json")
    def test_auto_generate(self):
        herd = models.Herd.objects.get(id=INFO.PUBLIC_HERD_ID)

        male = models.Bovine.auto_generate(herd, True)
        female = models.Bovine.auto_generate(herd, False)

        self.assertTrue(male)

        self.assertTrue(male.male)
        self.assertFalse(female.male)

        self.assertEquals(male.herd, herd)
        self.assertEquals(male.sire, None)
        self.assertEquals(male.dam, None)
        self.assertEquals(male.pedigree, None)
        self.assertEquals(male.generation, 0)
        self.assertEquals(male.connectedclass, herd.connectedclass)
        self.assertEquals(male.inbreeding, 0)

    @load_fixture("class.json")
    def test_set_phenotypes(self):
        animal = models.Bovine.objects.select_related("connectedclass").get(
            id=INFO.PUBLIC_F_ID
        )
        initial = animal.phenotype

        animal.set_phenotypes()

        self.assertNotEquals(animal.phenotype, initial)

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

        self.assertIn("Net Merit", animal.genotype)
        self.assertNotEquals(animal.genotype["Net Merit"], 0)

    @load_fixture("class.json")
    def test_auto_generate_name(self):
        animal = models.Bovine.objects.select_related("herd").get(id=INFO.PUBLIC_F_ID)
        herd = animal.herd

        name = animal.auto_generate_name(herd)
        self.assertEquals(name, INFO.BOVINE_1_NAME)

    @load_fixture("class_personal_herd.json")
    def test_auto_generate_pedigree(self):
        dam = models.Bovine.objects.get(id=INFO.PUBLIC_F_ID)
        sire = models.Bovine.objects.get(id=INFO.PUBLIC_M_ID)
        herd = models.Herd.objects.get(id=INFO.PERSONAL_HERD_ID)
        animal = models.Bovine.create_from_breeding(sire, dam, herd, True)

        self.assertEquals(animal.pedigree, INFO.BRED_PEDIGREE)

    @load_fixture("class_bred_herd.json")
    def test_get_inbreeding(self):
        animal1 = models.Bovine.objects.get(id=INFO.BRED_F_ID)
        animal1.get_inbreeding()

        animal2 = models.Bovine.objects.get(id=INFO.BRED_F_ID + 1)
        animal2.pedigree = INFO.INBRED_PEDIGREE
        animal2.get_inbreeding()

        self.assertEquals(animal1.inbreeding, 0)
        self.assertEquals(animal2.inbreeding, INFO.INBRED_PEDIGREE_COEFFICIENT)
