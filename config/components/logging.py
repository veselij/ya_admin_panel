import logging
import os

LOGSTASH_HOST = os.environ.get("LOGSTASH_HOST", "127.0.0.1")
LOGSTASH_PORT = os.environ.get("LOGSTASH_PORT", 5044)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if "X-Request-ID" in record.request.headers:
            record.request_id = record.request.headers["X-Request-ID"]
        else:
            record.request_id = "none"
        return True


LOGGING = {
    "version": 1,
    "filters": {
        "custom_filter": {
            "()": RequestIdFilter,
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "logstash": {
            "level": "INFO",
            "class": "logstash.LogstashHandler",
            "filters": ["custom_filter"],
            "host": LOGSTASH_HOST,
            "port": LOGSTASH_PORT,
            "version": 1,
            "message_type": "logstash",
            "fqdn": False,
            "tags": ["admin"],
        },
    },
    "loggers": {
        "gunicorn.accesslog": {"level": "INFO", "handlers": ["logstash"]},
        "gunicorn.errorlog": {"level": "INFO", "handlers": ["logstash"]},
    },
    "root": {"level": "INFO", "handlers": ["logstash"]},
}
