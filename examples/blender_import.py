# This script imports a 3D model from the game "Emperor:Battle for Dune" into Blender.
# Open and run it in Blender's script editor.
# Alternatively, run blender from the command line with the --python flag:
# blender --python examples/blender_import.py
# Assumes the game assets can be found from the working directory.
# Adjust the paths as needed.
import bpy
from mathutils import Matrix
from xanlib import load_xbf

def should_hide(name):
    return name == "#^^0" or "{LEECH}" in name or name.startswith("SLCT")

def process_node(node, materials, parent_obj=None):
    mesh = bpy.data.meshes.new(name=f'{node.name}_mesh')

    obj = bpy.data.objects.new(name=node.name, object_data=mesh)
    for material in materials:
        obj.data.materials.append(material)

    mesh.from_pydata(
        [vertex.position for vertex in node.vertices],
        [],
        [face.vertex_indices for face in node.faces]
    )

    for i, face in enumerate(mesh.polygons):
        face.material_index = node.faces[i].texture_index

        for j, loop_index in enumerate(face.loop_indices):
            u = node.faces[i].uv_coords[j][0]
            v = 1 - node.faces[i].uv_coords[j][1]
            if not mesh.uv_layers:
                mesh.uv_layers.new(name="UVMap")
            if not mesh.uv_layers.active:
                mesh.uv_layers.active = mesh.uv_layers[0]
            mesh.uv_layers.active.data[loop_index].uv = [u,v]

    obj.matrix_local = Matrix([node.transform[i*4:(i+1)*4] for i in range(4)]).transposed()

    if parent_obj is not None:
        obj.parent = parent_obj
    bpy.context.collection.objects.link(obj)

    if should_hide(node.name):
        obj.hide_viewport = True
        obj.hide_render = True

    for child in node.children:
        process_node(child, materials, obj)



scene = load_xbf('Data/3DDATA0001/Units/HK_missile_H0.xbf')
materials = []
for texture in scene.textures:
    material = bpy.data.materials.new(name=f"Material_{texture}")
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (0, 0)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)

    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.location = (-400, 0)

    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.location = (-400, 0)

    try:
        texture_image = bpy.data.images.load(f'Data/3DDATA0001/Textures/{texture}')
    except:
        texture_image = None

    if texture_image is not None:
        texture_node.image = texture_image

    links.new(texture_node.outputs['Color'], bsdf_node.inputs['Base Color'])

    materials.append(material)

for node in scene.nodes:
    process_node(node, materials)
