from struct import pack

def write_Int32sl(buffer, v):
	buffer.write(pack("<i", v))

def save_xbf(scene, filename):
    with open(filename, 'wb') as f:
        write_Int32sl(f, scene.version)
        write_Int32sl(f, len(scene.FXData))
        f.write(scene.FXData)
        write_Int32sl(f, len(scene.textureNameData))
        f.write(scene.textureNameData)
