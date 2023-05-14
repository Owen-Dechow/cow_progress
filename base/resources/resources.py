from django.conf import settings

RELPATH = settings.BASE_DIR / "base/resources/"


class Resource:
    def __init__(self, title, url):
        self.title = title
        self.link = url


def get_resources():
    resources = []

    with open(RELPATH / "resources.txt") as f:
        for line in f.readlines():
            data = line.strip().removesuffix("\n").split("==")
            if data:
                resources.append(Resource(data[0], data[1]))

    return resources
