from xanlib.xbf_save import save_xbf


def test_write_vertex(vertex):
    assert bytes(vertex.decoded) == vertex.encoded


def test_write_face(face):
    assert bytes(face.decoded) == face.encoded


def test_write_vertex_animation(vertex_animation):
    assert bytes(vertex_animation.decoded) == vertex_animation.encoded


def test_write_key_animation(key_animation):
    assert bytes(key_animation.decoded) == key_animation.encoded


def test_write_node_basic(node_basic):
    assert bytes(node_basic.decoded) == node_basic.encoded


def test_write_node_with_children(node_with_children):
    assert bytes(node_with_children.decoded) == node_with_children.encoded


def test_write_scene(scene):
    assert bytes(scene.decoded) == scene.encoded


def test_save_xbf(mocker, scene):
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    file = "foo.xbf"
    save_xbf(scene.decoded, file)
    mock_open.assert_called_once_with(file, "wb")
