import contextlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Type
from uuid import uuid4

from decouple import Csv, config
from django.conf import settings
from django.core import management
from django.http import HttpResponse
from django.urls import include, path
from django.utils import module_loading

from carladam import PetriNet


def configure(**kwargs):
    params = dict(
        ALLOWED_HOSTS=config("ALLOWED_HOSTS", default="*", cast=Csv()),
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            },
        },
        DEBUG=config("DEBUG", default=True),
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        INSTALLED_APPS=["carladam.django.petrinet_simulator"],
        ROOT_URLCONF=__name__,
        SECRET_KEY=config("SECRET_KEY", default="SECRET"),
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                    ],
                },
            },
        ],
    )
    return settings.configure(**params, **kwargs)


def home(request):
    return HttpResponse("Welcome!")


urlpatterns = [
    path("", include("carladam.django.petrinet_simulator.urls")),
]


def is_petrinet_subclass(obj: Any) -> bool:
    return isinstance(obj, type) and issubclass(obj, PetriNet)


def main():
    configure()

    petrinets: Dict[str, PetriNet] = {}
    settings.CARLADAM_SIMULATOR_PETRINETS = petrinets

    arg0, *args = sys.argv

    if "--" in args:
        separator_index = args.index("--")
        runserver_args, simulator_args = args[:separator_index], args[separator_index + 1 :]
    else:
        runserver_args, simulator_args = [], args

    for arg in simulator_args:
        with contextlib.suppress(ImportError, ValueError):
            petrinet_cls = module_loading.import_string(arg)
            if is_petrinet_subclass(petrinet_cls):
                petrinets[petrinet_cls.__name__] = petrinet_cls.new()
                continue
        arg_path = Path(arg)
        if not arg_path.exists():
            print(f"Warning: Could not find {arg_path!r}")
            continue
        if arg_path.is_dir():
            paths = arg_path.glob("**/*.py")
        elif arg_path.suffix != ".py":
            print(f"Warning: Not a Python module {arg_path!r}")
            continue
        else:
            paths = [arg_path]
        for module_path in sorted(paths):
            with contextlib.suppress(ImportError):
                # cf. https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
                module_name = f"__{uuid4().hex}__"
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                for key in sorted(dir(module)):
                    petrinet_cls: Type[PetriNet] = getattr(module, key)
                    if petrinet_cls is PetriNet:
                        continue
                    if not is_petrinet_subclass(petrinet_cls):
                        continue
                    petrinets[petrinet_cls.__name__] = petrinet_cls.new()

    print("")
    print("PetriNet classes loaded:")
    print("\n".join(f"- {key}" for key in sorted(petrinets)))
    print("")

    management.execute_from_command_line([arg0, "runserver", *runserver_args])


if __name__ == "__main__":
    main()
