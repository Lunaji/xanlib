import io
import pytest
from xanlib.xbf_load import (
    readInt,
    readUInt, 
    readInt16, 
    readInt8, 
    readUInt8, 
    readUInt16, 
    readMatrix, 
    readByte,
    read_vertex,
    read_face,
    read_vertex_animation,
    read_key_animation,
    read_node,
    load_xbf,
)
from xanlib.scene import convert_signed_5bit
from conftest import load_test_data


def test_convert_signed_5bit(signed_5bit):
    v, expected = signed_5bit
    assert convert_signed_5bit(v) == expected


#TODO: parametrize
def test_read_positive_integer(pos_int):
    stream = io.BytesIO(pos_int['binary'])
    assert readInt(stream) == pos_int['decoded']

def test_read_negative_integer():
    stream = io.BytesIO(b'\xc0\x1d\xfe\xff')  # Represents -123456 in little-endian
    assert readInt(stream) == -123456

def test_read_zero():
    stream = io.BytesIO(b'\x00\x00\x00\x00')  # Represents 0
    assert readInt(stream) == 0

def test_read_minimum_value():
    stream = io.BytesIO(b'\x00\x00\x00\x80')  # Represents -2147483648 (minimum 32-bit signed int)
    assert readInt(stream) == -2147483648

def test_read_maximum_value():
    stream = io.BytesIO(b'\xff\xff\xff\x7f')  # Represents 2147483647 (maximum 32-bit signed int)
    assert readInt(stream) == 2147483647
    
#rest

def test_readUInt(pos_int):
    stream = io.BytesIO(pos_int['binary'])
    assert readUInt(stream) == pos_int['decoded']

    # Test the maximum value for unsigned 32-bit integer (4294967295)
    stream = io.BytesIO(b'\xff\xff\xff\xff')  # 4294967295 in little-endian
    assert readUInt(stream) == 4294967295

    # Test with zero
    stream = io.BytesIO(b'\x00\x00\x00\x00')  # 0 in little-endian
    assert readUInt(stream) == 0

def test_readInt16():
    # Test a positive 16-bit signed integer
    stream = io.BytesIO(b'\x34\x12')  # 4660 in little-endian
    assert readInt16(stream) == 4660

    # Test the minimum 16-bit signed integer (-32768)
    stream = io.BytesIO(b'\x00\x80')  # -32768 in little-endian
    assert readInt16(stream) == -32768

    # Test the maximum 16-bit signed integer (32767)
    stream = io.BytesIO(b'\xff\x7f')  # 32767 in little-endian
    assert readInt16(stream) == 32767

def test_readInt8():
    # Test positive 8-bit signed integer
    stream = io.BytesIO(b'\x7f')  # 127 in 8-bit signed integer
    assert readInt8(stream) == 127

    # Test negative 8-bit signed integer
    stream = io.BytesIO(b'\x80')  # -128 in 8-bit signed integer
    assert readInt8(stream) == -128

def test_readUInt8():
    # Test maximum value for 8-bit unsigned integer
    stream = io.BytesIO(b'\xff')  # 255 in 8-bit unsigned integer
    assert readUInt8(stream) == 255

    # Test minimum value (zero)
    stream = io.BytesIO(b'\x00')  # 0 in 8-bit unsigned integer
    assert readUInt8(stream) == 0

def test_readUInt16():
    # Test a positive 16-bit unsigned integer
    stream = io.BytesIO(b'\x34\x12')  # 4660 in little-endian
    assert readUInt16(stream) == 4660

    # Test maximum value for 16-bit unsigned integer (65535)
    stream = io.BytesIO(b'\xff\xff')  # 65535 in little-endian
    assert readUInt16(stream) == 65535

def test_readMatrix():
    # Binary representation of 1.0 and 0.0 in double-precision floating point (64-bit)
    bin_one = b'\x00\x00\x00\x00\x00\x00\xf0\x3f'  # 1.0
    bin_zero = b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0

    # Use variables to build the 4x4 identity matrix as binary data (16 doubles, 128 bytes)
    binary_matrix = (
        bin_one + bin_zero + bin_zero + bin_zero +  # Row 1: 1.0, 0.0, 0.0, 0.0
        bin_zero + bin_one + bin_zero + bin_zero +  # Row 2: 0.0, 1.0, 0.0, 0.0
        bin_zero + bin_zero + bin_one + bin_zero +  # Row 3: 0.0, 0.0, 1.0, 0.0
        bin_zero + bin_zero + bin_zero + bin_one    # Row 4: 0.0, 0.0, 0.0, 1.0
    )
    
    stream = io.BytesIO(binary_matrix)
    matrix = readMatrix(stream)
    
    expected_matrix = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
    
    assert matrix == expected_matrix

def test_readByte():
    # Test reading a single byte ('a')
    stream = io.BytesIO(b'a')
    assert readByte(stream) == b'a'

    # Test reading another byte ('z')
    stream = io.BytesIO(b'z')
    assert readByte(stream) == b'z'
    
def test_read_vertex(vertex):
    stream = io.BytesIO(vertex.encoded)
    result = read_vertex(stream)
    assert result == vertex.decoded
    
def test_read_face(face):
    stream = io.BytesIO(face.encoded)
    result = read_face(stream)
    assert result == face.decoded

def test_read_vertex_animation(vertex_animation):
    stream = io.BytesIO(vertex_animation.encoded)
    result = read_vertex_animation(stream)
    assert result == vertex_animation.decoded

def test_read_key_animation(key_animation):
    stream = io.BytesIO(key_animation.encoded)
    result = read_key_animation(stream)
    assert result == key_animation.decoded

def test_read_node_basic(node_basic):
    stream = io.BytesIO(node_basic.encoded)
    result = read_node(stream)
    assert result == node_basic.decoded

def test_read_node_with_children(node_with_children):
    stream = io.BytesIO(node_with_children.encoded)
    result = read_node(stream)
    result.children[0].parent = None #TODO: remove this line
    assert result == node_with_children.decoded

def test_load_xbf(mocker, scene):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data=scene.encoded))
    result = load_xbf(scene.decoded.file)
    assert result == scene.decoded
    mock_open.assert_called_once_with(scene.decoded.file, 'rb')
