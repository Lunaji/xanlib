from struct import pack

def write_Int32sl(buffer, v):
	buffer.write(pack("<i", v))
	
def write_node(buffer, node):
    write_Int32sl(buffer, len(node.vertices))
    write_Int32sl(buffer, node.flags)
    write_Int32sl(buffer, len(node.faces))
    write_Int32sl(buffer, len(node.children))

def save_xbf(scene, filename):
    with open(filename, 'wb') as f:
        write_Int32sl(f, scene.version)
        write_Int32sl(f, len(scene.FXData))
        f.write(scene.FXData)
        write_Int32sl(f, len(scene.textureNameData))
        f.write(scene.textureNameData)
        for node in scene.nodes:
            write_node(f, node)
