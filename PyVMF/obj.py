from pywavefront import *
from PyVMF import *


def obj_to_solids(filename: str, material_path: str = "", scale=64):
    """
    Turns an .obj file to VMF solids, **BETA** it's very finicky and remember to invert normals

    :param filename: The name of the .obj file with path (ex: "test/wall.obj")
    :param material_path: The path to the .VMT's using same names (from the game materials folder, ex: "custom/ramp/"
    :param scale: The scale applied to the entire .obj
    """
    if material_path[-1] != "/":
        material_path += "/"

    scene = Wavefront(filename, collect_faces=True)
    for mesh in scene.mesh_list:
        solid = Solid()

        for face in mesh.faces[::2]:
            side = Side()

            for i, vertex in enumerate(face):
                vs = str(scene.vertices[vertex])
                v = Convert.string_to_vertex(vs)
                v.multiply(scale)
                side.plane[i] = v

            solid.add_sides(side)

        solid.editor = Editor()
        solid.set_texture(material_path + mesh.materials[0].name[0:-3])
        solid.rotate_x(Vertex(), 90)

        yield solid
