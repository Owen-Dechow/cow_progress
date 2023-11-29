from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from random import randrange
from .inbreeding import InbreedingCalculator
from .traitinfo.traitsets import TraitSet, TRAITSET_CHOICES, Trait, DOMAIN

PTA_DECIMALS = 3  # Number of decimal placements shown for PTAs on website/ xlsx files


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
        for trait in TraitSet(connectedclass.traitset).traits:
            top = None
            for animal in animals:
                if animal not in do_not_use:
                    if top is not None:
                        nmd = trait.net_merit_dollars
                        top_val = top.genotype[trait.name] * nmd
                        animal_val = animal.genotype[trait.name] * nmd

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
            for key in animal.genotype:
                if self.connectedclass.viewable_traits[key]:
                    if key in summary:
                        summary[key] += animal.genotype[key]
                    else:
                        summary[key] = animal.genotype[key]
                else:
                    continue

        for animal in animals:
            for key in animal.phenotype:
                if self.connectedclass.viewable_traits[key]:
                    if f"ph: {key}" in summary:
                        summary[f"ph: {key}"] += animal.phenotype[key]
                    else:
                        summary[f"ph: {key}"] = animal.phenotype[key]
                else:
                    continue

        # Divide each PTA by number of animals
        number_of_animals = len(animals)
        for key in summary:
            summary[key] = round(summary[key] / number_of_animals, PTA_DECIMALS)

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

        # Update name and pedigree after getting id
        Bovine.objects.bulk_create(animals)
        for animal in animals:
            animal.name = animal.auto_generate_name(self)
            animal.pedigree["id"] = animal.id

        Bovine.objects.bulk_update(animals, ["name", "pedigree", "inbreeding"])

        # Cull any animals of their max age
        self.remove_animals_over_max_age()

        # Remove any animals dead from recessives
        return self.remove_deaths_from_recessives()

    def remove_deaths_from_recessives(self):
        traitset = TraitSet(self.connectedclass.traitset)
        number_of_deaths = 0
        animals = Bovine.objects.filter(herd=self)

        kill_list = []
        for bovine in animals:
            for recessive in traitset.recessives:
                if bovine.recessives[recessive.name] == 2 and recessive.fatal:
                    if bovine not in kill_list:
                        number_of_deaths += 1
                        kill_list.append(bovine)
                        bovine.herd = None

        Bovine.objects.bulk_update(kill_list, ["herd"])

        return number_of_deaths

    def remove_animals_over_max_age(self):
        MAX_GEN = 5

        traitset = TraitSet(self.connectedclass.traitset)
        animals = Bovine.objects.filter(herd=self)
        kill_list = []

        for animal in animals:
            age = self.breedings - animal.generation

            if animal.male == False and traitset.DPR_for_max_gen:
                dpr = (
                    animal.phenotype[traitset.DPR_for_max_gen.name]
                    / 2
                    / traitset.DPR_for_max_gen.standard_deviation
                )
                half_max_gen = (MAX_GEN - 1) / 2
                max_age = round(half_max_gen * dpr + half_max_gen + 0.1) + 1
            else:
                max_age = MAX_GEN

            if age > max_age:
                if max_age != MAX_GEN:
                    print(max_age, dpr)

                kill_list.append(animal)
                animal.herd = None

        Bovine.objects.bulk_update(kill_list, ["herd"])


# Information on single animal
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

    genotype = models.JSONField(default=dict)  # Stores the scaled genotype
    phenotype = models.JSONField(default=dict, null=True)  # Stores the scaled phenotype

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
        """Takes in two animals and creates a child List from the genotype"""

        # Create and initialize new animal
        new = Bovine()

        new.herd = herd
        new.male = male
        new.sire = sire
        new.dam = dam
        new.generation = herd.breedings
        new.connectedclass = herd.connectedclass

        # Get Traitset
        traitset = TraitSet(herd.connectedclass.traitset)

        # Generate mutated uncorrelated values
        uncorrelated = {}
        for trait in traitset.traits:
            uncorrelated[trait.name] = trait.PTA_mutation(
                sire.genotype[trait.name], dam.genotype[trait.name]
            )

        # Correlate data
        correlated_data = traitset.get_correlated_values(uncorrelated)
        new.genotype = {key.name: val for key, val in correlated_data.items()}

        # Scale genotype for front end
        new.pedigree = new.auto_generate_pedigree()
        new.get_inbreeding()
        new.set_phenotypes()
        new.set_net_merit()

        # Set the genetic recessives for new animal
        for recessive in traitset.recessives:
            new.recessives[
                recessive.name
            ] = traitset.get_result_of_two_recessive_int_vals(
                sire.recessives[recessive.name], dam.recessives[recessive.name]
            )

        return new

    @staticmethod
    def auto_generate(herd, male):
        """Auto generates the data for an animal"""

        # Create and initialize new animal
        new = Bovine()

        new.herd = herd
        new.male = male
        new.connectedclass = herd.connectedclass
        new.inbreeding = 0

        # Get traitset
        traitset = TraitSet(herd.connectedclass.traitset)

        uncorrelated_values = {
            x.name: x.get_point_on_mendelian_sample() for x in traitset.traits
        }
        correlated_data = traitset.get_correlated_values(uncorrelated_values)
        new.genotype = {
            key.name: round(val, PTA_DECIMALS) for key, val in correlated_data.items()
        }

        new.set_phenotypes()
        new.set_net_merit()

        # Set the genetic recessives for new animal
        new.recessives = {}
        for recessive in traitset.recessives:
            new.recessives[recessive.name] = recessive.get_carrier_int_from_prominence()

        return new

    def set_phenotypes(self):
        """Scales the phenotypes of animal"""

        # Get traitset
        traitset = TraitSet(self.connectedclass.traitset)

        uncorrelated_ph = {}
        for trait in traitset.traits:
            uncorrelated_ph[trait.name] = trait.PTA_to_phenotype(
                self.genotype[trait.name]
            )

        correlated_phenotype = traitset.get_correlated_values(uncorrelated_ph, True)
        self.phenotype = {
            key.name: round(val, PTA_DECIMALS)
            for key, val in correlated_phenotype.items()
        }

    def get_dict(self, connectedclass=None):
        """Returns a JSON serializable summary of animal"""

        if not connectedclass:
            connectedclass = self.herd.connectedclass

        traits = dict(self.genotype)
        for key, val in self.phenotype.items():
            traits[f"ph: {key}"] = val

        for key, val in connectedclass.viewable_traits.items():
            if not val:
                if key in traits:
                    del traits[key]
                if f"ph: {key}" in traits:
                    del traits[f"ph: {key}"]

        recessives = dict(self.recessives)
        for key, val in connectedclass.viewable_recessives.items():
            if not val:
                del recessives[key]

        return {
            "name": self.name,
            "Generation": self.generation,
            "Sire": self.sire_id if self.sire_id else "~",
            "Dam": self.dam_id if self.dam_id else "~",
            "Inbreeding Coefficient": self.inbreeding,
            "traits": traits,
            "recessives": recessives,
        }

    def set_net_merit(self):
        traitset = TraitSet(self.connectedclass.traitset)

        self.genotype = {
            "Net Merit": round(
                traitset.calculate_net_merit(self.genotype),
                PTA_DECIMALS,
            )
        } | self.genotype

    def auto_generate_name(self, herd):
        """Autogenerates a name for animal"""

        if herd.name[-1] == "s":
            return herd.name + f"' {self.id}"
        else:
            return herd.name + f"'s {self.id}"

    def auto_generate_pedigree(self):
        pedigree = {"id": self.id if self.id else -1}
        if self.sire_id:
            pedigree["sire"] = self.sire.pedigree
        if self.dam_id:
            pedigree["dam"] = self.dam.pedigree

        return pedigree

    def get_inbreeding(self):
        # Calculate inbreeding
        if self.sire and self.dam:
            calculator = InbreedingCalculator(self.pedigree)
            self.inbreeding = calculator.get_coefficient()
        else:
            self.inbreeding = 0


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
    viewable_recessives = models.JSONField(null=True)

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

    # Selects the traitset for class
    traitset = models.CharField(
        max_length=20,
        default=TRAITSET_CHOICES[0][0],
        null=True,
    )

    def update_trend_log(self, entry_name: str):
        summary = {}
        animal_count = 0

        herds = Herd.objects.filter(connectedclass=self)
        for herd in herds:
            for animal in Bovine.objects.filter(herd=herd):
                animal_count += 1

                for key, value in animal.genotype.items():
                    if key not in summary:
                        summary[key] = value
                    else:
                        summary[key] += value

                for key, value in animal.phenotype.items():
                    if f"ph: {key}" not in summary:
                        summary[f"ph: {key}"] = value
                    else:
                        summary[f"ph: {key}"] += value

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
