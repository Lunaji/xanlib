from struct import pack

def save_xbf(scene, filename):
    with open(filename, 'wb') as f:
        f.write(pack('<2i', scene.version, len(scene.FXData)))
        f.write(scene.FXData)
        f.write(pack('<i', len(scene.textureNameData)))
        f.write(scene.textureNameData)
