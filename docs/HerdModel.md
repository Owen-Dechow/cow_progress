# Herd Model

Represents a single herd of bulls and cows.


## Properties

```python
name = CharField(max_length=255)
# Stores the name of the herd.
```

```python
owner = models.ForeignKey(
    to=User,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
# Stores the name of the herd.
# Owner is set to the creator of herd.
```

```python
breedings = models.IntegerField(default=0)
# Stores the number of breedings run on herd.
# Used to prevent herd from exceeding class limit.
```

```python
connectedclass = models.ForeignKey(
    to="Class",
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="_herd_connectedclass",
)
# Stores the class the herd was created for.
```

```python
enrollment = models.ForeignKey(
    to="Enrollment",
    related_name="_herd_enrollment",
    on_delete=models.CASCADE,
    null=True,
    blank=True,
)
# Stores the enrollment used to create herd if herd is not Class or Public Herd.
```

```python
@staticmethod
get_auto_generated_herd(name, connectedclass, enrollment=None):
# Builds a random herd connected to class and enrollment.
```


## Methods

```python
@staticmethod
make_public_herd(name, animal_name_prefix, star_word, connectedclass):
# Creates a class public herd.
# Auto names animals based on animal_name_prefix, star_word & connected class.
```

```python
get_summary(self):
# Gets a dict object with all traits & NM$ averages of animals in herd.
# Any trait hidden by class will be set to "~".
# Returned dict: JSON serializable.

# Example:
{
    "Milk": 0.56,
    "PROT": -0.1,
    "SCS": "~",
    "NM$": 15,
}
```

```python
get_herd_dict(self):
# Gets dict containing all animals.
# Returns Cows and Bulls in separate sections.
# Animals identified by id number.
# Returned dict: JSON serializable.

#Example:
{
    "cows": {
        23: {
            "name": "example cow",
            "Generation": 0,
            "Sire": "~",
            "Dam": "~",
            "Inbreeding Coefficient": 0,
            "traits": {
                "Milk": 0.56,
                "PROT": -0.1,
                "SCS": "~",
                "NM$": 15,
            },
            "recessives": {
                "BLAD": 0,
                "BY": 1,
                "CR", 0,
            },
        }
    },
    "bulls": {
    },
}
```

```python
run_breeding(self, sires):
    NUMBER_OF_COWS = 100
    NUMBER_OF_BULLS = 10
    MAX_GENERATION = 5
# Takes in a list of sires and breeds cows to result in NUMBER_OF_COWS cows and NUMBER_OF_BULLS bulls then culls any animals of MAX_GENERATION age.

# Finally calls remove_deaths_from_recessives.
```

```python
remove_deaths_from_recessives(self):
# Culls any animal positive for any fatal recessive.
```