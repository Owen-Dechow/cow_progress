# Bovine Model

Holds data for one animal

## Properties

```python
name = models.CharField(max_length=255, null=True)
# Stores the name of the animal for webpage
```

```python
herd = models.ForeignKey(to=Herd, on_delete=models.SET_NULL, null=True)
# Stores the herd animal belongs to
```

```python
generation = models.IntegerField(default=0)
# Stores the breeding run the animal was born in
```

```python
male = models.BooleanField(null=True)
# Stores the sex of the animal
# True = Male, False = Female
```

```python
genotype = models.JSONField(default=dict) 
# Stores the genotype of the animal
```

```python
phenotype = models.JSONField(default=dict, null=True)
# Stores the phenotype of the animal
```

```python
recessives = models.JSONField(default=dict)
# Stores recessive information of the animal
```

```python
connectedclass = models.ForeignKey(to="Class", on_delete=models.CASCADE)
# Stores what class animal is associated with
```

```python
dam = models.ForeignKey(
    to="Bovine",
    related_name="_dam",
    on_delete=models.SET_NULL,
    null=True,
)
# Stores the mother of the animal
```

```python
sire = models.ForeignKey(
    to="Bovine",
    related_name="_sire",
    on_delete=models.SET_NULL,
    null=True,
)
# Stores the father of the animal
```

```python
pedigree = models.JSONField(null=True)
# Stores a dictionary version of the pedigree
```

```python
inbreeding = models.FloatField(null=True)
# Stores the inbreeding coefficient of the animal
```

## Methods

```python
@staticmethod
def create_from_breeding(sire, dam, herd, male):
# Creates and returns a new animal from breeding of sire and dam
# Herd will be auto set to 'herd' arg and sex will be auto set to 'male' arg
```

```python
@staticmethod
def auto_generate(herd, male):
# Auto generates and returns a completely random animal on normal distribution
```

```python
def set_phenotypes(self):
# Uses animals genotype to calculate and set the animal phenotype
```

```python
def get_dict(self, connectedclass=None):
# Returns a JSON serializable dictionary representation of the animal
```

```python
def set_net_merit(self):
# Calculates and sets the Net Merit (NM$) of the animal
# NM$ value will be saved as 'Net Merit' key in genotypes
```

```python
def auto_generate_name(self, herd):
# Auto generates and returns a name for animal based off of herd
```

```python
def auto_generate_pedigree(self):
# Creates and returns the pedigree of the animal
```

```python
def get_inbreeding(self):
# Calculates and sets the inbreeding coefficient of animal
```