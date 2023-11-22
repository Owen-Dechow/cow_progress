register = [
    ("NM_2021", True),
    ("MILK_FAT_PROT", True),
]

TRAITSET_CHOICES = [(item, item) for item, allow in register if allow]
