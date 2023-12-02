# Class Model

Represents a single class

## Properties

```python
name = models.CharField(max_length=255)
# Holds the name of the class used on webpage
```

```python
info = models.TextField(
    blank=True, null=True, max_length=1024
) 
# Holds the class info displayed on webpage
```

```python
classcode = models.CharField(
    unique=True, max_length=255
)
# Holds the student enrollment code
```

```python
teacherclasscode = models.CharField(
    unique=True, max_length=255
)
# Holds the teacher enrollment code
```

```python
viewable_traits = models.JSONField()
# Defines what traits are visible to students
```

```python
viewable_recessives = models.JSONField(null=True)
# Defines what recessives are visible to students
```

```python
breeding_limit = models.IntegerField(default=0)
# Maximun number of breedings allowed on a class herd
```

```python
trend_log = models.JSONField(default=dict)
# Holds the population average after each breeding
```

```python
owner = models.ForeignKey(
    to=User,
    on_delete=models.CASCADE,
    related_name="classowner"
)
# Connects the owner of the class
```

```python
herd = models.OneToOneField(
    to=Herd,
    on_delete=models.CASCADE,
    related_name="classherd",
    null=True
)
# Connects a class herd
```

```python
publicherd = models.OneToOneField(
    to=Herd,
    on_delete=models.CASCADE,
    related_name="classpublicherd",
    null=True
)
# Connects a class public herd
```

```python
traitset = models.CharField(
    max_length=20,
    default=TRAITSET_CHOICES[0][0],
    null=True,
)
# Selects the traitset for class
```

## Methods

```python
def update_trend_log(self, entry_name: str):
# Updates the trend_log field
```

```python
@staticmethod
def get_class_code():
    CODE_SECTIONS = 3
    CHAR_PER_SECTIONS = 3
    ALLOWEDCHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
# Generates a random unique class code
```

```python
@staticmethod
def get_from_code(code):
# Gets a class from class code, raises error if no class found
```

## Meta
```python
class Meta:
    verbose_name_plural = "Classes"
```