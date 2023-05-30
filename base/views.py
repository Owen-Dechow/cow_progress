from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.text import slugify
from django.contrib import messages
from .traitinfo import traits
from .resources.resources import get_resources
from io import BytesIO
from . import models
from . import forms
from . import excel


########### Utility functions ##########


def auth_herd(
    request: WSGIRequest, herd: models.Herd, error=True, use_class_herds=True
):
    """Authenticate a users herd acceses"""

    if use_class_herds:
        classes = (
            [
                x.connectedclass
                for x in models.Enrollment.objects.filter(user=request.user)
            ]
            if request.user.is_authenticated
            else []
        )

        if herd.connectedclass in classes and herd.owner == None:
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


def error_404_handler(request, exception):
    return render(request, "base/404.html")


def error_500_handler(request):
    return render(request, "base/500.html")


def home(request: WSGIRequest):
    """Home page"""

    args = {"resources": get_resources()}
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

    if herd.connectedclass.herd == herd:
        herdstatus = "Class"
    elif herd.owner is None:
        herdstatus = "Public"
    else:
        herdstatus = "Private"

    deaths = None
    for message in messages.get_messages(request):
        if "deaths:" in str(message):
            deaths = int(str(message).split(":")[1])

    return render(
        request,
        "base/open_herd.html",
        {
            "herd": herd,
            "herdstatus": herdstatus,
            "deaths": deaths,
        },
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
        "updateclass": forms.UpdateClass,
    }

    if request.method == "POST":
        try:
            formid = request.POST["formid"]
            form = view_forms[formid](request.POST)
            view_forms[formid] = form

            if form.is_valid(request.user):
                form.save(request.user)

            return HttpResponseRedirect("/classes")
        except:
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


def pedigree(request: WSGIRequest):
    animal_id = -1
    data_id = -1

    if "animal_id" in request.GET:
        try:
            animal_id = int(request.GET["animal_id"])
        except:
            animal_id = float("inf")

        try:
            data_id = models.Pedigree.objects.get(animal_id=animal_id).id
        except:
            data_id = -1

    return render(
        request,
        "base/pedigree.html",
        {"animal_id": animal_id, "data_id": data_id},
    )


def cookies(request: WSGIRequest):
    return render(request, "base/cookies.html")


def app_credits(request: WSGIRequest):
    return render(request, "base/credits.html")


########## JSON requests ##########
@login_required
def traitnames(request: WSGIRequest):
    """JSON dict of all trait names"""

    traitdict = {}

    traitdict["Net Merit"] = 0

    for trait in traits.Trait.get_all():
        traitdict[trait.name] = trait.net_merit_dollars

    return JsonResponse(traitdict)


@login_required
def herdsummaries(request: WSGIRequest):
    """JSON dict of all accessable herd summaries"""

    privateherdlist = models.Herd.objects.filter(owner=request.user)

    publicherdlist = []
    for enrollment in models.Enrollment.objects.filter(user=request.user):
        connectedclass = enrollment.connectedclass
        publicherdlist.append(connectedclass.herd)
        publicherdlist.append(connectedclass.publicherd)

    summaries = {"public": {}, "private": {}, "class": {}}

    for herd in publicherdlist:
        summaries["public"][herd.id] = {
            "name": herd.name,
            "class": "",
            "traits": herd.get_summary(),
        }

    for herd in privateherdlist:
        summaries["private"][herd.id] = {
            "name": herd.name,
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
        animal = models.Bovine.objects.get(id=cowID)
        assert animal.male
        assert auth_herd(request, animal.herd, error=False)
        assert animal.herd.connectedclass == animal.herd.connectedclass
    except:
        return JsonResponse({"name": None})

    return JsonResponse({"name": animal.name})


def get_pedigree(request: WSGIRequest, pedigreeID: int):
    pedigree = get_object_or_404(models.Pedigree, id=pedigreeID)
    return JsonResponse(pedigree.get_as_dict())


@login_required
def get_cow_data(request: WSGIRequest, cowID: int):
    try:
        animal = models.Bovine.objects.get(id=cowID)
    except:
        return JSONSuccess(False)

    can_give_data = auth_herd(request, animal.herd, False)

    if can_give_data:
        return JsonResponse({"successful": True} | animal.get_dict())
    else:
        return JSONSuccess(False)


########## File requests ##########


@login_required
def get_herd_file(request: WSGIRequest, herdID: int):
    """Get XLSX file for herd"""

    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd)

    row1 = []
    animals = models.Bovine.objects.filter(herd=herd)
    for key, val in animals[0].get_dict().items():
        if key == "traits":
            for traitkey in val:
                row1.append(traitkey)
        elif key == "recessives":
            for traitkey in val:
                row1.append(traitkey)
        else:
            row1.append(key)

    block = [row1]
    row1[0] = "Name"

    for animal in animals:
        row = []
        for key, val in animal.get_dict().items():
            if key == "traits":
                for traitkey, traitval in val.items():
                    row.append(traitval)
            elif key == "recessives":
                for traitkey, traitval in val.items():
                    if traitval == 0:
                        realval = "--"
                    elif traitval == 1:
                        realval = "-+"
                    else:
                        realval = "++"
                    row.append(realval)
            else:
                row.append(val)

        block.append(row)

    output = BytesIO()

    file = excel.ExcelDoc(output, ["Sheet1"], overridename=True, in_memory=True)
    file.add_format("header", {"bold": True})
    file.write_block(0, block, (1, 1), "header")
    file.freeze_cells(0, (1, 0))
    file.close()

    output.seek(0)

    response = HttpResponse(
        output.read(),
    )
    response["Content-Disposition"] = f"attachment; filename={slugify(herd.name)}.xlsx"

    output.close()

    return response


@login_required
def get_class_tendchart(request: WSGIRequest, classID: int):
    """Get XLSX trend file"""

    connectedclass = get_object_or_404(models.Class, id=classID)

    # Authenticate user enrollment
    get_object_or_404(
        models.Enrollment, connectedclass=connectedclass, user=request.user
    )

    row1 = ["Action ID"]
    block = [row1]

    for key in connectedclass.trend_log["Initial Population"]:
        row1.append(key)

    for row_id, row_info in connectedclass.trend_log.items():
        row = [row_id]
        for key in row1[1:]:
            row.append(row_info[key])

        block.append(row)

    output = BytesIO()

    file = excel.ExcelDoc(output, [f"Sheet1"], overridename=True, in_memory=True)
    file.add_format("header", {"bold": True})
    file.write_block(0, block, (1, 1), "header")
    file.freeze_cells(0, (1, 0))
    file.close()

    output.seek(0)

    response = HttpResponse(
        output.read(),
    )
    response[
        "Content-Disposition"
    ] = f"attachment; filename={slugify(connectedclass.name)}.xlsx"

    output.close()

    return response


########## Actions -> success dict ##########


@login_required
def change_name(request: WSGIRequest, cowID: int, name: str):
    """Change the name of a cow"""

    try:
        string_validation(name, 1, 100, specialchar=" -_.'")

        animal = get_object_or_404(models.Bovine, id=cowID)
        auth_herd(request, animal.herd, use_class_herds=False)

        animal.name = name
        animal.save()
        return JSONSuccess(True)
    except:
        return JSONSuccess(False)


@login_required
def move_cow(request: WSGIRequest, cowID: int):
    """Move an animal to class herd"""

    try:
        animal = get_object_or_404(models.Bovine, id=cowID)
        auth_herd(request, animal.herd, use_class_herds=False)
        animal.herd = animal.herd.connectedclass.herd
        animal.name = f"[{request.user.get_full_name()}] {animal.name}"
        animal.save()
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
    """Un-enroll user in class"""

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
    
    herd = get_object_or_404(models.Herd, id=herdID)
    auth_herd(request, herd, use_class_herds=False)

    sires = []
    for key in request.POST:
        if key[:5] == "bull-":
            sire = get_object_or_404(
                models.Bovine, id=int(request.POST[key]), male=True
            )
            sires.append(sire)
            auth_herd(request, sire.herd)

            if sire.herd.connectedclass != herd.connectedclass:
                raise Http404()

    if len(sires) == 0:
        raise Http404()


    if herd.breedings >= herd.connectedclass.breeding_limit:
        raise Http404()

    deaths = herd.run_breeding(sires)
    herd.connectedclass.update_trend_log(
        f"{request.user.get_full_name()} [{request.user.username}] {herd.name}: {herd.breedings}"
    )

    messages.info(request, f"deaths:{deaths}")
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
    auth_herd(request, herd, use_class_herds=False)
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
