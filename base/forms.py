from django.contrib.auth.forms import UserCreationForm
from django import forms
from . import models
from .models import NET_MERIT_KEY
from .traitinfo.traitsets import TraitSet, TRAITSET_CHOICES


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
        except models.Class.DoesNotExist:
            return False

        try:
            # Make sure user is not already enrolled in class
            _enrollment = models.Enrollment.objects.get(
                connectedclass=connectedclass[0], user=user
            )

            self.add_error("connectedclass", "Cannot enroll in class more than once.")
            return False
        except models.Enrollment.DoesNotExist:
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

        return enrollment

    @staticmethod
    def validate_classcode(value):
        try:
            _connectedclass = models.Class.get_from_code(value)
        except models.Class.DoesNotExist:
            raise forms.ValidationError("This is not a recognized classcode.")

    connectedclass = forms.CharField(
        max_length=models.Class._meta.get_field("classcode").max_length,
        validators=[validate_classcode],
        strip=False,
        label="Class Code",
    )


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
        choices=TRAITSET_CHOICES, initial=TRAITSET_CHOICES[-1][0]
    )

    def is_valid(self) -> bool:
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

        traitset = TraitSet(connectedclass.traitset)
        connectedclass.viewable_traits = {NET_MERIT_KEY: True}
        connectedclass.viewable_traits |= {x.name: True for x in traitset.traits}
        connectedclass.viewable_recessives = {x.name: True for x in traitset.recessives}

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

        connectedclass.update_trend_log("Initial Population")

        return enrollment


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


# Auto generate herd form
class AutoGenerateHerd(forms.Form):
    name = forms.CharField(max_length=255)
