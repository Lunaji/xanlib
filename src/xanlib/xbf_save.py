from struct import pack
from .xbf_base import NodeFlags

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

def write_compressed_vertex(stream, compressed_vertex):
    stream.write(pack('<3hH', *vars(compressed_vertex).values()))
    
def write_face(stream, face):
    stream.write(pack('<3i', *face.vertex_indices))
    stream.write(pack('<1i', face.texture_index))
    stream.write(pack('<1i', face.flags))
    for uv in face.uv_coords:
        stream.write(pack('2f', *uv))
        
def write_vertex_animation(stream, va):
    write_Int32sl(stream, va.frame_count)
    write_Int32sl(stream, va.count)
    write_Int32sl(stream, va.actual)
    for key in va.keys:
        write_Int32ul(stream, key)
    
    if va.count<0:
        write_Int32ul(stream, va.scale)
        write_Int32ul(stream, va.base_count)
        for frame in va.frames:
            for vertex_flagged in frame:
                write_compressed_vertex(stream, vertex_flagged)
        if (va.scale & 0x80000000):
            for v in va.interpolation_data:
                write_Int32ul(stream, v)
                
def write_key_animation(stream, ka):
    write_Int32sl(stream, ka.frame_count)
    write_Int32sl(stream, ka.flags)
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
            write_Int16sl(stream, frame.frame_id)
            write_Int16sl(stream, frame.flag)
            if frame.rotation is not None:
                stream.write(pack('<4f', *frame.rotation))
            if frame.scale is not None:
                stream.write(pack('<3f', *frame.scale))
            if frame.translation is not None:
                stream.write(pack('<3f', *frame.translation))
	
def write_node(stream, node):
    write_Int32sl(stream, len(node.vertices))
    write_Int32sl(stream, node.flags)
    write_Int32sl(stream, len(node.faces))
    write_Int32sl(stream, len(node.children))
    write_matrix44dl(stream, node.transform)
    write_Int32sl(stream, len(node.name))
    stream.write(node.name.encode())
    
    for child in node.children:
        write_node(stream, child)
        
    for vertex in node.vertices:
        write_vertex(stream, vertex)
        
    for face in node.faces:
        write_face(stream, face)
        
    if NodeFlags.PRELIGHT in node.flags:
        for j, vertex in enumerate(node.vertices):
            for i in range(3):
                write_Int8ul(stream, node.rgb[j][i])

    if NodeFlags.FACE_DATA in node.flags:
        for faceDatum in node.faceData:
            write_Int32sl(stream, faceDatum)

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
