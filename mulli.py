import pickle
import random
import itertools

from datetime import date, timedelta, MAXYEAR
from zlib import adler32

from werkzeug.routing import BaseConverter, ValidationError


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


def int_to_bytes(integer: int) -> bytes:
    return integer.to_bytes((integer.bit_length() // 8) + 1, 'little')


def load_database(filename: str) -> dict:
    try:
        with open(filename, mode='rb') as f:
            return pickle.load(f)
    except (EOFError, FileNotFoundError, pickle.UnpicklingError):
        return {}


def save_database(database: dict, filename: str) -> None:
    try:
        with open(filename, mode='wb') as f:
            pickle.dump(database, f)
    except Exception as e:
        raise RuntimeError from e


def create_id(input: str, database: dict) -> int:
    h = adler32(input.encode('utf-8'))
    for _ in itertools.repeat(None, h):
        r = int_to_bytes(random.randint(1, h))
        h = adler32(r, h)
        if h not in database:
            return h
    raise ValueError


def is_expired(entry: dict) -> bool:
    return date.today() > entry['expire']


def add_entry(id: int, entry: dict, valid: int, database: dict) -> dict:
    valid = int(valid)
    if valid == -1:
        expire = date(MAXYEAR, 12, 31)
    else:
        expire = date.today() + timedelta(valid)
    entry['expire'] = expire
    database[id] = entry
    return database


def load_entry(id: int, database: dict) -> dict:
    try:
        entry = database[id]
    except KeyError:
        raise
    else:
        if is_expired(entry):
            raise ValueError
    return entry