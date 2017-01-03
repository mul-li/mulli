import pickle
import random
import itertools

from datetime import date, timedelta, MAXYEAR
from zlib import adler32

from flask import current_app
from werkzeug.routing import BaseConverter, ValidationError
from celery import current_app as celery_app
from celery import Task


class HexConverter(BaseConverter):

    def __init__(self, map) -> None:
        super().__init__(map)

    def to_python(self, value: str) -> int:
        try:
            return int(value, base=16)
        except ValueError:
            raise ValidationError()

    def to_url(self, value: int) -> str:
        return hex(value)[2:]


class AppContextTask(Task):

    abstract = True

    def __call__(self, *args, **kwargs):
        with self.app.flask_app.app_context():
            return super().__call__(self, *args, **kwargs)


def int_to_bytes(integer: int) -> bytes:
    return integer.to_bytes((integer.bit_length() // 8) + 1, 'little')


def load_database() -> dict:
    try:
        with open(current_app.config['DATABASE'], mode='rb') as f:
            return pickle.load(f)
    except (EOFError, FileNotFoundError, pickle.UnpicklingError):
        return {}


def save_database(database: dict) -> None:
    try:
        with open(current_app.config['DATABASE'], mode='wb') as f:
            pickle.dump(database, f)
    except Exception as e:
        raise RuntimeError from e


def create_id(input: str) -> int:
    database = load_database()
    h = adler32(input.encode('utf-8'))
    for _ in itertools.repeat(None, h):
        r = int_to_bytes(random.randint(1, h))
        h = adler32(r, h)
        if h not in database:
            return h
    raise ValueError


def is_expired(entry: dict) -> bool:
    return date.today() > entry['expire']


def add_entry(id: int, entry: dict, valid: int) -> dict:
    valid = int(valid)
    if valid == -1:
        expire = date(MAXYEAR, 12, 31)
    else:
        expire = date.today() + timedelta(valid)
    entry['expire'] = expire
    database = load_database()
    database[id] = entry
    save_database(database)
    remove_entry.apply_async(args=[id], eta=expire)
    return database


def load_entry(id: int) -> dict:
    database = load_database()
    try:
        entry = database[id]
    except KeyError:
        raise
    else:
        if is_expired(entry):
            raise ValueError
    return entry


@celery_app.task
def remove_entry(id: int) -> None:
    database = load_database()
    del database[id]
    save_database(database)


def make_celery(flask_app, celery_config):
    celery_app.conf.update(celery_config)
    celery_app.Task = AppContextTask

    if not hasattr(celery_app, 'flask_app'):
        celery_app.flask_app = flask_app
