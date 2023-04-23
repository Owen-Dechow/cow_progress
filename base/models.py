from django.db import models
from django.contrib.auth.models import User
from random import randrange, random
from . import correlations as cor

PTA_DECIMALS = 3  # Number of decimal placements shown for PTAs on website/ xlsx files
MUTATION_RATE = 0.25  # Maximum mutation of a PTA in one generation from -1 to 1 value


# List of recourses found on front page
class Resource(models.Model):
    __str__ = lambda self: self.title

    title = models.CharField(max_length=255)  # The text that will be displayed for resource
    link = models.CharField(max_length=255)  # Url to the resource itself


# Holds the information for one PTA
class Trait(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255) # Common identifier of the PTA (MILK, PROT, DCE, etc.)
    average = models.FloatField() # The average PTA value | Should always be 0
    standard_deviation = models.FloatField() # The standard deviation of PTA | AKA The scale factor


# Correlation class for PTAs
class Correlation(models.Model):
    __str__ = lambda self: str(self.trait_a) + " to " + str(self.trait_b)

    factor = models.FloatField() # Strength of the correlation

    #### The connected PTAs ####
    trait_a = models.ForeignKey(
        to=Trait, on_delete=models.CASCADE, related_name="trait_b"
    )
    trait_b = models.ForeignKey(
        to=Trait, on_delete=models.CASCADE, related_name="trait_a"
    )


# Holds the PTAs on single animal
class TraitsList(models.Model):
    data = models.JSONField() # Stores the unscaled data -1 to 1 form
    scaled = models.JSONField() # Stores the front end scaled PTA data

    #### Refrances either the cow or bull connected to PTA list ####
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
        """ Takes in two TraitsLists and creates a child List from the data """

        # Create and initialize new List
        new = TraitsList()
        new.data = {}

        # Generate mutated uncorrelated values -1 to 1
        uncorrelated = {}
        for trait in Trait.objects.all():
            val = (a.data[trait.name] + b.data[trait.name]) / 2
            newval = val + MUTATION_RATE * cor.DOMAIN()
            
            # Ensure new value is in range -1 to 1
            if abs(newval) > 1:
                newval += abs(newval) / newval

            uncorrelated[trait.name] = newval

        # Correlate data
        initial_val_list = [uncorrelated[key.name] for key in cor_matrix["traits"]]
        corelated_data = cor.get_result(cor_matrix, initial_values=initial_val_list)
        new.data = cor.convert_data(corelated_data)
        
        # Scale data for front end
        new.set_scaled_data()

        # Connect to animal
        if bull:
            bull.save()
            new.connected_bull = bull
        if cow:
            cow.save()
            new.connected_cow = cow

        new.save()
        return new

    def auto_data(self, cor_matrix, cow=None, bull=None):
        """ Auto generates the data for one TraitsList"""

        # Get data -1 to 1
        correlated_data = cor.get_result(cor_matrix)
        self.data = cor.convert_data(correlated_data)
        
        # Scale the data
        self.set_scaled_data()

        # Connect to animal and save data
        if bull:
            bull.save()
            self.connected_bull = bull
        if cow:
            cow.save()
            self.connected_cow = cow
        self.save()

    def set_scaled_data(self):
        """ Scales the data field into the scaled field """

        traits = Trait.objects.all()
        scaled_data = {}
        for key, val in self.data.items():
            scaled_data[key] = round(
                traits.get(name=key).standard_deviation * val, PTA_DECIMALS
            )

        self.scaled = scaled_data

    def __str__(self):
        if self.connected_cow is not None:
            return "Cow: " + str(self.connected_cow.id)
        elif self.connected_bull is not None:
            return "Bull: " + str(self.connected_bull.id)
        else:
            return "NONE"


# Holds a group of animals
class Herd(models.Model):
    name = models.CharField(max_length=255) # Name of the herd
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True) # Owner of the herd
    breedings = models.IntegerField(default=0) # Number of breedings that have been run on herd
    unrestricted = models.BooleanField(default=False) # Tells if herd can be accessed by anyone
    
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
        """ Builds a random herd """

        NUMBER_OF_COWS = 150 # Number of cows generated
        NUMBER_OF_BULLS = 10 # Number of bulls generated

        # Create and initialize herd
        herd = Herd()
        herd.connectedclass = connectedclass
        herd.enrollment = enrollment
        herd.name = name
        herd.save()

        # Build correlation matrix
        cor_matrix = cor.get_cor_matrix()

        # Create cows
        for _ in range(NUMBER_OF_COWS):
            cow = Cow()

            cow.traits = TraitsList()
            cow.traits.auto_data(cor_matrix, cow=cow)
            cow.herd = herd
            cow.name = cow.get_name()
            cow.save()

        # Create bulls
        for _ in range(NUMBER_OF_BULLS):
            bull = Bull()

            bull.traits = TraitsList()
            bull.traits.auto_data(cor_matrix, bull=bull)
            bull.herd = herd
            bull.name = bull.get_name()
            bull.save()

        herd.save()
        return herd

    def get_summary(self):
        """ Gets a JSON serializable dict of all PTAs average among animals """

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
        """ Gets a JSON serializable dict of all animals in herd """

        herd = {"cows": {}, "bulls": {}}

        # Adds cows to dict
        for cow in Cow.objects.filter(herd=self):
            herd["cows"][cow.id] = {
                "name": cow.name,
                "Generation": cow.generation,
                "Sire": cow.sire.id if cow.sire else "NA",
                "Dam": cow.dam.id if cow.dam else "NA",
                "traits": cow.traits.scaled,
            }

        # Adds bulls to dict
        for bull in Bull.objects.filter(herd=self):
            herd["bulls"][bull.id] = {
                "name": bull.name,
                "Generation": bull.generation,
                "Sire": bull.sire.id if bull.sire else "NA",
                "Dam": bull.dam.id if bull.dam else "NA",
                "traits": bull.traits.scaled,
            }

        return herd

    def run_breeding(self, sires):
        """ Breeds the herd to specified bulls """

        NUMBER_OF_COWS = 100 # Planed number of cows generated
        NUMBER_OF_BULLS = 10 # Planed number of bulls generated
        MAX_GENERATION = 5 # Max age of animal before its removed

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
        cor_matrix = cor.get_cor_matrix()
        for breeding in breedings_Male:
            for dam in breeding["cows"]:
                Bull.from_breeding(breeding["sire"], dam, self, cor_matrix)

        # Generate new cows
        for breeding in breedings_Female:
            for dam in breeding["cows"]:
                Cow.from_breeding(breeding["sire"], dam, self, cor_matrix)

        #### Remove any animals over the max age ####
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


# Single female animal
class Cow(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255) # Holds the name of the cow
    herd = models.ForeignKey(to=Herd, on_delete=models.CASCADE, null=True) # Holds the herd the cow is part of
    generation = models.IntegerField(default=0) # Holds the generation the cow was born in
    
    # Connects a trait list to cow
    traits = models.OneToOneField(
        to=TraitsList, on_delete=models.SET_NULL, related_name="Cull_traits_TraitsList", null=True
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
        """ Autogenerates a name for cow """

        return f"X Id-{self.id} Gen-{self.generation}"

    def get_sexed_id(self):
        """ Gets the int id of cow with the 'f' prefix """

        return "f" + str(self.id)

    @staticmethod
    def from_breeding(sire, dam, herd, cor_matrix):
        """ Creates a cow from a breeding """

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


# Single male animal
class Bull(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255) # Holds the name of the bull
    herd = models.ForeignKey(to=Herd, on_delete=models.CASCADE, null=True) # Holds the herd the bull is part of
    generation = models.IntegerField(default=0) # Holds the generation the bull was born in

    # Connects a trait list to bull
    traits = models.OneToOneField(
        to=TraitsList, on_delete=models.SET_NULL, related_name="Bull_traits_TraitsList", null=True
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
        """ Autogenerates a name for bull """

        return f"Y id-{self.id} Gen-{self.generation}"

    def get_sexed_id(self):
        """ Gets the int id of cow with the 'm' prefix """

        return "m" + str(self.id)

    @staticmethod
    def from_breeding(sire, dam, herd, cor_matrix):
        """ Creates a bull from a breeding """
        
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


# Class object
class Class(models.Model):
    __str__ = lambda self: self.name

    name = models.CharField(max_length=255) # Holds the name of the class
    info = models.TextField(blank=True, null=True, max_length=1024) # Holds the class info
    classcode = models.CharField(unique=True, max_length=255) # Holds the student enrollment code
    teacherclasscode = models.CharField(unique=True, max_length=255) # Holds the teacher enrollment code
    
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
        """ Autogenerates a class code """

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
        """ Gets the class from classcode and returns it in a tuple with the a boolean
        telling if a teacher class code was used  """
        
        try:
            _class = Class.objects.get(classcode=code)
            teacher = False
        except:
            _class = Class.objects.get(teacherclasscode=code)
            teacher = True

        return _class, teacher


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
        """ Saves the enrollment and calls the scrub method """

        super().save(*args, **kwargs)
        Enrollment.scrub_enrollment(self.user, self.connectedclass)

    @staticmethod
    def scrub_enrollment(user, connectedclass):
        """ Deletes any douplicate enrollments """

        enrollments = list(
            Enrollment.objects.filter(user=user, connectedclass=connectedclass)
        )

        while len(enrollments) > 1:
            e = enrollments.pop()
            e.delete()
