import io
import pytest
from xanlib.xbf_save import (
    write_Int32sl,
    write_vertex_animation,
)

def test_write_Int32sl(pos_int):
    buffer = io.BytesIO()
    write_Int32sl(buffer, pos_int['decoded'])
    assert buffer.getvalue() == pos_int['binary']

def test_write_vertex_animation(vertex_animation):
    buffer = io.BytesIO()
    write_vertex_animation(buffer, vertex_animation['decoded'])
    assert buffer.getvalue() == vertex_animation['binary']

