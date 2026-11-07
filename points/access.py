import hmac
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect


SESSION_ACCESS_KEY = "shared_code_valid"


def shared_code_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.session.get(SESSION_ACCESS_KEY):
            return view(request, *args, **kwargs)
        return redirect("access")

    return wrapped


def access_code_matches(submitted_code):
    configured_code = settings.ACCESS_CODE
    return bool(configured_code) and hmac.compare_digest(
        str(submitted_code), configured_code
    )
