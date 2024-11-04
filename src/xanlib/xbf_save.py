from struct import pack, Struct
from xanlib.compressed_vertex import CompressedVertex
from xanlib.node import NodeFlags

def convert_to_5bit_signed(v):
    v_clamped = max(-15, min(15, int(round(v))))

    if v_clamped < 0:
        return v_clamped + 32
    else:
        return v_clamped
    
def write_vertex(stream, vertex):
    stream.write(pack('<3f', *vertex.position))
    stream.write(pack('<3f', *vertex.normal))
    
def write_face(stream, face):
    stream.write(pack('<3i', *face.vertex_indices))
    stream.write(pack('<1i', face.texture_index))
    stream.write(pack('<1i', face.flags))
    for uv in face.uv_coords:
        stream.write(pack('2f', *uv))
        
def write_vertex_animation(stream, va):
    header_fmt = Struct(f'<3i{len(va.keys)}I')
    stream.write(header_fmt.pack(va.frame_count, va.count, va.actual, *va.keys))
    
    if va.count<0:
        compressed_header_fmt = Struct('<2I')
        stream.write(compressed_header_fmt.pack(va.scale, va.base_count))
        for frame in va.frames:
            for vertex in frame:
                stream.write(CompressedVertex.fmt.pack(*vars(vertex).values()))
        if va.interpolation_data is not None:
            stream.write(pack(f'{len(va.interpolation_data)}I', *va.interpolation_data))
                
def write_key_animation(stream, ka):
    header_fmt = Struct('<2i')
    stream.write(header_fmt.pack(ka.frame_count, ka.flags))
    if ka.flags==-1:
        for matrix in ka.matrices:
            stream.write(pack('<16f', *matrix))
    elif ka.flags==-2:
        for matrix in ka.matrices:
            stream.write(pack('<12f', *matrix))
    elif ka.flags==-3:
        extra_fmt = Struct(f'i{len(ka.extra_data)}h')
        stream.write(extra_fmt.pack(ka.actual, *ka.extra_data))
        for matrix in ka.matrices:
            stream.write(pack('<12f', *matrix))
    else:
        for frame in ka.frames:
            pos_fmt = Struct('<2h')
            stream.write(pos_fmt.pack(frame.frame_id, frame.flag))
            if frame.rotation is not None:
                stream.write(pack('<4f', *frame.rotation))
            if frame.scale is not None:
                stream.write(pack('<3f', *frame.scale))
            if frame.translation is not None:
                stream.write(pack('<3f', *frame.translation))
	
def write_node(stream, node):
    header_fmt = Struct(f'<4i16dI{len(node.name)}s')
    stream.write(header_fmt.pack(
        len(node.vertices),
        node.flags,
        len(node.faces),
        len(node.children),
        *node.transform,
        len(node.name),
        node.name.encode('ascii')
    ))
    
    for child in node.children:
        write_node(stream, child)
        
    for vertex in node.vertices:
        write_vertex(stream, vertex)
        
    for face in node.faces:
        write_face(stream, face)
        
    if NodeFlags.PRELIGHT in node.flags:
        rgb_fmt = Struct(f'<{3*len(node.rgb)}B')
        stream.write(rgb_fmt.pack(*(c for rgb in node.rgb for c in rgb)))

    if NodeFlags.FACE_DATA in node.flags:
        stream.write(pack(f'<{len(node.faceData)}i', *node.faceData))

    if NodeFlags.VERTEX_ANIMATION in node.flags:
        write_vertex_animation(stream, node.vertex_animation)
        
    if NodeFlags.KEY_ANIMATION in node.flags:
        write_key_animation(stream, node.key_animation)

def save_xbf(scene, filename):
    with open(filename, 'wb') as f:
        header_fmt = Struct(f'<2i{len(scene.FXData)}si{len(scene.textureNameData)}s')
        f.write(header_fmt.pack(
            scene.version,
            len(scene.FXData),
            scene.FXData,
            len(scene.textureNameData),
            scene.textureNameData
        ))
        for node in scene.nodes:
            write_node(f, node)
        if scene.unparsed is not None:
            f.write(scene.unparsed)
        else:
            f.write(pack('i', -1))
