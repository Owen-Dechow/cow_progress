from django.db import models
from django.contrib.auth.models import User
from random import randrange
from . import correlations as cor

MUTATION_RATE = 0.25
PTA_DECIMALS = 3


class Resource(models.Model):
    __str__ = lambda self: self.title

    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)


class StaticDataClass(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255, unique=True)
    data = models.TextField(max_length=1000, blank=True)

    @staticmethod
    def get_text(title):
        return StaticDataClass.objects.get(name=title).data

    @staticmethod
    def get_number(title):
        return float(StaticDataClass.objects.get(name=title).data)


class Trait(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255)
    average = models.FloatField()
    standard_deviation = models.FloatField()


class Correlation(models.Model):
    __str__ = lambda self: str(self.trait_a) + " to " + str(self.trait_b)

    factor = models.FloatField()
    trait_a = models.ForeignKey(
        to=Trait, on_delete=models.CASCADE, related_name="trait_b"
    )
    trait_b = models.ForeignKey(
        to=Trait, on_delete=models.CASCADE, related_name="trait_a"
    )


class TraitsList(models.Model):
    data = models.JSONField()
    connected_bull = models.ForeignKey(
        to="Bull",
        on_delete=models.CASCADE,
        related_name="_connectedbull",
        null=True,
    )
    connected_cow = models.ForeignKey(
        to="Cow",
        on_delete=models.CASCADE,
        related_name="_connectedcow",
        null=True,
    )

    @staticmethod
    def get_mutated_average(a, b, cor_matrix, bull=None, cow=None):
        new = TraitsList()
        new.data = {}

        correlated_data = cor.get_result(cor_matrix)
        for trait in Trait.objects.all():
            perfect = (a.data[trait.name] + b.data[trait.name]) / 2
            mutated = perfect + (
                correlated_data[trait] * MUTATION_RATE * trait.standard_deviation
            )
            new.data[trait.name] = round(mutated, PTA_DECIMALS)

        if bull:
            bull.save()
            new.connected_bull = bull
        if cow:
            cow.save()
            new.connected_cow = cow

        new.save()
        return new

    def auto_data(self, cor_matrix, cow=None, bull=None):
        self.data = {}

        correlated_data = cor.get_result(cor_matrix)
        for key, val in correlated_data.items():
            self.data[key.name] = round(val * key.standard_deviation, PTA_DECIMALS)
        self.save()

        if bull:
            bull.save()
            self.connected_bull = bull
        if cow:
            cow.save()
            self.connected_cow = cow

        self.save()

    def __str__(self):
        if self.connected_cow is not None:
            return "Cow: " + str(self.connected_cow.id)
        elif self.connected_bull is not None:
            return "Bull: " + str(self.connected_bull.id)


class Herd(models.Model):
    breedings = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    unrestricted = models.BooleanField(default=False)
    connectedclass = models.ForeignKey(
        to="Class",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="_herd_connectedclass",
    )
    enrollment = models.ForeignKey(
        to="Enrollment",
        related_name="_herd_enrollment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @staticmethod
    def get_auto_generated_herd(name, connectedclass, enrollment=None):
        herd = Herd()
        herd.connectedclass = connectedclass
        herd.enrollment = enrollment
        herd.name = name
        herd.save()

        cor_matrix = cor.get_cor_matrix()
        for _ in range(150):
            cow = Cow()

            cow.traits = TraitsList()
            cow.traits.auto_data(cor_matrix, cow=cow)
            cow.herd = herd
            cow.name = cow.get_name()
            cow.save()

        for _ in range(10):
            bull = Bull()

            bull.traits = TraitsList()
            bull.traits.auto_data(cor_matrix, bull=bull)
            bull.herd = herd
            bull.name = bull.get_name()
            bull.save()

        herd.save()
        return herd

    def get_summary(self):
        summary = {}

        cows = [t.traits for t in Cow.objects.filter(herd=self)]
        bulls = [t.traits for t in Bull.objects.filter(herd=self)]
        traitgroups = cows + bulls

        for trait in traitgroups:
            for key in trait.data:
                if key in summary:
                    summary[key] += trait.data[key]
                else:
                    summary[key] = trait.data[key]

        n = len(traitgroups)
        for key in summary:
            summary[key] = summary[key] / n

        return summary

    def get_herd_dict(self):
        herd = {"cows": {}, "bulls": {}}

        for cow in Cow.objects.filter(herd=self):
            herd["cows"][cow.id] = {
                "name": cow.name,
                "Generation": cow.generation,
                "Sire": cow.sire.id if cow.sire else "NA",
                "Dam": cow.dam.id if cow.sire else "NA",
                "traits": cow.traits.data,
            }

        for bull in Bull.objects.filter(herd=self):
            herd["bulls"][bull.id] = {
                "name": bull.name,
                "Generation": bull.generation,
                "Sire": bull.sire.id if bull.sire else "NA",
                "Dam": bull.dam.id if bull.sire else "NA",
                "traits": bull.traits.data,
            }

        return herd

    def run_breeding(self, sires):
        NUMBER_OF_COWS = 100
        NUMBER_OF_BULLS = 10

        n_cows = NUMBER_OF_COWS
        n_bulls = NUMBER_OF_BULLS

        MAX_GENERATION = 5

        self.breedings += 1
        self.save()

        breedings_Male = []
        breedings_Female = []
        for sire in sires:
            breedings_Male.append({"sire": sire, "cows": []})
            breedings_Female.append({"sire": sire, "cows": []})

        cows = list(Cow.objects.filter(herd=self))

        while len(cows) < n_cows + n_bulls:
            if n_cows > 0:
                n_cows -= 1
            if n_bulls > 0:
                n_bulls -= 1

        used_cows = []
        for _ in range(n_cows + n_bulls):
            cowIDX = randrange(0, len(cows))
            used_cows.append(cows[cowIDX])
            cows.pop(cowIDX)

        for _ in range(n_bulls):
            cow = used_cows.pop()
            breedings_Male[randrange(0, len(breedings_Male))]["cows"].append(cow)

        for _ in range(n_cows):
            cow = used_cows.pop()
            breedings_Female[randrange(0, len(breedings_Male))]["cows"].append(cow)

        cor_matrix = cor.get_cor_matrix()
        for breeding in breedings_Male:
            for dam in breeding["cows"]:
                Bull.from_breeding(breeding["sire"], dam, self, cor_matrix)

        for breeding in breedings_Female:
            for dam in breeding["cows"]:
                Cow.from_breeding(breeding["sire"], dam, self, cor_matrix)

        for cow in Cow.objects.filter(herd=self):
            if self.breedings - cow.generation > MAX_GENERATION:
                cow.delete()

        for bull in Bull.objects.filter(herd=self):
            if self.breedings - bull.generation > MAX_GENERATION:
                bull.delete()

    def __str__(self):
        if self.connectedclass:
            return self.connectedclass.name + ": " + self.name
        else:
            return self.name


class Cow(models.Model):
    __str__ = lambda self: self.name

    generation = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    herd = models.ForeignKey(to=Herd, on_delete=models.CASCADE, null=True)
    traits = models.OneToOneField(
        to=TraitsList, on_delete=models.SET_NULL, related_name="_cowtraits", null=True
    )

    dam = models.ForeignKey(
        to="Cow", on_delete=models.SET_NULL, null=True, default=None
    )
    sire = models.ForeignKey(
        to="Bull", on_delete=models.SET_NULL, null=True, default=None
    )

    def get_name(self):
        return f"X Id-{self.id} Gen-{self.generation}"

    def get_sexed_id(self):
        return "f" + str(self.id)

    @staticmethod
    def from_breeding(sire, dam, herd, cor_matrix):
        cow = Cow()
        cow.traits = TraitsList.get_mutated_average(
            sire.traits, dam.traits, cor_matrix, cow=cow
        )
        cow.generation = herd.breedings
        cow.herd = herd
        cow.name = cow.get_name()
        cow.sire = sire
        cow.dam = dam

        cow.save()


class Bull(models.Model):
    __str__ = lambda self: self.name

    generation = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    herd = models.ForeignKey(to=Herd, on_delete=models.CASCADE, null=True)
    traits = models.OneToOneField(
        to=TraitsList, on_delete=models.CASCADE, related_name="_bulltraits", null=True
    )

    dam = models.ForeignKey(
        to="Cow", on_delete=models.SET_NULL, null=True, default=None
    )
    sire = models.ForeignKey(
        to="Bull", on_delete=models.SET_NULL, null=True, default=None
    )

    def get_name(self):
        return f"Y id-{self.id} Gen-{self.generation}"

    def get_sexed_id(self):
        return "m" + str(self.id)

    @staticmethod
    def from_breeding(sire, dam, herd, cor_matrix):
        bull = Bull()
        bull.traits = TraitsList.get_mutated_average(
            sire.traits, dam.traits, cor_matrix, bull=bull
        )
        bull.generation = herd.breedings
        bull.herd = herd
        bull.name = bull.get_name()
        bull.sire = sire
        bull.dam = dam
        bull.save()


class Class(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255)
    classcode = models.CharField(unique=True, max_length=255)
    teacherclasscode = models.CharField(unique=True, max_length=255)
    info = models.TextField(blank=True, null=True, max_length=1024)
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="classowner"
    )
    herd = models.OneToOneField(
        to=Herd, on_delete=models.CASCADE, related_name="classherd"
    )

    @staticmethod
    def get_class_code():
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
        """returns (object: Class, teacher: bool)"""
        try:
            _class = Class.objects.get(classcode=code)
            teacher = False
        except:
            _class = Class.objects.get(teacherclasscode=code)
            teacher = True

        return _class, teacher


class Enrollment(models.Model):
    __str__ = lambda self: self.user.username + " in " + self.connectedclass.name

    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="_enrollmentuser"
    )
    connectedclass = models.ForeignKey(
        to=Class, on_delete=models.CASCADE, related_name="_enrollmentclass"
    )
    teacher = models.BooleanField(default=False)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        Enrollment.scrub_enrollment(self.user, self.connectedclass)

    @staticmethod
    def scrub_enrollment(user, connectedclass):
        enrollments = list(
            Enrollment.objects.filter(user=user, connectedclass=connectedclass)
        )

        while len(enrollments) > 1:
            e = enrollments.pop()
            e.delete()
