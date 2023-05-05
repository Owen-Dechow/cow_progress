from typing import Iterable, Optional
from django.contrib.auth.models import User
from .traitinfo import correlations as cor
from .traitinfo import recessives
from random import randrange, random, randint
from .traitinfo import traits
from django.db import models
from math import prod

PTA_DECIMALS = 3  # Number of decimal placements shown for PTAs on website/ xlsx files
MUTATION_RATE = 0.25  # Maximum mutation of a PTA in one generation from -1 to 1 value
ATTRACT_0 = lambda: prod(
    random() for _ in range(4)
)  # Returns a number close to 0 | Mean = 0.5^4 = 0.0625, Range = [0, 1)


# List of recourses found on front page
class Resource(models.Model):
    __str__ = lambda self: self.title

    title = models.CharField(
        max_length=255
    )  # The text that will be displayed for resource
    link = models.CharField(max_length=255)  # Url to the resource itself


# Holds the PTAs on single animal
class Bovine(models.Model):
    data = models.JSONField()  # Stores the unscaled data -1 to 1 form
    scaled = models.JSONField()  # Stores the front end scaled PTA data

    # Stores recessives [0 = Homozygous Dominant, 1=Heterozygous, 2=Homozygous Recessive]
    recessives = models.JSONField()

    # Stores the pedigree object for animal
    pedigree = models.ForeignKey(to="Pedigree", on_delete=models.CASCADE)

    #### Refrances either the cow or bull connected to PTA list ####
    connected_bull = models.ForeignKey(
        to="Bull",
        on_delete=models.CASCADE,
        related_name="_connected_bull",
        null=True,
        blank=True,
    )
    connected_cow = models.ForeignKey(
        to="Cow",
        on_delete=models.CASCADE,
        related_name="_connected_cow",
        null=True,
        blank=True,
    )

    @staticmethod
    def get_mutated_average(a, b, bull=None, cow=None):
        """Takes in two TraitsLists and creates a child List from the data"""

        # Create and initialize new List
        new = Bovine()
        new.data = {}
        new.recessives = {}

        # Generate mutated uncorrelated values -1 to 1
        uncorrelated = {}
        for trait in traits.Trait.Get_All():
            val = (a.data[trait.name] + b.data[trait.name]) / 2
            newval = val + MUTATION_RATE * traits.DOMAIN()

            # Ensure new value is in range -1 to 1
            if abs(newval) > 1:
                newval = (abs(newval) / newval) * (1 + ATTRACT_0())

            uncorrelated[trait.name] = newval

        # Correlate data
        initial_val_list = [uncorrelated[key.name] for key in traits.Trait.Get_All()]
        corelated_data = cor.get_result(initial_values=initial_val_list)
        new.data = cor.convert_data(corelated_data)

        # Scale data for front end
        new.set_scaled_data()

        # Set the genetic recessives for new animal
        for recessive in recessives.get_recessives():
            new.recessives[recessive] = recessives.get_result_of_two(
                a.recessives[recessive], b.recessives[recessive]
            )

        # Connect to animal
        if bull:
            bull.save()
            new.connected_bull = bull
        if cow:
            cow.save()
            new.connected_cow = cow

        new.save()
        return new

    def auto_data(self, cow=None, bull=None):
        """Auto generates the data for one TraitsList"""

        # Get data -1 to 1
        correlated_data = cor.get_result()
        self.data = cor.convert_data(correlated_data)

        # Scale the data
        self.set_scaled_data()

        # Set the genetic recessives for new animal
        self.recessives = {}
        for recessive in recessives.get_recessives():
            self.recessives[recessive] = randint(0, randint(0, 2))

        # Connect to animal and save data
        self.save()
        if bull:
            bull.save()
            self.connected_bull = bull
        if cow:
            cow.save()
            self.connected_cow = cow
        self.save()

    def set_scaled_data(self):
        """Scales the data field into the scaled field"""

        scaled_data = {}
        for key, val in self.data.items():
            standard_deviation = traits.Trait.get(key).standard_deviation
            scaled_data[key] = round(standard_deviation * val, PTA_DECIMALS)

        self.scaled = scaled_data

    def __str__(self):
        if self.connected_cow is not None:
            return "Cow: " + str(self.connected_cow.id)
        elif self.connected_bull is not None:
            return "Bull: " + str(self.connected_bull.id)
        else:
            return "NONE"

    def save(self, *args, **kwargs):
        if not hasattr(self, "pedigree"):
            self.pedigree = Pedigree()

        if self.connected_bull:
            male = True
            animal = self.connected_bull
        elif self.connected_cow:
            male = False
            animal = self.connected_cow
        else:
            animal = None

        if animal is not None:
            self.pedigree.animal_id = animal.id
            self.pedigree.male = male
            if animal.sire:
                self.pedigree.sire = animal.sire.traits.pedigree
            if animal.dam:
                self.pedigree.dam = animal.dam.traits.pedigree

        self.pedigree.save()

        super().save(*args, **kwargs)


# Holds a group of animals
class Herd(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255)  # Name of the herd
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, null=True, blank=True
    )  # Owner of the herd
    breedings = models.IntegerField(
        default=0
    )  # Number of breedings that have been run on herd
    unrestricted = models.BooleanField(
        default=False
    )  # Tells if herd can be accessed by anyone

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

        # Create cows
        for _ in range(NUMBER_OF_COWS):
            cow = Cow()

            cow.traits = Bovine()
            cow.traits.auto_data(cow=cow)
            cow.herd = herd
            cow.name = cow.get_name()
            cow.save()

        # Create bulls
        for _ in range(NUMBER_OF_BULLS):
            bull = Bull()

            bull.traits = Bovine()
            bull.traits.auto_data(bull=bull)
            bull.herd = herd
            bull.name = bull.get_name()
            bull.save()

        # Remove any animals dead from recessives
        herd.remove_deaths_from_recessives()

        herd.save()
        return herd

    def get_summary(self):
        """Gets a JSON serializable dict of all PTAs average among animals"""

        summary = {}

        # Get all animals
        cows = [t.traits for t in Cow.objects.filter(herd=self)]
        bulls = [t.traits for t in Bull.objects.filter(herd=self)]
        traitgroups = cows + bulls

        # Add animals PTAs together
        for trait in traitgroups:
            for key in trait.data:
                if key in summary:
                    summary[key] += trait.scaled[key]
                else:
                    summary[key] = trait.scaled[key]

        # Divide each PTA by number of animals
        n = len(traitgroups)
        for key in summary:
            summary[key] = round(summary[key] / n, PTA_DECIMALS)

        return summary

    def get_herd_dict(self):
        """Gets a JSON serializable dict of all animals in herd"""

        herd = {"cows": {}, "bulls": {}}

        # Adds cows to dict
        for cow in Cow.objects.filter(herd=self):
            herd["cows"][cow.id] = {
                "name": cow.name,
                "Generation": cow.generation,
                "Sire": cow.traits.pedigree.sire.animal_id
                if cow.traits.pedigree.sire
                else "~",
                "Dam": cow.traits.pedigree.dam.animal_id
                if cow.traits.pedigree.dam
                else "~",
                "traits": cow.traits.scaled,
                "recessives": cow.traits.recessives,
            }

        # Adds bulls to dict
        for bull in Bull.objects.filter(herd=self):
            herd["bulls"][bull.id] = {
                "name": bull.name,
                "Generation": bull.generation,
                "Sire": bull.traits.pedigree.sire.animal_id
                if bull.traits.pedigree.sire
                else "~",
                "Dam": bull.traits.pedigree.dam.animal_id
                if bull.traits.pedigree.dam
                else "~",
                "traits": bull.traits.scaled,
                "recessives": bull.traits.recessives,
            }

        return herd

    def run_breeding(self, sires):
        """Breeds the herd to specified bulls"""

        NUMBER_OF_COWS = 100  # Planed number of cows generated
        NUMBER_OF_BULLS = 10  # Planed number of bulls generated
        MAX_GENERATION = 5  # Max age of animal before its removed

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
        cows = list(Cow.objects.filter(herd=self))

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
        for breeding in breedings_Male:
            for dam in breeding["cows"]:
                Bull.from_breeding(breeding["sire"], dam, self)

        # Generate new cows
        for breeding in breedings_Female:
            for dam in breeding["cows"]:
                Cow.from_breeding(breeding["sire"], dam, self)

        #### Remove any animals over the max age ####
        for cow in Cow.objects.filter(herd=self):
            if self.breedings - cow.generation > MAX_GENERATION:
                cow.delete()
        for bull in Bull.objects.filter(herd=self):
            if self.breedings - bull.generation > MAX_GENERATION:
                bull.delete()

        # Remove any animals dead from recessives
        return self.remove_deaths_from_recessives()

    def remove_deaths_from_recessives(self):
        recessives_list = recessives.get_recessives_fatal()
        deaths = 0

        for cow in Cow.objects.filter(herd=self):
            for recessive in recessives_list:
                if cow.traits.recessives[recessive[0]] == 2 and recessive[1]:
                    if cow.id:
                        deaths += 1
                        cow.delete()

        for bull in Bull.objects.filter(herd=self):
            for recessive in recessives_list:
                if bull.traits.recessives[recessive[0]] == 2 and recessive[1]:
                    if bull.id:
                        deaths += 1
                        bull.delete()

        return deaths


# Single female animal
class Cow(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255)  # Holds the name of the cow
    herd = models.ForeignKey(
        to=Herd, on_delete=models.CASCADE, null=True
    )  # Holds the herd the cow is part of
    generation = models.IntegerField(
        default=0
    )  # Holds the generation the cow was born in

    # Connects a trait list to cow
    traits = models.OneToOneField(
        to=Bovine,
        on_delete=models.SET_NULL,
        related_name="Cull_traits_TraitsList",
        null=True,
    )

    # Connects dam to cow
    dam = models.ForeignKey(
        to="Cow", on_delete=models.SET_NULL, null=True, default=None
    )

    # Connects sire to cow
    sire = models.ForeignKey(
        to="Bull", on_delete=models.SET_NULL, null=True, default=None
    )

    def get_name(self):
        """Autogenerates a name for cow"""

        return f"X{self.id} G{self.generation}"

    def get_sexed_id(self):
        """Gets the int id of cow with the 'f' prefix"""

        return "f" + str(self.id)

    @staticmethod
    def from_breeding(sire, dam, herd):
        """Creates a cow from a breeding"""

        cow = Cow()
        cow.traits = Bovine.get_mutated_average(sire.traits, dam.traits, cow=cow)
        cow.generation = herd.breedings
        cow.herd = herd
        cow.name = cow.get_name()
        cow.sire = sire
        cow.dam = dam

        cow.save()
        cow.traits.save()


# Single male animal
class Bull(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255)  # Holds the name of the bull
    herd = models.ForeignKey(
        to=Herd, on_delete=models.CASCADE, null=True
    )  # Holds the herd the bull is part of
    generation = models.IntegerField(
        default=0
    )  # Holds the generation the bull was born in

    # Connects a trait list to bull
    traits = models.OneToOneField(
        to=Bovine,
        on_delete=models.SET_NULL,
        related_name="Bull_traits_TraitsList",
        null=True,
    )

    # Connects dam to bull
    dam = models.ForeignKey(
        to="Cow", on_delete=models.SET_NULL, null=True, default=None
    )

    # Connects sire to bull
    sire = models.ForeignKey(
        to="Bull", on_delete=models.SET_NULL, null=True, default=None
    )

    def get_name(self):
        """Autogenerates a name for bull"""

        return f"Y{self.id} G{self.generation}"

    def get_sexed_id(self):
        """Gets the int id of cow with the 'm' prefix"""

        return "m" + str(self.id)

    @staticmethod
    def from_breeding(sire, dam, herd):
        """Creates a bull from a breeding"""

        bull = Bull()
        bull.traits = Bovine.get_mutated_average(sire.traits, dam.traits, bull=bull)
        bull.generation = herd.breedings
        bull.herd = herd
        bull.name = bull.get_name()
        bull.sire = sire
        bull.dam = dam

        bull.save()
        bull.traits.save()


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

    # Connects the owner of the class
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="classowner"
    )

    # Connects a class herd
    herd = models.OneToOneField(
        to=Herd, on_delete=models.CASCADE, related_name="classherd"
    )

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
        """Deletes any douplicate enrollments"""

        enrollments = list(
            Enrollment.objects.filter(user=user, connectedclass=connectedclass)
        )

        while len(enrollments) > 1:
            e = enrollments.pop()
            e.delete()


class Pedigree(models.Model):
    animal_id = models.CharField(max_length=255, null=True)
    male = models.BooleanField(null=True)
    dam = models.ForeignKey(
        to="Pedigree", related_name="_dam", on_delete=models.CASCADE, null=True
    )
    sire = models.ForeignKey(
        to="Pedigree", related_name="_sire", on_delete=models.CASCADE, null=True
    )
