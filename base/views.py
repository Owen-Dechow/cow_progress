from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, Http404
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from io import BytesIO
from . import models
from . import forms
from . import excel
from .models import NET_MERIT_KEY
from .resources.resources import get_resources
from .traitinfo.traitsets import TraitSet

########### Utility functions ##########


def auth_herd(
    request: WSGIRequest, herd: models.Herd, error=True, allow_class_herds=True
):
    """Authenticate a users herd acceses"""

    if allow_class_herds:
        classes = (
            [
                x.connectedclass
                for x in models.Enrollment.objects.filter(user=request.user)
            ]
            if request.user.is_authenticated
            else []
        )

        if herd.connectedclass in classes and herd.owner_id == None:
            return True

    if herd.owner_id == request.user.id:
        return True

    if error:
        raise Http404("Herd authentication failed")
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
        raise Http404("String validation failed: invalid len")

    if not allowall:
        for l in string:
            if not (l in specialchar or l.isalpha() or l.isdigit()):
                raise Http404("String validation failed: invalid char")

    return True


def JSONSuccess(success: bool):
    """Returns a success dict"""
    return JsonResponse({"successful": success})


def enrollment_or_404(request: WSGIRequest, _class):
    return get_object_or_404(
        models.Enrollment.objects.select_related("connectedclass"),
        user=request.user,
        connectedclass=_class,
    )


########## Page views ##########


def error_404_handler(request, exception):
    return render(request, "base/404.html")


def error_500_handler(request):
    return render(request, "base/500.html")


def home(request: WSGIRequest):
    """Home page"""

    enrollments = (
        models.Enrollment.objects.filter(user=request.user)
        if request.user.is_authenticated
        else []
    )
    args = {"resources": get_resources(), "enrollments": enrollments}
    return render(request, "base/home.html", args)


@login_required
@transaction.atomic
def new_class(request: WSGIRequest):
    if request.method == "POST":
        form = forms.AddClass(request.POST)
        if form.is_valid():
            enrollment = form.save(request.user)
            return HttpResponseRedirect(f"/class/{enrollment.connectedclass.id}")
    else:
        form = forms.AddClass()

    return render(request, "base/new_class.html", {"form": form})


@login_required
@transaction.atomic
def join_class(request: WSGIRequest):
    if request.method == "POST":
        form = forms.JoinClass(request.POST)
        if form.is_valid(request.user):
            enrollment = form.save(request.user)
            return HttpResponseRedirect(f"/class/{enrollment.connectedclass.id}")
    else:
        form = forms.JoinClass()

    return render(request, "base/join_class.html", {"form": form})


@login_required
@transaction.atomic
@require_POST
@csrf_protect
def update_class(request: WSGIRequest, class_id: int):
    enrollment = enrollment_or_404(request, class_id)

    if not enrollment.teacher:
        raise Http404("User does not have permission to update class")

    connectedclass = enrollment.connectedclass
    connectedclass.info = request.POST.get("classinfo", "~")

    maxgen = request.POST.get("maxgen", "~")
    if not maxgen.isdigit():
        maxgen = 1
    connectedclass.breeding_limit = maxgen

    for trait in connectedclass.viewable_traits:
        connectedclass.viewable_traits[trait] = "trait-" + trait in request.POST

    for rec in connectedclass.viewable_recessives:
        connectedclass.viewable_recessives[rec] = "rec-" + rec in request.POST

    connectedclass.save()

    return HttpResponseRedirect(f"/class/{connectedclass.id}/")


@login_required
@transaction.atomic
@require_POST
@csrf_protect
def delete_class(request: WSGIRequest, class_id: int):
    enrollment = enrollment_or_404(request, class_id)
    if request.user != enrollment.connectedclass.owner:
        raise Http404("User does not have permission to delete class.")

    enrollment.connectedclass.delete()

    return HttpResponseRedirect("/")


@login_required
@transaction.atomic
@require_POST
@csrf_protect
def exit_class(request: WSGIRequest, class_id: int):
    enrollment = enrollment_or_404(request, class_id)
    if request.user == enrollment.connectedclass.owner:
        raise Http404("Owner cannot exit class")

    enrollment.delete()

    return HttpResponseRedirect("/")


@login_required
def open_class(request: WSGIRequest, class_id: int):
    enrollment = get_object_or_404(
        models.Enrollment, connectedclass=class_id, user=request.user
    )
    _class = get_object_or_404(models.Class, id=class_id)
    members = models.Enrollment.objects.filter(connectedclass=_class)

    return render(
        request,
        "base/class.html",
        {"class": _class, "members": members, "enrollment": enrollment},
    )


@transaction.atomic
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


@transaction.atomic
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


@transaction.atomic
@login_required
def herds(request: WSGIRequest, class_id: int):
    """Your herds page"""

    enrollment = enrollment_or_404(request, class_id)

    return render(
        request,
        "base/herds.html",
        {
            "enrollment": enrollment,
            "class": enrollment.connectedclass,
            "maxlen": models.Herd._meta.get_field("name").max_length,
        },
    )


@transaction.atomic
@login_required
def open_herd(request: WSGIRequest, class_id: int, herd_id: int):
    """View herd page"""

    enrollment = enrollment_or_404(request, class_id)
    herd = get_object_or_404(
        models.Herd.objects.select_related("connectedclass__herd"),
        id=herd_id,
        connectedclass=enrollment.connectedclass,
    )
    auth_herd(request, herd, allow_class_herds=True)

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
            "enrollment": enrollment,
            "class": enrollment.connectedclass,
        },
    )


@transaction.atomic
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
        formid = request.POST["formid"]
        form = view_forms[formid](request.POST)
        view_forms[formid] = form

        if form.is_valid(request.user):
            form.save(request.user)
            form.data = dict()

    enrollments = models.Enrollment.objects.filter(user=request.user)
    enrollment_info = {}

    for e in enrollments:
        enrollment_info[e] = list(
            models.Enrollment.objects.prefetch_related("user").filter(
                connectedclass=e.connectedclass
            )
        )
    return render(
        request,
        "base/classes.html",
        view_forms | {"enrollmentinfo": enrollment_info},
    )


@login_required
def recessives(request: WSGIRequest, class_id: int):
    enrollment = enrollment_or_404(request, class_id)
    args = {"recessives": TraitSet(enrollment.connectedclass.traitset).recessives}
    return render(request, "base/recessives.html", args)


@login_required
def pedigree(request: WSGIRequest, class_id: int, animal_id: int):
    enrollment = enrollment_or_404(request, class_id)
    animal = get_object_or_404(
        models.Bovine, id=animal_id, connectedclass=enrollment.connectedclass
    )

    return render(request, "base/pedigree.html", {"animal": animal})


@login_required
def get_pedigree(request: WSGIRequest, class_id: int, animal_id: int):
    enrollment = enrollment_or_404(request, class_id)
    animal = get_object_or_404(
        models.Bovine, id=animal_id, connectedclass=enrollment.connectedclass
    )
    return JsonResponse(animal.pedigree)


def cookies(request: WSGIRequest):
    return render(request, "base/cookies.html")


def app_credits(request: WSGIRequest):
    return render(request, "base/credits.html")


########## JSON requests ##########
@login_required
def herdsummaries(request: WSGIRequest, class_id: int):
    """JSON dict of all accessable herd summaries"""

    enrollment = enrollment_or_404(request, class_id)
    public_herds = [
        enrollment.connectedclass.publicherd,
        enrollment.connectedclass.herd,
    ]

    private_herds = models.Herd.objects.filter(
        connectedclass=enrollment.connectedclass, owner=request.user
    )

    summaries = {"public": {}, "private": {}}

    for herd in public_herds:
        summaries["public"][herd.id] = {
            "name": herd.name,
            "class": "",
            "traits": herd.get_summary(),
        }

    for herd in private_herds:
        summaries["private"][herd.id] = {
            "name": herd.name,
            "class": herd.connectedclass.name,
            "traits": herd.get_summary(),
        }

    return JsonResponse(summaries)


def herdsummary(request: WSGIRequest, class_id: int, herd_id: int):
    """JSON dict of a herd summary"""

    enrollment = enrollment_or_404(request, class_id)
    herd = get_object_or_404(
        models.Herd, id=herd_id, connectedclass=enrollment.connectedclass
    )
    auth_herd(request, herd, allow_class_herds=True)
    return JsonResponse(herd.get_summary())


@login_required
def herddata(request: WSGIRequest, class_id: int, herd_id: int):
    """JSON response of all cows in herd"""

    enrollment = enrollment_or_404(request, class_id)
    herd = get_object_or_404(
        models.Herd, id=herd_id, connectedclass=enrollment.connectedclass
    )
    auth_herd(request, herd, allow_class_herds=True)
    herd_dict = herd.get_herd_dict()
    return JsonResponse(herd_dict)


@login_required
def get_bull_name(request: WSGIRequest, class_id: int, bull_id: int):
    """Get the name if a bull from id"""

    enrollment = enrollment_or_404(request, class_id)
    bull_queryset = models.Bovine.objects.filter(id=bull_id, male=True)

    if len(bull_queryset) != 1:
        return JsonResponse({"name": None})

    bull = bull_queryset[0]

    if not auth_herd(request, bull.herd, error=False, allow_class_herds=True):
        return JsonResponse({"name": None})

    if bull.herd.connectedclass != enrollment.connectedclass:
        return JsonResponse({"name": None})

    return JsonResponse({"name": bull.name})


@login_required
def get_cow_data(request: WSGIRequest, class_id: int, animal_id: int):
    enrollment = enrollment_or_404(request, class_id)

    try:
        animal = models.Bovine.objects.get(
            id=animal_id, connectedclass=enrollment.connectedclass
        )
    except:
        return JSONSuccess(False)

    if auth_herd(request, animal.herd, error=False, allow_class_herds=True):
        return JsonResponse({"successful": True} | animal.get_dict())
    else:
        return JSONSuccess(False)


########## File requests ##########


@login_required
def get_herd_file(request: WSGIRequest, class_id: int, herd_id: int):
    """Get XLSX file for herd"""

    enrollment = enrollment_or_404(request, class_id)
    herd = get_object_or_404(
        models.Herd.objects.select_related("connectedclass"), id=herd_id
    )
    auth_herd(request, herd, allow_class_herds=True)

    animals = models.Bovine.objects.filter(herd=herd)
    connectedclass = herd.connectedclass
    traitset = TraitSet(herd.connectedclass.traitset)

    model_row = (
        [
            "Name",
            "Id",
            "Generation",
            "Sex",
            "Sire",
            "Dam",
            "Inbreeding Coefficient",
            NET_MERIT_KEY,
        ]
        + [x.name for x in traitset.traits if connectedclass.viewable_traits[x.name]]
        + [
            f"ph: {x.name}"
            for x in traitset.traits
            if connectedclass.viewable_traits[x.name]
        ]
        + [
            x.name
            for x in traitset.recessives
            if connectedclass.viewable_recessives[x.name]
        ]
    )

    block = [model_row]

    for animal in animals:
        block.append(animal.get_XLSX_row(model_row))

    with BytesIO() as output:
        file = excel.ExcelDoc(output, ["Sheet1"], overridename=True, in_memory=True)
        file.add_format("header", {"bold": True})
        file.write_block(0, block, (1, 1), "header")
        file.freeze_cells(0, (1, 0))
        file.close()

        output.seek(0)

        response = HttpResponse(output.read())
        response["Content-Type"] = "application/vnd.ms-excel"
        response["Content-Disposition"] = (
            f"attachment; filename={slugify(herd.name)}.xlsx"
        )

        output.close()
        return response


@login_required
def get_class_tendchart(request: WSGIRequest, class_id: int):
    """Get XLSX trend file"""

    connectedclass = get_object_or_404(models.Class, id=class_id)

    # Authenticate user enrollment
    enrollment_or_404(request, class_id)

    row1 = [x for x in connectedclass.trend_log["Initial Population"]]
    block = [row1]

    for row_id, row_info in connectedclass.trend_log.items():
        row = []
        for key in row1:
            row.append(row_info[key])

        block.append(row)

    with BytesIO() as output:
        file = excel.ExcelDoc(output, [f"Sheet1"], overridename=True, in_memory=True)
        file.add_format("header", {"bold": True})
        file.write_block(0, block, (1, 1), "header")
        file.freeze_cells(0, (1, 0))
        file.close()

        output.seek(0)

        response = HttpResponse(output.read())
        response["Content-Type"] = "application/vnd.ms-excel"
        response["Content-Disposition"] = (
            f"attachment; filename={slugify(connectedclass.name)}_trends.xlsx"
        )

        output.close()

        return response


@login_required
def get_class_datafile(request: WSGIRequest, class_id: int):
    enrollment = enrollment_or_404(request, class_id)

    animals = list(
        models.Bovine.objects.select_related("herd").filter(connectedclass=class_id)
    )
    traitset = TraitSet(enrollment.connectedclass.traitset)

    row_model = (
        [
            "Name",
            "Id",
            "Herd",
            "Generation",
            "Sex",
            "Sire",
            "Dam",
            "Inbreeding Coefficient",
            NET_MERIT_KEY,
        ]
        + [x.name for x in traitset.traits]
        + [f"ph: {x.name}" for x in traitset.traits]
        + [x.name for x in traitset.recessives]
    )

    block = [row_model]
    for animal in animals:
        block.append(animal.get_XLSX_row(row_model))

    with BytesIO() as output:
        file = excel.ExcelDoc(output, [f"Sheet1"], overridename=True, in_memory=True)
        file.add_format("header", {"bold": True})
        file.write_block(0, block, (1, 1), "header"),
        file.freeze_cells(0, (1, 0))
        file.close()

        output.seek(0)

        response = HttpResponse(output.read())
        response["Content-Type"] = "application/vnd.ms-excel"
        response["Content-Disposition"] = (
            f"attachment; filename={slugify(enrollment.connectedclass.name)}_data.xlsx"
        )

        output.close()
        return response


########## Actions -> success dict ##########


@transaction.atomic
@login_required
def rename(
    request: WSGIRequest, class_id: int, herd_id: int, animal_id: int, name: str
):
    """Change the name of a cow"""

    try:
        enrollment = enrollment_or_404(request, class_id)
        string_validation(name, 1, 100, specialchar=" -_.'")

        animal = get_object_or_404(
            models.Bovine,
            id=animal_id,
            herd=herd_id,
            connectedclass=enrollment.connectedclass,
        )
        auth_herd(request, animal.herd, allow_class_herds=False)

        animal.name = name
        animal.save()
        return JSONSuccess(True)
    except:
        return JSONSuccess(False)


@transaction.atomic
@login_required
def move_animal(request: WSGIRequest, class_id: int, herd_id: int, animal_id: int):
    """Move an animal to class herd"""

    try:
        enrollment = enrollment_or_404(request, class_id)
        animal = get_object_or_404(models.Bovine, id=animal_id, herd=herd_id)
        auth_herd(request, animal.herd, allow_class_herds=False)
        animal.herd = enrollment.connectedclass.herd
        animal.name = f"[{request.user.get_full_name()}] {animal.name}"
        animal.save()
        return JSONSuccess(True)
    except:
        return JSONSuccess(False)


########## Actions -> redirect ##########
@transaction.atomic
@login_required
def breed_herd(request: WSGIRequest, class_id: int, herd_id: int):
    """Breed your herd"""

    enrollment = enrollment_or_404(request, class_id)
    herd = get_object_or_404(
        models.Herd.objects.select_related("connectedclass"), id=herd_id
    )
    auth_herd(request, herd, allow_class_herds=False)

    sires = []
    for key in request.POST:
        if key[:5] == "bull-":
            sire = get_object_or_404(
                models.Bovine.objects.prefetch_related("herd", "herd__connectedclass"),
                id=int(request.POST[key]),
                male=True,
            )
            sires.append(sire)
            auth_herd(request, sire.herd, allow_class_herds=True)

            if sire.herd.connectedclass != herd.connectedclass:
                raise Http404("Bull outside of class")

    if len(sires) == 0:
        raise Http404("No bull labeled")

    if herd.breedings >= herd.connectedclass.breeding_limit:
        raise Http404("Max breeding limit reached")

    deaths = herd.run_breeding(sires)
    herd.connectedclass.update_trend_log(
        f"{request.user.get_full_name()} [{request.user.username}] {herd.name}: {herd.breedings}"
    )

    messages.info(request, f"deaths:{deaths}")
    return HttpResponseRedirect(
        f"/class/{enrollment.connectedclass.id}/herds/{herd.id}/"
    )


@transaction.atomic
@login_required
def auto_generate_herd(request: WSGIRequest, class_id: int):
    """Generate a random herd"""

    form = forms.AutoGenerateHerd(request.POST)
    if not form.is_valid():
        raise Http404("Invalid create herd form")

    enrollment = enrollment_or_404(request, class_id)

    herd, animals = models.Herd.get_auto_generated_herd(
        form.cleaned_data["name"], enrollment.connectedclass, enrollment=enrollment
    )
    herd.owner = request.user
    herd.save()

    for animal in animals:
        animal.name = animal.auto_generate_name(herd)
        animal.pedigree = animal.auto_generate_pedigree()
    models.Bovine.objects.bulk_update(animals, ["name", "pedigree"])

    enrollment.connectedclass.update_trend_log(
        f"{request.user.get_full_name()} [{request.user.get_full_name()}] created: {herd.name}"
    )

    return HttpResponseRedirect(
        f"/class/{enrollment.connectedclass.id}/herds/{herd.id}/"
    )


@transaction.atomic
@login_required
def delete_herd(request: WSGIRequest, class_id: int, herd_id: int):
    """Delete a herd"""

    enrollment = enrollment_or_404(request, class_id)
    herd = get_object_or_404(models.Herd, id=herd_id)
    auth_herd(request, herd, allow_class_herds=False)
    herd.delete()
    return HttpResponseRedirect(f"/class/{enrollment.connectedclass.id}/herds/")


@transaction.atomic
@login_required
def delete_account(request: WSGIRequest):
    """Dissable an account"""

    if auth_password(request):
        request.user.is_active = False
        request.user.save()
        return HttpResponseRedirect("/auth/account-deleted")

    messages.error(request, "wrong-password")
    return HttpResponseRedirect("/account")
