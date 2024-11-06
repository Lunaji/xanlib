import io
from xanlib.xbf_load import (
    read_key_animation,
    read_node,
    load_xbf,
)
from xanlib.face import Face
from xanlib.vertex import Vertex
from xanlib.compressed_vertex import convert_signed_5bit
from xanlib.vertex_animation import VertexAnimation


def test_convert_signed_5bit(signed_5bit):
    v, expected = signed_5bit
    assert convert_signed_5bit(v) == expected


def test_read_vertex(vertex):
    assert Vertex(*Vertex.cstruct.unpack(vertex.encoded)) == vertex.decoded


def test_read_face(face):
    assert Face(*Face.cstruct.unpack(face.encoded)) == face.decoded


def test_read_vertex_animation(vertex_animation):
    stream = io.BytesIO(vertex_animation.encoded)
    result = VertexAnimation.fromstream(stream)
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
    result.children[0].parent = None  # TODO: remove this line
    assert result == node_with_children.decoded


def test_load_xbf(mocker, scene):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=scene.encoded))
    result = load_xbf(scene.decoded.file)
    assert result == scene.decoded
    mock_open.assert_called_once_with(scene.decoded.file, "rb")
