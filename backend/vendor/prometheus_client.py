"""
Prometheus client shim for backward compatibility.

Provides stub implementations when prometheus_client is not installed.
"""


class Counter:
    def __init__(self, *args, **kwargs):
        pass

    def labels(self, **kwargs):
        return self

    def inc(self, *args, **kwargs):
        pass


class Histogram:
    def __init__(self, *args, **kwargs):
        pass

    def labels(self, **kwargs):
        return self

    def observe(self, *args, **kwargs):
        pass

    def time(self):
        return self


class Gauge:
    def __init__(self, *args, **kwargs):
        pass

    def labels(self, **kwargs):
        return self

    def inc(self, *args, **kwargs):
        pass

    def dec(self, *args, **kwargs):
        pass

    def set(self, *args, **kwargs):
        pass


def generate_latest():
    return b""


CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
