from struct import pack, Struct
from .xbf_base import NodeFlags
from xanlib.scene import CompressedVertex

def convert_to_5bit_signed(v):
    v_clamped = max(-15, min(15, int(round(v))))

    if v_clamped < 0:
        return v_clamped + 32
    else:
        return v_clamped

def write_Int32sl(stream, v):
	stream.write(pack('<i', v))
	
def write_Int32ul(stream, v):
	stream.write(pack('<I', v))
	
def write_Int16sl(stream, v):
	stream.write(pack('<h', v))
	
def write_Int16ul(stream, v):
	stream.write(pack('<H', v))
	
def write_Int8ul(stream, v):
	stream.write(pack('<B', v))
	
def write_matrix44dl(stream, v):
    stream.write(pack('<16d', *v))
    
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
        write_Int32sl(stream, ka.actual)
        for extra_datum in ka.extra_data:
            write_Int16sl(stream, extra_datum)
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
        node.name.encode()
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
        write_Int32sl(f, scene.version)
        write_Int32sl(f, len(scene.FXData))
        f.write(scene.FXData)
        write_Int32sl(f, len(scene.textureNameData))
        f.write(scene.textureNameData)
        for node in scene.nodes:
            write_node(f, node)
        if scene.unparsed is not None:
            f.write(scene.unparsed)
        else:
            write_Int32sl(f, -1)
