from django.contrib.auth.forms import UserCreationForm
from django import forms
from . import models
from .traitinfo import traits, traitsets


# User registration form
class CustomUserCreationForm(UserCreationForm):
    def save(self, commit: bool = False):
        user = super().save(commit)
        user.save()

    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name", "last_name", "email")


# Join a class form
class JoinClass(forms.Form):
    def is_valid(self, user) -> bool:
        # Find connected class for code
        try:
            connectedclass = models.Class.get_from_code(self.data["connectedclass"])
        except:
            return False

        try:
            # Make sure user is not already enrolled in class
            _ = models.Enrollment.objects.get(
                connectedclass=connectedclass[0], user=user
            )
            return False
        except:
            return super().is_valid()

    def save(self, user):
        # Find connected class
        connectedclass = models.Class.get_from_code(self.cleaned_data["connectedclass"])

        # Create enrollment
        enrollment = models.Enrollment()
        enrollment.connectedclass = connectedclass[0]
        enrollment.teacher = connectedclass[1]
        enrollment.user = user
        enrollment.save()

    @staticmethod
    def validate_classcode(value):
        try:
            connectedclass = models.Class.get_from_code(value)
        except:
            raise forms.ValidationError("This is not a recognized classcode.")

    connectedclass = forms.CharField(
        max_length=models.Class._meta.get_field("classcode").max_length,
        validators=[validate_classcode],
        label="Class Code",
    )
    formid = forms.CharField(initial="joinclass", widget=forms.HiddenInput, label="")


# Create a class form
class AddClass(forms.Form):
    classname = forms.CharField(
        max_length=100,
        label="Class Name",
    )

    info = forms.CharField(
        widget=forms.Textarea, label="Class Info", max_length=1024, required=False
    )

    formid = forms.CharField(
        initial="addclass", widget=forms.HiddenInput, label="", required=False
    )

    traitset = forms.ChoiceField(
        choices=traitsets.TRAITSET_CHOICES, initial=traitsets.TRAITSET_CHOICES[0][0]
    )

    def is_valid(self, user) -> bool:
        return super().is_valid()

    def save(self, user):
        """Create class object and enroll user as owner"""

        # Create class
        connectedclass = models.Class()
        connectedclass.name = self.cleaned_data["classname"]
        connectedclass.teacherclasscode = models.Class.get_class_code()
        connectedclass.classcode = models.Class.get_class_code()
        connectedclass.owner = user
        connectedclass.info = self.cleaned_data["info"]
        connectedclass.traitset = self.cleaned_data["traitset"]
        connectedclass.viewable_traits = {
            x.name: True for x in traits.Trait.get_all(connectedclass.traitset)
        } | {"Net Merit": True}
        connectedclass.save()

        # Create class herd
        herd = models.Herd()
        herd.name = f"[{connectedclass.name}] Class Herd"
        herd.connectedclass = connectedclass
        herd.save()

        # Create class public herd
        name_prefix = connectedclass.name
        name_prefix += "'" if connectedclass.name[-1] == "s" else "'s"
        publicherd = models.Herd.make_public_herd(
            f"[{connectedclass.name}] Public Herd", name_prefix, "Star", connectedclass
        )
        publicherd.save()

        # Connect class to heard
        connectedclass.herd = herd
        connectedclass.publicherd = publicherd
        connectedclass.save()

        # Enroll owner as teacher
        enrollment = models.Enrollment()
        enrollment.connectedclass = connectedclass
        enrollment.teacher = True
        enrollment.user = user
        enrollment.save()


# Delete a class form
class DeleteClass(forms.Form):
    connectedclass = forms.IntegerField(widget=forms.HiddenInput)
    formid = forms.CharField(initial="deleteclass", widget=forms.HiddenInput)

    def is_valid(self, user) -> bool:
        try:
            # Check to make sure user is enrolled in class
            enrollment = models.Enrollment.objects.get(
                user=user,
                connectedclass=models.Class.objects.get(id=self.data["connectedclass"]),
            )

            # Check to make sure user is class owner
            assert enrollment.connectedclass.owner == user

            # Standard validation
            return super().is_valid()
        except:
            return False

    def save(self, user):
        data = self.cleaned_data

        enrollment = models.Enrollment.objects.get(
            user=user,
            connectedclass=models.Class.objects.get(id=data["connectedclass"]),
        )
        enrollment.connectedclass.delete()


# Un enroll from class form
class ExitClass(forms.Form):
    connectedclass = forms.IntegerField(widget=forms.HiddenInput)
    formid = forms.CharField(initial="exitclass", widget=forms.HiddenInput)

    def is_valid(self, user) -> bool:
        try:
            # Check to make sure student is enrolled in class
            enrollment = models.Enrollment.objects.get(
                user=user,
                connectedclass=models.Class.objects.get(id=self.data["connectedclass"]),
            )

            # Check to make sure student is not class owner
            assert enrollment.connectedclass.owner != user

            # Standard validation
            return super().is_valid()
        except:
            return False

    def save(self, user):
        """Delete the student's enrollment"""
        enrollment = models.Enrollment.objects.get(
            user=user,
            connectedclass=models.Class.objects.get(
                id=self.cleaned_data["connectedclass"]
            ),
        )
        enrollment.delete()


# Premote from student to teacher form
class PromoteClass(forms.Form):
    connectedclass = forms.IntegerField(widget=forms.HiddenInput)
    formid = forms.CharField(initial="promoteclass", widget=forms.HiddenInput)
    classcode = forms.CharField(
        max_length=100,
        label="Teacher Promotion Code",
    )

    def is_valid(self, user) -> bool:
        try:
            # Check to make sure that student is already in class
            enrollment = models.Enrollment.objects.get(
                user=user,
                connectedclass=models.Class.objects.get(id=self.data["connectedclass"]),
            )

            # Check to make sure that class exists
            assert models.Class.get_from_code(self.data["classcode"])[1]

            # Check to make sure that entered code is a teacher code
            assert not enrollment.teacher

            # Standard validation
            return super().is_valid()
        except:
            return False

    def save(self, user):
        """Update the users enrollment info"""

        enrollment = models.Enrollment.objects.get(
            user=user,
            connectedclass=models.Class.objects.get(
                id=self.cleaned_data["connectedclass"]
            ),
        )
        enrollment.teacher = True
        enrollment.save()


# Updates class info
class UpdateClass(forms.Form):
    def is_valid(self, user) -> bool:
        try:
            connectedclass = models.Class.objects.get(id=self.data["connectedclass"])

            enrollment = models.Enrollment.objects.get(
                user=user, connectedclass=connectedclass
            )

            assert enrollment.teacher

            assert "classinfo" in self.data

            assert int(self.data["maxgen"]) >= 0

            return True
        except:
            return False

    def save(self, user):
        connectedclass = models.Class.objects.get(id=self.data["connectedclass"])

        for trait in connectedclass.viewable_traits:
            connectedclass.viewable_traits[trait] = "trait-" + trait in self.data

        connectedclass.info = self.data["classinfo"]
        connectedclass.breeding_limit = self.data["maxgen"]
        connectedclass.save()


# Change user info form
class EditUser(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    @staticmethod
    def get_user(user):
        """Returns a new form prefilled with user info.
        Use over regular initializer"""

        info = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return EditUser(info)

    def save(self, user):
        """Update the users information"""

        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()


# Get password form
class Passwordcheck(forms.Form):
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(),
    )
