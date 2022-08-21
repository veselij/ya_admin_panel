import json

import requests
from django.http.response import JsonResponse
from requests import ConnectionError, ConnectTimeout, HTTPError

from billing.utils.backoff import backoff
from billing.utils.exceptions import RetryExceptionError
from config import settings


def check_token(func):
    def wrapper(request, *args, **kwargs):
        token = request.get("Authorization", None)
        if token and verify_token_in_auth(token):
            return func(request, *args, **kwargs)
        return JsonResponse({}, status=401)

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
        raise RetryExceptionError("Auth server is not available")
    except HTTPError:
        return False
    return True
