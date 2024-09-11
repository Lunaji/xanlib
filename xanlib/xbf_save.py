from struct import pack

def write_Int32sl(buffer, v):
	buffer.write(pack('<i', v))
	
def write_matrix44dl(buffer, v):
    buffer.write(pack('<16d', *v))
    
def write_vertex(buffer, vertex):
    buffer.write(pack('<3f', *vertex.position))
    buffer.write(pack('<3f', *vertex.normal))
    
def write_face(buffer, face):
    buffer.write(pack('<3i', *face.vertex_indices))
    buffer.write(pack('<1i', face.texture_index))
    buffer.write(pack('<1i', face.flags))
    for uv in face.uv_coords:
        buffer.write(pack('2f', *uv))
	
def write_node(buffer, node):
    write_Int32sl(buffer, len(node.vertices))
    write_Int32sl(buffer, node.flags)
    write_Int32sl(buffer, len(node.faces))
    write_Int32sl(buffer, len(node.children))
    write_matrix44dl(buffer, node.transform)
    write_Int32sl(buffer, len(node.name))
    buffer.write(node.name.encode())
    
    for child in node.children:
        write_node(buffer, child)
        
    for vertex in node.vertices:
        write_vertex(buffer, vertex)
        
    for face in node.faces:
        write_face(buffer, face)
        

def save_xbf(scene, filename):
    with open(filename, 'wb') as f:
        write_Int32sl(f, scene.version)
        write_Int32sl(f, len(scene.FXData))
        f.write(scene.FXData)
        write_Int32sl(f, len(scene.textureNameData))
        f.write(scene.textureNameData)
        for node in scene.nodes:
            write_node(f, node)
