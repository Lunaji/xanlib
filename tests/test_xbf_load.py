import io
import pytest
from xanlib.xbf_load import readInt

def test_read_positive_integer():
    buffer = io.BytesIO(b'\x40\xe2\x01\x00')  # Represents 123456 in little-endian
    assert readInt(buffer) == 123456

def test_read_negative_integer():
    buffer = io.BytesIO(b'\xc0\x1d\xfe\xff')  # Represents -123456 in little-endian
    assert readInt(buffer) == -123456

def test_read_zero():
    buffer = io.BytesIO(b'\x00\x00\x00\x00')  # Represents 0
    assert readInt(buffer) == 0

def test_read_minimum_value():
    buffer = io.BytesIO(b'\x00\x00\x00\x80')  # Represents -2147483648 (minimum 32-bit signed int)
    assert readInt(buffer) == -2147483648

def test_read_maximum_value():
    buffer = io.BytesIO(b'\xff\xff\xff\x7f')  # Represents 2147483647 (maximum 32-bit signed int)
    assert readInt(buffer) == 2147483647
