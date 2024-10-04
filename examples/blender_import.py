import bpy
from mathutils import Matrix
from xanlib import load_xbf

def process_node(node, parent_obj=None):
    mesh = bpy.data.meshes.new(name=f'{node.name}_mesh')
    obj = bpy.data.objects.new(name=node.name, object_data=mesh)
    mesh.from_pydata(
        [vertex.position for vertex in node.vertices],
        [],
        [face.vertex_indices for face in node.faces]
    )
    mesh.update()

    obj.matrix_local = Matrix([node.transform[i*4:(i+1)*4] for i in range(4)]).transposed()

    bpy.context.view_layer.update()

    if parent_obj is not None:
        obj.parent = parent_obj
    bpy.context.collection.objects.link(obj)

    for child in node.children:
        process_node(child, obj)

scene = load_xbf('Data/UI0001/FRONTEND/CAMPAIGN.XBF')
for node in scene.nodes:
    process_node(node)
