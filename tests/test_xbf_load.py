from xanlib.face import Face
from xanlib.vertex import Vertex
from xanlib.compressed_vertex import convert_signed_5bit
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from xanlib.node import Node
from xanlib.scene import Scene
from xanlib.xbf_load import load_xbf


def test_convert_signed_5bit(signed_5bit):
    v, expected = signed_5bit
    assert convert_signed_5bit(v) == expected


def test_read_vertex(vertex):
    assert Vertex(*Vertex.cstruct.unpack(vertex.encoded)) == vertex.decoded


def test_read_face(face):
    assert Face(*Face.cstruct.unpack(face.encoded)) == face.decoded


def test_read_vertex_animation(vertex_animation):
    assert (
        VertexAnimation.frombuffer(vertex_animation.encoded) == vertex_animation.decoded
    )


def test_read_key_animation(key_animation):
    assert KeyAnimation.frombuffer(key_animation.encoded) == key_animation.decoded


def test_read_node_basic(node_basic):
    assert Node.frombuffer(node_basic.encoded) == node_basic.decoded


def test_read_node_with_children(node_with_children):
    result = Node.frombuffer(node_with_children.encoded)
    result.children[0].parent = None  # TODO: make this unnecessary
    assert result == node_with_children.decoded


def test_read_scene(scene):
    assert Scene.frombuffer(scene.encoded) == scene.decoded


def test_load_xbf(mocker, scene):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=scene.encoded))
    file = "foo.xbf"
    result = load_xbf(file)
    assert result == scene.decoded
    mock_open.assert_called_once_with(file, "rb")
