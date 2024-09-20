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
    convert_signed_5bit,
)
from xanlib.scene import (
    Vertex,
    Face,
    VertexAnimation,
    KeyAnimation,
    Node,
)
from xanlib.xbf_base import NodeFlags


def test_convert_signed_5bit(signed_5bit):
    v, expected = signed_5bit
    assert convert_signed_5bit(v) == expected


#TODO: parametrize
def test_read_positive_integer(pos_int):
    buffer = io.BytesIO(pos_int['binary'])
    assert readInt(buffer) == pos_int['decoded']

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

def test_readUInt(pos_int):
    buffer = io.BytesIO(pos_int['binary'])
    assert readUInt(buffer) == pos_int['decoded']

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
    
def test_read_vertex(vertex_data):    
    given, expected = vertex_data
    buffer = io.BytesIO(given)
    vertex = read_vertex(buffer)    
    assert vertex == expected
    
def test_read_face(face_data):
    
    face_bin, expected_face = face_data
    
    buffer = io.BytesIO(face_bin)
    
    face = read_face(buffer)
    
    assert face == expected_face

#TODO: cases of count<0 and interpolation    
def test_read_vertex_animation(vertex_animation):
    buffer = io.BytesIO(vertex_animation['binary'])
    va = read_vertex_animation(buffer)
    
    assert va == vertex_animation['decoded']

# Key animation tests for different cases of `flags`
def test_read_key_animation_flags_minus1():
    # Binary data for frame_count = 2, flags = -1
    frame_count_bin = b'\x02\x00\x00\x00'  # 2 as int
    flags_bin = b'\xff\xff\xff\xff'        # -1 as int
    
    # 3 matrices (frame_count + 1) of 16 floats each (all set to 1.0 for simplicity)
    matrices_bin = b''.join([b'\x00\x00\x80\x3f' * 16] * 3)  # 1.0 as 32-bit float (little-endian)
    
    binary_data = frame_count_bin + flags_bin + matrices_bin
    
    buffer = io.BytesIO(binary_data)
    
    key_animation = read_key_animation(buffer)
    
    expected_key_animation = KeyAnimation(
        frame_count=2,
        flags=-1,
        matrices=[(1.0,) * 16] * 3,
        actual=None,
        extra_data=None
    )
    
    assert key_animation == expected_key_animation

def test_read_key_animation_flags_minus2():
    # Binary data for frame_count = 1, flags = -2
    frame_count_bin = b'\x01\x00\x00\x00'  # 1 as int
    flags_bin = b'\xfe\xff\xff\xff'        # -2 as int
    
    # 2 matrices (frame_count + 1) of 12 floats each (all set to 2.0 for simplicity)
    matrices_bin = b''.join([b'\x00\x00\x00\x40' * 12] * 2)  # 2.0 as 32-bit float (little-endian)
    
    binary_data = frame_count_bin + flags_bin + matrices_bin
    
    buffer = io.BytesIO(binary_data)
    
    key_animation = read_key_animation(buffer)
    
    expected_key_animation = KeyAnimation(
        frame_count=1,
        flags=-2,
        matrices=[(2.0,) * 12] * 2,
        actual=None,
        extra_data=None
    )
    
    assert key_animation == expected_key_animation

def test_read_key_animation_flags_minus3():
    # Binary data for frame_count = 1, flags = -3, actual = 2
    frame_count_bin = b'\x01\x00\x00\x00'  # 1 as int
    flags_bin = b'\xfd\xff\xff\xff'        # -3 as int
    actual_bin = b'\x02\x00\x00\x00'       # 2 as int
    
    # 2 extra_data entries (frame_count + 1) as 16-bit integers
    extra_data_bin = b'\x0a\x00' * 2  # 10 as int16
    
    # 2 matrices (actual count) of 12 floats each (all set to 3.0 for simplicity)
    matrices_bin = b''.join([b'\x00\x00\x40\x40' * 12] * 2)  # 3.0 as 32-bit float (little-endian)
    
    binary_data = frame_count_bin + flags_bin + actual_bin + extra_data_bin + matrices_bin
    
    buffer = io.BytesIO(binary_data)
    
    key_animation = read_key_animation(buffer)
    
    expected_key_animation = KeyAnimation(
        frame_count=1,
        flags=-3,
        matrices=[(3.0,) * 12] * 2,
        actual=2,
        extra_data=[10, 10]
    )
    
    assert key_animation == expected_key_animation

def test_read_node_basic(vertex_data, face_data):
    
    vertex_bin, expected_vertex = vertex_data
    face_bin, expected_face = face_data
    
    # Binary data for vertexCount = 1, flags = NodeFlags.PRELIGHT, faceCount = 1, childCount = 0, name = "TestNode"
    vertexCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    flags_bin = b'\x01\x00\x00\x00'        # NodeFlags.PRELIGHT (1)
    faceCount_bin = b'\x01\x00\x00\x00'    # 1 as int
    childCount_bin = b'\x00\x00\x00\x00'   # 0 as int (no children)
    
    matrix_bin = b'\x00' * (8 * 16)  # Simplified for the mock

    # Name: length = 8, "TestNode"
    nameLength_bin = b'\x08\x00\x00\x00'  # 8 as int
    name_bin = b'TestNode'

    # RGB color data for 1 vertex: (255, 0, 0)
    rgb_bin = b'\xff\x00\x00'

    binary_data = (
        vertexCount_bin + flags_bin + faceCount_bin + childCount_bin + 
        matrix_bin + nameLength_bin + name_bin + vertex_bin + face_bin + rgb_bin
    )

    buffer = io.BytesIO(binary_data)

    node = read_node(buffer)

    # Check basic attributes
    assert node is not None
    assert node.flags == NodeFlags.PRELIGHT
    assert node.name == "TestNode"
    assert node.vertices == [expected_vertex]
    assert node.faces == [expected_face]
    assert node.rgb == [(255, 0, 0)]
    
def test_read_node_with_children(vertex_data, face_data):
    
    vertex_bin, expected_vertex = vertex_data
    face_bin, expected_face = face_data

    # Binary data for parent node (vertexCount = 1, faceCount = 1, childCount = 1)
    vertexCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    flags_bin = b'\x01\x00\x00\x00'        # NodeFlags.PRELIGHT (1)
    faceCount_bin = b'\x01\x00\x00\x00'    # 1 as int
    childCount_bin = b'\x01\x00\x00\x00'   # 1 as int (1 child)

    # Identity matrix for parent node.transform (mocked 4x4 matrix)
    matrix_bin = b'\x00' * (8 * 16)  # Simplified for the mock

    # Name: length = 10, "ParentNode"
    nameLength_bin = b'\x0a\x00\x00\x00'  # 10 as int
    parent_name_bin = b'ParentNode'

    # RGB color data for parent vertex: (255, 0, 0)
    rgb_bin = b'\xff\x00\x00'

    # Binary data for child node (vertexCount = 1, faceCount = 1, childCount = 0)
    child_vertexCount_bin = b'\x01\x00\x00\x00'  # 1 as int
    child_flags_bin = b'\x01\x00\x00\x00'        # NodeFlags.PRELIGHT (1)
    child_faceCount_bin = b'\x01\x00\x00\x00'    # 1 as int
    child_childCount_bin = b'\x00\x00\x00\x00'   # 0 as int (no children)

    # Name: length = 9, "ChildNode"
    child_nameLength_bin = b'\x09\x00\x00\x00'  # 9 as int
    child_name_bin = b'ChildNode'

    # RGB color data for child vertex: (0, 255, 0)
    child_rgb_bin = b'\x00\xff\x00'

    child_node_bin = (
        child_vertexCount_bin + child_flags_bin + child_faceCount_bin + child_childCount_bin +
        matrix_bin + child_nameLength_bin + child_name_bin + vertex_bin + face_bin + child_rgb_bin
    )

    binary_data = (
        vertexCount_bin + flags_bin + faceCount_bin + childCount_bin +
        matrix_bin + nameLength_bin + parent_name_bin + child_node_bin +
        vertex_bin + face_bin + rgb_bin
    )

    buffer = io.BytesIO(binary_data)

    node = read_node(buffer)

    # Check parent node attributes
    assert node is not None
    assert node.name == "ParentNode"
    assert node.vertices == [expected_vertex]  # Reusing expected vertex object
    assert node.faces == [expected_face]       # Reusing expected face object
    assert node.rgb == [(255, 0, 0)]           # RGB for parent

    # Check that the parent node has one child
    assert len(node.children) == 1

    # Check child node attributes
    child_node = node.children[0]
    assert child_node.name == "ChildNode"
    assert child_node.vertices == [expected_vertex]  # Reusing expected vertex object
    assert child_node.faces == [expected_face]       # Reusing expected face object
    assert child_node.rgb == [(0, 255, 0)]           # RGB for child

