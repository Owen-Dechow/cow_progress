from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .traitinfo import traits
from io import BytesIO
from . import models
from . import forms
from . import excel


########### Utility functions ##########


def auth_herd(request: WSGIRequest, herd: models.Herd, error=True, unprotected=True):
    """Authenticate a users herd acceses"""

    if unprotected:
        if herd.unrestricted:
            return True

        classes = [
            x.connectedclass
            for x in models.Enrollment.objects.filter(user=request.user)
        ]
        for connectedclass in classes:
            if herd == connectedclass.herd:
                return True

    if herd.owner == request.user:
        return True

    if error:
        raise Http404()
    return False


def auth_password(request: WSGIRequest):
    """Ensure user entered a proper password | request.POST['password']"""

    form = forms.Passwordcheck(request.POST)
    if form.is_valid():
        if check_password(form.cleaned_data["password"], request.user.password):
            return True

    return False


def string_validation(
    string: str, minlength: int, maxlength: int, specialchar="", allowall=False
):
    """Validate a string"""

    if len(string) not in range(minlength, maxlength + 1):
        raise Http404()

    if not allowall:
        for l in string:
            if not (l in specialchar or l.isalpha() or l.isdigit()):
                raise Http404()

    return True


def JSONSuccess(success: bool):
    """Returns a success dict"""
    return JsonResponse({"successful": success})


########## Page views ##########


def home(request: WSGIRequest):
    """Home page"""

    args = {"resources": models.Resource.objects.all()}
    return render(request, "base/home.html", args)


def register(request: WSGIRequest):
    """Signup page"""

    if request.method == "POST":
        user = forms.CustomUserCreationForm(request.POST)

        if user.is_valid():
            user.save()
            login(request, User.objects.get(username=user.cleaned_data["username"]))

            return HttpResponseRedirect("/")
    else:
        user = forms.CustomUserCreationForm()

    return render(request, "auth/register.html", {"form": user})


@login_required
def account(request: WSGIRequest):
    """Your account page"""

    context = {"passwordcheck": forms.Passwordcheck}

    for message in messages.get_messages(request):
        if "wrong-password" == str(message):
            context["passworderror"] = True

    if request.method == "POST":
        form = forms.EditUser(request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect("/account")
        else:
            return render(request, "auth/account.html", {"form": form} | context)
    else:
        return render(
            request,
            "auth/account.html",
            {"form": forms.EditUser.get_user(request.user)} | context,
        )


def account_deleted(request: WSGIRequest):
    """Account deleted page"""

    return render(request, "auth/account_deleted.html")


@login_required
def herds(request: WSGIRequest):
    """Your herds page"""

    classes = [
        x.connectedclass for x in models.Enrollment.objects.filter(user=request.user)
    ]
    return render(
        request,
        "base/herds.html",
        {
            "classes": classes,
            "maxlen": models.Herd._meta.get_field("name").max_length,
        },
    )


@login_required
def open_herd(request: WSGIRequest, herdID: int):
    """View herd page"""

    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd)

    if herd.unrestricted:
        herdstatus = "Public"
    elif herd.connectedclass.herd == herd:
        herdstatus = "Class"
    else:
        herdstatus = "Private"

    return render(
        request,
        "base/open_herd.html",
        {"herd": herd, "herdstatus": herdstatus},
    )


@login_required
def classes(request: WSGIRequest):
    """Your classes page"""

    view_forms = {
        "joinclass": forms.JoinClass,
        "addclass": forms.AddClass,
        "exitclass": forms.ExitClass,
        "deleteclass": forms.DeleteClass,
        "promoteclass": forms.PromoteClass,
    }

    if request.method == "POST":
        try:
            formid = request.POST["formid"]
            form = view_forms[formid](request.POST)
            view_forms[formid] = form
            if form.is_valid(request.user):
                form.save(request.user)

            return HttpResponseRedirect("/classes")
        except Exception as e:
            raise Http404()

    enrollments = models.Enrollment.objects.filter(user=request.user)
    enrollment_info = {}

    for e in enrollments:
        enrollment_info[e] = [
            x for x in models.Enrollment.objects.filter(connectedclass=e.connectedclass)
        ]

    return render(
        request,
        "base/classes.html",
        view_forms | {"enrollmentinfo": enrollment_info},
    )


def recessives(request: WSGIRequest):
    return render(request, "base/recessives.html")


########## JSON requests ##########
@login_required
def traitnames(request: WSGIRequest):
    """JSON dict of all trait names"""

    traitdict = {}

    for trait in traits.Trait.Get_All():
        traitdict[trait.name] = trait.standard_deviation

    return JsonResponse(traitdict)


@login_required
def herdsummaries(request: WSGIRequest):
    """JSON dict of all accessable herd summaries"""

    publicherdlist = models.Herd.objects.filter(unrestricted=True)
    privateherdlist = models.Herd.objects.filter(owner=request.user)
    classherdslist = [
        x.connectedclass.herd
        for x in models.Enrollment.objects.filter(user=request.user)
    ]

    summaries = {"public": {}, "private": {}, "class": {}}

    for herd in list(publicherdlist) + classherdslist:
        summaries["public"][herd.id] = {
            "name": herd.name,
            "class": herd.connectedclass.name,
            "traits": herd.get_summary(),
        }

    for herd in privateherdlist:
        summaries["private"][herd.id] = {
            "name": str(herd),
            "class": herd.connectedclass.name,
            "traits": herd.get_summary(),
        }

    return JsonResponse(summaries)


def herdsummary(request: WSGIRequest, herdID: int):
    """JSON dict of a herd summary"""

    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd)
    return JsonResponse(herd.get_summary())


@login_required
def get_herd_data(request: WSGIRequest, herdID: int):
    """JSON response of all cows in herd"""

    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd)
    return JsonResponse(herd.get_herd_dict())


@login_required
def get_bull_name(request: WSGIRequest, cowID: int):
    """Get the name if a bull from id"""

    try:
        bull = models.Bull.objects.get(id=cowID)
    except Exception:
        return JsonResponse({"name": None})

    accessible = auth_herd(request, bull.herd, error=False)
    return JsonResponse({"name": bull.name if accessible else None})


########## File requests ##########


@login_required
def get_herd_file(request: WSGIRequest, herdID: int):
    """Get XLSX file for herd"""

    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd)

    special = ["Id", "Name", "Sex", "Generation", "Sire", "Dam"]
    block = [special + [x.name for x in traits.Trait.Get_All()]]

    for cow in list(models.Bull.objects.filter(herd=herd)) + list(
        models.Cow.objects.filter(herd=herd)
    ):
        row = []
        for attr in block[0]:
            match attr:
                case "Id":
                    row.append(cow.get_sexed_id())
                case "Name":
                    row.append(cow.name)
                case "Sex":
                    row.append("male" if type(cow) is models.Bull else "female")
                case "Generation":
                    row.append(cow.generation)
                case "Sire":
                    if cow.sire:
                        row.append(cow.sire.get_sexed_id())
                    else:
                        row.append("NA")
                case "Dam":
                    if cow.dam:
                        row.append(cow.dam.get_sexed_id())
                    else:
                        row.append("NA")
                case _:
                    row.append(cow.traits.data[attr])
        block.append(row)

    output = BytesIO()

    file = excel.ExcelDoc(
        output, [f"Herd-{herd.id}"], overridename=True, in_memory=True
    )
    file.add_format("header", {"bold": True})
    file.write_block(0, block, (1, 1), "header")
    file.freeze_cells(0, (1, 0))
    file.close()

    output.seek(0)

    response = HttpResponse(
        output.read(),
    )
    response["Content-Disposition"] = f"attachment; filename={herd.name}.xlsx"

    output.close()

    return response


########## Actions -> success dict ##########


@login_required
def change_name(request: WSGIRequest, cowID: int, gender: str, name: str):
    """Change the name of a cow"""

    try:
        targetmodel = models.Bull if gender == "bull" else models.Cow

        string_validation(name, 1, 100, specialchar=" -_.")

        cow = get_object_or_404(targetmodel, id=cowID)
        auth_herd(request, cow.herd, unprotected=False)

        cow.name = name
        cow.save()
        return JSONSuccess(True)
    except:
        return JSONSuccess(False)


@login_required
def move_cow(request: WSGIRequest, cowID: int, gender: str):
    """Move an animal to class herd"""

    try:
        targetmodel = models.Bull if gender == "bulls" else models.Cow
        cow = get_object_or_404(targetmodel, id=cowID)
        auth_herd(request, cow.herd, unprotected=False)
        cow.herd = cow.herd.connectedclass.herd
        cow.name = f"[{request.user.get_full_name()}] {cow.name}"
        cow.save()
        return JSONSuccess(True)
    except:
        return JSONSuccess(False)


@login_required
def setclassinfo(request: WSGIRequest, classID: int, info: str):
    """Sets the info for a class"""

    try:
        connectedclass = models.Class.objects.get(id=classID)
        assert models.Enrollment.objects.get(
            connectedclass=connectedclass, user=request.user
        ).teacher

        connectedclass.info = info.replace("<&:slash>", "/")
        connectedclass.info = info.replace("<&:none>", "")
        connectedclass.save()
        return JSONSuccess(True)
    except:
        return JSONSuccess(False)


@login_required
def delete_enrollment(request: WSGIRequest, enrollmentID: int):
    """Unenroll user in class"""

    try:
        enrollment = models.Enrollment.objects.get(id=enrollmentID)
        user_enrollment = models.Enrollment.objects.get(
            user=request.user, connectedclass=enrollment.connectedclass
        )

        assert user_enrollment.teacher
        if enrollment.teacher:
            assert enrollment.connectedclass.owner == request.user

        enrollment.delete()
        return JSONSuccess(True)

    except:
        return JSONSuccess(False)


########## Actions -> redirect ##########
@login_required
def breed_herd(request: WSGIRequest, herdID: int):
    """Breed your herd"""

    sires = []
    for key in request.POST:
        if key[:5] == "bull-":
            sire = get_object_or_404(models.Bull, id=int(request.POST[key]))
            sires.append(sire)
            auth_herd(request, sire.herd)
    if len(sires) == 0:
        raise Http404()

    herd = models.Herd.objects.get(id=herdID)
    auth_herd(request, herd, unprotected=False)

    herd.run_breeding(sires)
    return HttpResponseRedirect(f"/openherd-{herd.id}")


@login_required
def auto_generate_herd(request: WSGIRequest):
    """Generate a random herd"""

    try:
        name = request.POST["name"]
        _class = models.Class.objects.get(id=request.POST["class"])
        enrollment = models.Enrollment.objects.get(
            connectedclass=_class, user=request.user
        )
        string_validation(name, 1, 100, allowall=True)
    except:
        return HttpResponseRedirect("/herds")

    herd = models.Herd.get_auto_generated_herd(name, _class, enrollment=enrollment)
    herd.owner = request.user
    herd.save()
    return HttpResponseRedirect(f"/openherd-{herd.id}")


@login_required
def delete_herd(request: WSGIRequest, herdID: int):
    """Delete a herd"""

    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd, unprotected=False)
    herd.delete()
    return HttpResponseRedirect("/herds")


@login_required
def delete_account(request: WSGIRequest):
    """Dissable an account"""

    if auth_password(request):
        request.user.is_active = False
        request.user.save()
        return HttpResponseRedirect("/auth/account-deleted")

    messages.error(request, "wrong-password")
    return HttpResponseRedirect("/account")
