from .settings import INDOCKER

if INDOCKER:
    from .celery import app as celery_app
    __all__ = ('celery_app',)