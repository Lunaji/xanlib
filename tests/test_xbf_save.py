import io
import pytest
from xanlib.xbf_save import (
    write_Int32sl
)

def test_write_Int32sl(pos_int):
    buffer = io.BytesIO()
    write_Int32sl(buffer, pos_int['decoded'])
    assert buffer.getvalue() == pos_int['binary']

