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
)
from xanlib.scene import (
    Vertex,
    Face,
    VertexAnimation,
)

#readInt()

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
    
#rest

def test_readUInt():
    # Test with a positive number (123456)
    buffer = io.BytesIO(b'\x40\xe2\x01\x00')  # 123456 in little-endian
    assert readUInt(buffer) == 123456

    # Test the maximum value for unsigned 32-bit integer (4294967295)
    buffer = io.BytesIO(b'\xff\xff\xff\xff')  # 4294967295 in little-endian
    assert readUInt(buffer) == 4294967295

    # Test with zero
    buffer = io.BytesIO(b'\x00\x00\x00\x00')  # 0 in little-endian
    assert readUInt(buffer) == 0

def test_readInt16():
    # Test a positive 16-bit signed integer
    buffer = io.BytesIO(b'\x34\x12')  # 4660 in little-endian
    assert readInt16(buffer) == 4660

    # Test the minimum 16-bit signed integer (-32768)
    buffer = io.BytesIO(b'\x00\x80')  # -32768 in little-endian
    assert readInt16(buffer) == -32768

    # Test the maximum 16-bit signed integer (32767)
    buffer = io.BytesIO(b'\xff\x7f')  # 32767 in little-endian
    assert readInt16(buffer) == 32767

def test_readInt8():
    # Test positive 8-bit signed integer
    buffer = io.BytesIO(b'\x7f')  # 127 in 8-bit signed integer
    assert readInt8(buffer) == 127

    # Test negative 8-bit signed integer
    buffer = io.BytesIO(b'\x80')  # -128 in 8-bit signed integer
    assert readInt8(buffer) == -128

def test_readUInt8():
    # Test maximum value for 8-bit unsigned integer
    buffer = io.BytesIO(b'\xff')  # 255 in 8-bit unsigned integer
    assert readUInt8(buffer) == 255

    # Test minimum value (zero)
    buffer = io.BytesIO(b'\x00')  # 0 in 8-bit unsigned integer
    assert readUInt8(buffer) == 0

def test_readUInt16():
    # Test a positive 16-bit unsigned integer
    buffer = io.BytesIO(b'\x34\x12')  # 4660 in little-endian
    assert readUInt16(buffer) == 4660

    # Test maximum value for 16-bit unsigned integer (65535)
    buffer = io.BytesIO(b'\xff\xff')  # 65535 in little-endian
    assert readUInt16(buffer) == 65535

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
    
    buffer = io.BytesIO(binary_matrix)
    matrix = readMatrix(buffer)
    
    expected_matrix = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
    
    assert matrix == expected_matrix

def test_readByte():
    # Test reading a single byte ('a')
    buffer = io.BytesIO(b'a')
    assert readByte(buffer) == b'a'

    # Test reading another byte ('z')
    buffer = io.BytesIO(b'z')
    assert readByte(buffer) == b'z'
    
def test_read_vertex():
    # Raw binary data for position (1.0, 2.0, 3.0) and normal (4.0, 5.0, 6.0)
    binary_position = (
        b'\x00\x00\x80\x3f'  # 1.0 in little-endian (32-bit float)
        b'\x00\x00\x00\x40'  # 2.0 in little-endian (32-bit float)
        b'\x00\x00\x40\x40'  # 3.0 in little-endian (32-bit float)
    )
    binary_normal = (
        b'\x00\x00\x80\x40'  # 4.0 in little-endian (32-bit float)
        b'\x00\x00\xa0\x40'  # 5.0 in little-endian (32-bit float)
        b'\x00\x00\xc0\x40'  # 6.0 in little-endian (32-bit float)
    )
    
    # Combine binary data for position and normal
    binary_data = binary_position + binary_normal
    
    # Simulate a buffer using io.BytesIO
    buffer = io.BytesIO(binary_data)
    
    # Call the function to read the vertex from the buffer
    vertex = read_vertex(buffer)
    
    # Create the expected Vertex object
    expected_vertex = Vertex(position=(1.0, 2.0, 3.0), normal=(4.0, 5.0, 6.0))
    
    # Check if the returned Vertex matches the expected one
    assert vertex == expected_vertex
    
def test_read_face():
    # Pre-prepared binary data for vertex_indices (1, 2, 3), texture_index (4), flags (8),
    # and UV coordinates [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]

    # Binary data for vertex_indices: (1, 2, 3)
    vertex_indices_bin = (
        b'\x01\x00\x00\x00'  # 1 as a 32-bit little-endian int
        b'\x02\x00\x00\x00'  # 2 as a 32-bit little-endian int
        b'\x03\x00\x00\x00'  # 3 as a 32-bit little-endian int
    )
    
    # Binary data for texture_index: 4
    texture_index_bin = b'\x04\x00\x00\x00'  # 4 as a 32-bit little-endian int
    
    # Binary data for flags: 8
    flags_bin = b'\x08\x00\x00\x00'  # 8 as a 32-bit little-endian int
    
    # Binary data for UV coordinates: [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]
    uv_coords_bin = (
        b'\x00\x00\x80\x3f'  # 1.0 as a 32-bit little-endian float
        b'\x00\x00\x00\x40'  # 2.0 as a 32-bit little-endian float
        b'\x00\x00\x40\x40'  # 3.0 as a 32-bit little-endian float
        b'\x00\x00\x80\x40'  # 4.0 as a 32-bit little-endian float
        b'\x00\x00\xa0\x40'  # 5.0 as a 32-bit little-endian float
        b'\x00\x00\xc0\x40'  # 6.0 as a 32-bit little-endian float
    )

    # Combine all binary data
    binary_data = vertex_indices_bin + texture_index_bin + flags_bin + uv_coords_bin
    
    # Simulate a buffer using io.BytesIO
    buffer = io.BytesIO(binary_data)
    
    # Call the function to read the face from the buffer
    face = read_face(buffer)
    
    # Create the expected Face object
    expected_face = Face(
        vertex_indices=(1, 2, 3),
        texture_index=4,
        flags=8,
        uv_coords=((1.0, 2.0), (3.0, 4.0), (5.0, 6.0))
    )
    
    # Check if the returned Face matches the expected one
    assert face == expected_face
    
def test_read_vertex_animation():
    # Binary data for frame_count (2), count (1), actual (3)
    frame_count_bin = b'\x02\x00\x00\x00'  # 2 as int
    count_bin = b'\x01\x00\x00\x00'        # 1 as int
    actual_bin = b'\x03\x00\x00\x00'       # 3 as int
    
    # Binary data for key_list: 3 unsigned integers (1, 2, 3)
    key_list_bin = (
        b'\x01\x00\x00\x00'  # 1
        b'\x02\x00\x00\x00'  # 2
        b'\x03\x00\x00\x00'  # 3
    )
    
    binary_data = frame_count_bin + count_bin + actual_bin + key_list_bin
    
    buffer = io.BytesIO(binary_data)
    
    vertex_animation = read_vertex_animation(buffer)
    
    expected_vertex_animation = VertexAnimation(
        frame_count=2,
        count=1,
        actual=3,
        keys=[1, 2, 3],
        scale=None,
        base_count=None,
        real_count=None,
        body=None,
        interpolation_data=None
    )
    
    assert vertex_animation == expected_vertex_animation

