from django.template.defaulttags import register
from django.utils.html import mark_safe


class PathComponent:
    def __init__(self, component) -> None:
        self.component = component
        if len(component) > 0:
            self.verbose_component = component[0].upper() + component[1:]
        else:
            self.verbose_component = ""

    def __str__(self):
        return self.verbose_component + f" ({self.component})"

    @classmethod
    def join_components(cls, verbose_component, components):
        new = PathComponent("/".join([x.component for x in components]))
        new.verbose_component = verbose_component
        return new

    @classmethod
    def get_a_tag(cls, components):
        classes = "as-link"
        href = ""
        for component in components:
            href += component.component + "/"

        return f"<a class='{classes}' href='{href}'>{components[-1].verbose_component}/</a> "


@register.simple_tag(takes_context=True)
def navpath(context):

    base_component = PathComponent("")
    base_component.verbose_component = "Cow Progress"

    path = [base_component] + [
        PathComponent(x) for x in context["request"].path.split("/") if x
    ]
    simplify_path(path, context)

    a_tags = ""
    for idx in range(len(path)):
        a_tags += PathComponent.get_a_tag(path[: idx + 1])

    return mark_safe(a_tags)


def simplify_path(path: list[str], context):
    simplifications = {
        (lambda x: x == "class", lambda x: x.isdigit()): lambda: "Class: "
        + context["class"].name,
        (lambda x: x == "herds", lambda x: x.isdigit()): lambda: "Herd: "
        + context["herd"].name,
        (lambda x: x == "pedigree", lambda x: x.isdigit()): lambda: "Pedigree: "
        + context["animal"].id.__str__(),
        (lambda x: x == "auth", lambda x: x == "login"): lambda: "Login",
        (lambda x: x == "auth", lambda x: x == "register"): lambda: "Register",
        (
            lambda x: x == "auth",
            lambda x: x == "account-deleted",
        ): lambda: "Account Deleted",
        (
            lambda x: x == "auth",
            lambda x: x == "password-change",
        ): lambda: "Password Change",
        (
            lambda x: x == "auth",
            lambda x: x == "password-reset",
        ): lambda: "Reset Password",
        (
            lambda x: x == "confirm",
            lambda x: x == "MQ",
            lambda x: x == "set-password",
        ): lambda: "Confirm",
    }

    for matchers, resolver in simplifications.items():
        idx = 0
        while idx + len(matchers) <= len(path):
            is_matching = all(
                match(
                    path[idx + match_idx].component
                    if type(path[idx + match_idx]) is PathComponent
                    else path[idx + match_idx]
                )
                for match_idx, match in enumerate(matchers)
            )
            if is_matching:
                path_slice = slice(idx, idx + len(matchers))
                new_component = PathComponent.join_components(
                    resolver(), path[path_slice]
                )
                path[path_slice] = [new_component]
                idx -= len(matchers)

            idx += 1
