import json

import requests
from django.http.response import JsonResponse
from requests import ConnectionError, ConnectTimeout, HTTPError

from billing.utils import errormessages
from billing.utils.backoff import backoff
from billing.utils.exceptions import RetryExceptionError
from config import settings


def check_token(func):
    def wrapper(request, *args, **kwargs):
        if settings.AUTH_ENABLED:
            token = request.POST.get("Authorization", None)
            if token and verify_token_in_auth(token):
                return func(request, *args, **kwargs)
            return JsonResponse({}, status=401)
        else:
            return func(request, *args, **kwargs)

    return wrapper


@backoff(
    settings.logger,
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
    max_retray=2,
)
def verify_token_in_auth(token):
    token = token.split(" ")[1]

    try:
        r = requests.post(settings.AUTH_URL, data=json.dumps({"access_token": token}))
        r.raise_for_status()
    except (ConnectTimeout, ConnectionError):
        raise RetryExceptionError(errormessages.AUTH)
    except HTTPError:
        return False
    return True
