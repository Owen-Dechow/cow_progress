from django.contrib.auth.forms import UserCreationForm
from django import forms
from . import models


class CustomUserCreationForm(UserCreationForm):
    def save(self, commit: bool = False):
        user = super().save(commit)
        user.save()

    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name", "last_name", "email")


class JoinClass(forms.Form):
    def is_valid(self, user) -> bool:
        connectedclass = models.Class.get_from_code(self.data["connectedclass"])
        try:
            enrollment = models.Enrollment.objects.get(
                connectedclass=connectedclass[0], user=user
            )
            return False
        except:
            return super().is_valid()

    def save(self, user):
        connectedclass = models.Class.get_from_code(self.cleaned_data["connectedclass"])

        enrollment = models.Enrollment()
        enrollment.connectedclass = connectedclass[0]
        enrollment.teacher = connectedclass[1]
        enrollment.user = user

        herd = models.Herd.get_auto_generated_herd("Personal Herd", connectedclass[0])
        herd.owner = user
        herd.connectedclass = connectedclass[0]
        herd.save()

        enrollment.save()
        herd.enrollment = enrollment
        herd.save()

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


class AddClass(forms.Form):
    connectedclass = forms.CharField(
        max_length=100,
        label="Class Name",
    )
    info = forms.CharField(
        widget=forms.Textarea, label="Class Info", max_length=1024, required=False
    )
    formid = forms.CharField(
        initial="addclass", widget=forms.HiddenInput, label="", required=False
    )

    def is_valid(self, user) -> bool:
        return super().is_valid()

    def save(self, user):
        connectedclass = models.Class()
        connectedclass.name = self.cleaned_data["connectedclass"]
        connectedclass.teacherclasscode = models.Class.get_class_code()
        connectedclass.classcode = models.Class.get_class_code()
        connectedclass.owner = user
        connectedclass.info = self.cleaned_data["info"]

        herd = models.Herd()
        herd.name = connectedclass.name
        herd.save()

        connectedclass.herd = herd
        connectedclass.save()

        herd.connectedclass = connectedclass
        herd.save()

        enrollment = models.Enrollment()
        enrollment.connectedclass = connectedclass
        enrollment.teacher = True
        enrollment.user = user
        enrollment.save()


class DeleteClass(forms.Form):
    connectedclass = forms.IntegerField(widget=forms.HiddenInput)
    formid = forms.CharField(initial="deleteclass", widget=forms.HiddenInput)

    def is_valid(self, user) -> bool:
        try:
            enrollment = models.Enrollment.objects.get(
                user=user,
                connectedclass=models.Class.objects.get(id=self.data["connectedclass"]),
            )
            assert enrollment.connectedclass.owner == user
            return super().is_valid()
        except Exception as e:
            return False

    def save(self, user):
        data = self.cleaned_data

        enrollment = models.Enrollment.objects.get(
            user=user,
            connectedclass=models.Class.objects.get(id=data["connectedclass"]),
        )
        enrollment.connectedclass.delete()


class ExitClass(forms.Form):
    connectedclass = forms.IntegerField(widget=forms.HiddenInput)
    formid = forms.CharField(initial="exitclass", widget=forms.HiddenInput)

    def is_valid(self, user) -> bool:
        try:
            enrollment = models.Enrollment.objects.get(
                user=user,
                connectedclass=models.Class.objects.get(id=self.data["connectedclass"]),
            )
            assert enrollment.connectedclass.owner != user
            return super().is_valid()
        except:
            return False

    def save(self, user):
        data = self.cleaned_data

        enrollment = models.Enrollment.objects.get(
            user=user,
            connectedclass=models.Class.objects.get(
                id=self.cleaned_data["connectedclass"]
            ),
        )
        enrollment.delete()


class PromoteClass(forms.Form):
    connectedclass = forms.IntegerField(widget=forms.HiddenInput)
    formid = forms.CharField(initial="promoteclass", widget=forms.HiddenInput)
    classcode = forms.CharField(
        max_length=100,
        label="Teacher Promotion Code",
    )

    def is_valid(self, user) -> bool:
        try:
            enrollment = models.Enrollment.objects.get(
                user=user,
                connectedclass=models.Class.objects.get(id=self.data["connectedclass"]),
            )
            assert models.Class.get_from_code(self.data["classcode"])[1]
            assert not enrollment.teacher
            return super().is_valid()
        except:
            return False

    def save(self, user):
        enrollment = models.Enrollment.objects.get(
            user=user,
            connectedclass=models.Class.objects.get(
                id=self.cleaned_data["connectedclass"]
            ),
        )
        enrollment.teacher = True
        enrollment.save()


class EditUser(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    @staticmethod
    def get_user(user):
        info = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return EditUser(info)

    def save(self, user):
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()


class Passwordcheck(forms.Form):
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(),
        help_text="Reconfirm password to continue.",
    )
