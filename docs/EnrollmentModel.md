# Enrollment Model

Connects users to classes

## Properties

```python
user = models.ForeignKey(
    to=User,
    on_delete=models.CASCADE,
    related_name="_enrollmentuser"
)
# Connects the student or teacher
```

```python
connectedclass = models.ForeignKey(
    to=Class,
    on_delete=models.CASCADE,
    related_name="_enrollmentclass"
)
# Connects the class
```

```python
teacher = models.BooleanField(default=False)
# Tells if user is a teacher (true) or student (false)
```