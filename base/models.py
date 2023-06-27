from django.contrib.auth.models import User
from .traitinfo import correlations as cor
from .traitinfo import recessives
from random import randrange, random, randint
from .traitinfo import traits
from django.db import models
from math import prod
from .inbreeding import InbreedingCalculator
from datetime import datetime

PTA_DECIMALS = 3  # Number of decimal placements shown for PTAs on website/ xlsx files
MUTATION_RATE = 0.25  # Maximum mutation of a PTA in one generation from -1 to 1 value

ATTRACT_0 = lambda: prod(random() for _ in range(6))
""" Returns a number close to 0 | Mean = 0.5^6 = 0.015625 | Range = [0, 1) """


# Holds a group of animals
class Herd(models.Model):
    __str__ = lambda self: self.name

    # Name of the herd
    name = models.CharField(max_length=255)

    # Owner of the herd
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)

    # Number of breedings that have been run on herd
    breedings = models.IntegerField(default=0)

    # Stores the class this herd is part of
    connectedclass = models.ForeignKey(
        to="Class",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="_herd_connectedclass",
    )

    # Stores the enrollment used to build herd
    enrollment = models.ForeignKey(
        to="Enrollment",
        related_name="_herd_enrollment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @staticmethod
    def get_auto_generated_herd(name, connectedclass, enrollment=None):
        """Builds a random herd"""

        NUMBER_OF_COWS = 150  # Number of cows generated
        NUMBER_OF_BULLS = 10  # Number of bulls generated

        # Create and initialize herd
        herd = Herd()
        herd.connectedclass = connectedclass
        herd.enrollment = enrollment
        herd.name = name
        herd.save()

        animals = []

        # Create cows
        for _ in range(NUMBER_OF_COWS):
            animals.append(Bovine.auto_generate(herd, False))

        # Create bulls
        for _ in range(NUMBER_OF_BULLS):
            animals.append(Bovine.auto_generate(herd, True))

        Bovine.objects.bulk_create(animals)

        return herd, animals

    @staticmethod
    def make_public_herd(name, animal_name_prefix, star_word, connectedclass):
        """Builds public herds"""

        herd, animals = Herd.get_auto_generated_herd(name, connectedclass)

        do_not_use = set()
        for trait in traits.Trait.get_all():
            top = None
            for animal in animals:
                if animal not in do_not_use:
                    if top is not None:
                        nmd = trait.net_merit_dollars
                        top_val = top.data[trait.name] * nmd
                        animal_val = animal.data[trait.name] * nmd

                    if top is None or animal_val > top_val:
                        top = animal

            top.name = animal_name_prefix + " " + trait.name + " " + star_word
            top.male = True
            do_not_use.add(top)

        for animal in animals:
            if animal not in do_not_use:
                animal.name = animal_name_prefix + " " + str(animal.id)
                animal.pedigree = animal.auto_generate_pedigree()

        Bovine.objects.bulk_update(animals, ["name", "pedigree", "male"])
        return herd

    def get_summary(self):
        """Gets a JSON serializable dict of all PTAs average among animals"""

        summary = {}

        # Get all animals
        animals = Bovine.objects.filter(herd=self)

        # Add animals PTAs together
        for animal in animals:
            for key in animal.scaled:
                if key in summary:
                    summary[key] += animal.scaled[key]
                else:
                    summary[key] = animal.scaled[key]

        # Divide each PTA by number of animals
        number_of_animals = len(animals)
        for key in summary:
            summary[key] = round(summary[key] / number_of_animals, PTA_DECIMALS)

        if self.connectedclass:
            for key, val in self.connectedclass.viewable_traits.items():
                if not val:
                    summary[key] = "~"

        for trait in traits.Trait.get_all() + [traits.Trait("Net Merit", "0", "0")]:
            if trait.name not in summary:
                summary[trait.name] = "~"

        return summary

    def get_herd_dict(self):
        """Gets a JSON serializable dict of all animals in herd"""

        herd = {"cows": {}, "bulls": {}}
        connectedclass = self.connectedclass

        # Add animals to dict
        for animal in Bovine.objects.filter(herd=self):
            sex = "bulls" if animal.male else "cows"
            herd[sex][animal.id] = animal.get_dict(connectedclass)

        return herd

    def run_breeding(self, sires):
        """Breeds the herd to specified bulls"""

        NUMBER_OF_COWS = 100  # Planed number of cows generated
        NUMBER_OF_BULLS = 10  # Planed number of bulls generated
        MAX_GENERATION = 5  # Max age of animal before its culled

        # Update the herd generation
        self.breedings += 1
        self.save()

        # Initialize breeding map
        breedings_Male = []
        breedings_Female = []
        for sire in sires:
            breedings_Male.append({"sire": sire, "cows": []})
            breedings_Female.append({"sire": sire, "cows": []})

        # Get cows in herd
        cows = list(Bovine.objects.filter(herd=self, male=False))

        # Get real number of cows and bulls in generated
        n_cows = NUMBER_OF_COWS
        n_bulls = NUMBER_OF_BULLS
        while len(cows) < n_cows + n_bulls:
            if n_cows > 0:
                n_cows -= 1
            if n_bulls > 0:
                n_bulls -= 1

        # Get random selection of cows to be breed
        used_cows = []
        for _ in range(n_cows + n_bulls):
            cowIDX = randrange(0, len(cows))
            used_cows.append(cows[cowIDX])
            cows.pop(cowIDX)

        # Map breedings for bulls
        for _ in range(n_bulls):
            cow = used_cows.pop()
            breedings_Male[randrange(0, len(breedings_Male))]["cows"].append(cow)

        # Map breedings for cows
        for _ in range(n_cows):
            cow = used_cows.pop()
            breedings_Female[randrange(0, len(breedings_Male))]["cows"].append(cow)

        # Generate new bulls
        animals = []
        for breeding in breedings_Male:
            for dam in breeding["cows"]:
                animals.append(
                    Bovine.create_from_breeding(breeding["sire"], dam, self, True)
                )

        # Generate new cows
        for breeding in breedings_Female:
            for dam in breeding["cows"]:
                animals.append(
                    Bovine.create_from_breeding(breeding["sire"], dam, self, False)
                )

        Bovine.objects.bulk_create(animals)
        for animal in animals:
            animal.name = animal.auto_generate_name(self)
            animal.pedigree = animal.auto_generate_pedigree()

            # Calculate inbreeding
            if animal.sire and animal.dam:
                calculator = InbreedingCalculator(animal.get_pedigree_dict())
                animal.inbreeding = calculator.get_coefficient()
            else:
                animal.inbreeding = 0

        Bovine.objects.bulk_update(animals, ["name", "pedigree", "inbreeding"])

        # Remove any animals over the max age
        animals = Bovine.objects.filter(herd=self)
        kill_list = []
        for bovine in animals:
            if self.breedings - bovine.generation > MAX_GENERATION:
                kill_list.append(bovine)
                bovine.herd = None

        Bovine.objects.bulk_update(kill_list, ["herd"])

        # Remove any animals dead from recessives
        return self.remove_deaths_from_recessives()

    def remove_deaths_from_recessives(self):
        recessives_list = recessives.get_recessives_fatal()
        number_of_deaths = 0
        animals = Bovine.objects.filter(herd=self)

        kill_list = []
        for bovine in animals:
            for recessive in recessives_list:
                if bovine.recessives[recessive[0]] == 2 and recessive[1]:
                    if bovine not in kill_list:
                        number_of_deaths += 1
                        kill_list.append(bovine)
                        bovine.herd = None

        Bovine.objects.bulk_update(kill_list, ["herd"])

        return number_of_deaths


# Holds the PTAs on single animal
class Bovine(models.Model):
    __str__ = lambda self: self.name

    # Stores the name of the animal
    name = models.CharField(max_length=255, null=True)

    # Stores the herd animal belongs to
    herd = models.ForeignKey(to=Herd, on_delete=models.SET_NULL, null=True)

    # Stores the generation the animal was born in
    generation = models.IntegerField(default=0)

    # True = Male, False = Female
    male = models.BooleanField(null=True)

    data = models.JSONField(default=dict)  # Stores the unscaled data -1 to 1 form
    scaled = models.JSONField(default=dict)  # Stores the front end scaled PTA data
    recessives = models.JSONField(default=dict)  # Recessive information

    connectedclass = models.ForeignKey(to="Class", on_delete=models.CASCADE)

    dam = models.ForeignKey(
        to="Bovine", related_name="_dam", on_delete=models.SET_NULL, null=True
    )
    sire = models.ForeignKey(
        to="Bovine", related_name="_sire", on_delete=models.SET_NULL, null=True
    )
    pedigree = models.JSONField(null=True)
    inbreeding = models.FloatField(null=True)

    @staticmethod
    def create_from_breeding(sire, dam, herd, male):
        """Takes in two animals and creates a child List from the data"""

        # Create and initialize new animal
        new = Bovine()

        new.herd = herd
        new.male = male
        new.sire = sire
        new.dam = dam
        new.generation = herd.breedings
        new.connectedclass = herd.connectedclass

        # Generate mutated uncorrelated values -1 to 1
        uncorrelated = {}
        for trait in traits.Trait.get_all():
            val = (sire.data[trait.name] + dam.data[trait.name]) / 2
            newval = val + MUTATION_RATE * traits.DOMAIN()

            # Ensure new value is in range -1 to 1
            if abs(newval) > 1:
                newval = (abs(newval) / newval) * (1 + ATTRACT_0())

            uncorrelated[trait.name] = newval

        # Correlate data
        initial_val_list = [uncorrelated[key.name] for key in traits.Trait.get_all()]
        corelated_data = cor.get_result(initial_values=initial_val_list)
        new.data = cor.convert_data(corelated_data)

        # Scale data for front end
        new.set_scaled_data()

        # Set the genetic recessives for new animal
        for recessive in recessives.get_recessives():
            new.recessives[recessive] = recessives.get_result_of_two(
                sire.recessives[recessive], dam.recessives[recessive]
            )

        return new

    def get_pedigree_dict(self):
        """Get a JSON serializable pedagree"""

        return self.pedigree

    @staticmethod
    def auto_generate(herd, male):
        """Auto generates the data for an animal"""

        # Create and initialize new animal
        new = Bovine()

        new.herd = herd
        new.male = male
        new.connectedclass = herd.connectedclass
        new.inbreeding = 0

        # Get data -1 to 1
        correlated_data = cor.get_result()
        new.data = cor.convert_data(correlated_data)

        # Scale the data
        new.set_scaled_data()

        # Set the genetic recessives for new animal
        new.recessives = {}
        for recessive in recessives.get_recessives():
            new.recessives[recessive] = randint(0, randint(0, 1))

        return new

    def set_scaled_data(self):
        """Scales the data field into the scaled field"""

        scaled_data = {}
        for key, val in self.data.items():
            standard_deviation = traits.Trait.get(key).standard_deviation
            scaled_data[key] = round(standard_deviation * val, PTA_DECIMALS)

        self.scaled = scaled_data
        self.set_net_merit()

    def get_dict(self, connectedclass=None):
        """Returns a JSON serializable summary of animal"""

        if not connectedclass:
            connectedclass = self.herd.connectedclass

        scaled = dict(self.scaled)
        for key, val in connectedclass.viewable_traits.items():
            if not val:
                scaled[key] = "~"

        return {
            "name": self.name,
            "Generation": self.generation,
            "Sire": self.sire_id if self.sire_id else "~",
            "Dam": self.dam_id if self.dam_id else "~",
            "Inbreeding Coefficient": self.inbreeding,
            "traits": scaled,
            "recessives": self.recessives,
        }

    def set_net_merit(self):
        self.scaled = {
            "Net Merit": round(
                traits.Trait.calculate_net_merit(self.scaled), PTA_DECIMALS
            )
        } | self.scaled

    def auto_generate_name(self, herd):
        """Autogenerates a name for animal"""

        if herd.name[-1] == "s":
            return herd.name + f"' {self.id}"
        else:
            return herd.name + f"'s {self.id}"

    def auto_generate_pedigree(self):
        pedigree = {"id": self.id}
        if self.sire_id:
            pedigree["sire"] = self.sire.pedigree
        if self.dam_id:
            pedigree["dam"] = self.dam.pedigree

        return pedigree


# Class object
class Class(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255)  # Holds the name of the class
    info = models.TextField(
        blank=True, null=True, max_length=1024
    )  # Holds the class info
    classcode = models.CharField(
        unique=True, max_length=255
    )  # Holds the student enrollment code
    teacherclasscode = models.CharField(
        unique=True, max_length=255
    )  # Holds the teacher enrollment code

    # Holds the traits that the students can see
    viewable_traits = models.JSONField()

    # Maximun number of breedings allowed on a class herd
    breeding_limit = models.IntegerField(default=0)

    # Holds the population average after each breeding
    trend_log = models.JSONField(default=dict)

    # Connects the owner of the class
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="classowner"
    )

    # Connects a class herd
    herd = models.OneToOneField(
        to=Herd, on_delete=models.CASCADE, related_name="classherd", null=True
    )

    # Connects a class to public herd
    publicherd = models.OneToOneField(
        to=Herd, on_delete=models.CASCADE, related_name="classpublicherd", null=True
    )

    def update_trend_log(self, entry_name: str):
        summary = {}
        animal_count = 0

        herds = Herd.objects.filter(connectedclass=self)
        for herd in herds:
            for animal in Bovine.objects.filter(herd=herd):
                animal_count += 1
                for key, value in animal.scaled.items():
                    if key not in summary:
                        summary[key] = value
                    else:
                        summary[key] += value

                for key, value in animal.data.items():
                    if "_" + key not in summary:
                        summary["_" + key] = value
                    else:
                        summary["_" + key] += value

        for key, value in summary.items():
            summary[key] = round(summary[key] / animal_count, PTA_DECIMALS)

        self.trend_log[entry_name] = {
            "Timestamp": str(datetime.now()),
            "Population Size": animal_count,
        } | summary
        self.save()

    @staticmethod
    def get_class_code():
        """Autogenerates a class code"""

        CODE_SECTIONS = 3
        CHAR_PER_SECTIONS = 3
        ALLOWEDCHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        code = ""
        for i in range(CODE_SECTIONS):
            for _ in range(CHAR_PER_SECTIONS):
                code += ALLOWEDCHAR[randrange(len(ALLOWEDCHAR))]
            if i != CODE_SECTIONS - 1:
                code += "-"

        try:
            try:
                Class.objects.get(classcode=code)
            except:
                Class.objects.get(teacherclasscode=code)
                return Class.get_class_code()
        except:
            return code

    @staticmethod
    def get_from_code(code):
        """Gets the class from classcode and returns it in a tuple with the a boolean
        telling if a teacher class code was used"""

        try:
            _class = Class.objects.get(classcode=code)
            teacher = False
        except:
            _class = Class.objects.get(teacherclasscode=code)
            teacher = True

        return _class, teacher

    class Meta:
        verbose_name_plural = "Classes"


# Connects users to classes
class Enrollment(models.Model):
    __str__ = lambda self: self.user.username + " in " + self.connectedclass.name

    # Connects the student or teacher
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="_enrollmentuser"
    )

    # Connects the class
    connectedclass = models.ForeignKey(
        to=Class, on_delete=models.CASCADE, related_name="_enrollmentclass"
    )

    # Tells if user is a teacher (true) of student (false)
    teacher = models.BooleanField(default=False)

    def save(self, *args, **kwargs) -> None:
        """Saves the enrollment and calls the scrub method"""

        super().save(*args, **kwargs)
        Enrollment.scrub_enrollment(self.user, self.connectedclass)

    @staticmethod
    def scrub_enrollment(user, connectedclass):
        """Deletes any duplicate enrollments"""

        enrollments = list(
            Enrollment.objects.filter(user=user, connectedclass=connectedclass)
        )

        while len(enrollments) > 1:
            e = enrollments.pop()
            e.delete()
