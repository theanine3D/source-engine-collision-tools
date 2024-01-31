from PyVMF import *
from random import randint
from typing import List


def triangulate_displacement(vmf: VMF, group: List[Solid], base_triangle: Solid = None, resolution=1, height=2):
    if base_triangle is None:
        base_triangle = SolidGenerator.displacement_triangle(Vertex(0, 0, 0), 1, 1, height)
        base_triangle.move(0, -1, 0)
        base_triangle.set_texture("tools/toolstrigger")

    if resolution != 1 and resolution % 2 == 1:
        raise ValueError("Resolution must either be 1 or a multiple of 2")

    # The tuples below represent the different corners of the triangle -> (False, True) = Left-Top corner
    # I divide the displacement into a matrix_size_fix amount of squares (ex: 4*4), each square is made up of 2
    # triangles (one being a 180 degree rotation of the other). Each new square is the previous square flipped on the
    # x-axis. This is why l_extremities has 2 sub-lists, one for "normal" extremities, and one for flipped extremities
    l_extremities = [[(False, True), None, (False, False), (True, False)],
                     [(False, True), (True, True), (False, False), None]]
    r_extremities = [[(False, True), (True, True), None, (True, False)],
                     [None, (True, True), (False, False), (True, False)]]

    directions = (l_extremities, r_extremities)

    export_list = []

    for solid in group:

        solid_side = solid.get_displacement_sides()[0]
        disp = solid_side.get_displacement()
        if disp:
            matrix = disp.matrix

            angle = solid_side.get_naive_rotation()

            # correct_size = solid.copy()
            # correct_size.rotate_z(solid.center_geo, -angle)

            size = solid.size

            size.divide(disp.matrix_size_fix/resolution)

            triangle = base_triangle.copy()

            flipped = True  # Whether the "triangle square" should be flipped or not
            tris_list = []
            for sy in range(0, disp.matrix_size_fix, resolution):
                # The last "triangle square" of a row is the same flip direction as the first in the next row
                flipped = not flipped
                for sx in range(0, disp.matrix_size_fix, resolution):
                    left_tri = triangle.copy()

                    left_tri.rotate_z(left_tri.center_geo, flipped * -90)
                    left_tri.scale(Vertex(0, 0, 0), size.x, size.y, 1)
                    left_tri.move(sx * size.x / resolution, sy * -size.y / resolution, 0)

                    right_tri = left_tri.copy()
                    right_tri.rotate_z(right_tri.center_geo, 180)

                    # --------------------------------- Change the values here for some cool geometry
                    left_tri.move(0, 0, 0)
                    right_tri.move(0, 0, 0)
                    # ---------------------------------

                    tris = [left_tri, right_tri]

                    flipped = not flipped

                    i = 0
                    for x, y, vert in matrix.inv_rect(sx, sy, 2*resolution, 2*resolution, resolution):
                        for j, side in enumerate(directions):
                            direction = side[not flipped][i]
                            if direction is not None:
                                for tri_vert in tris[j].get_3d_extremity(*direction)[1]:
                                    lv = tris[j].get_linked_vertices(tri_vert)
                                    for weird in lv:
                                        weird.move(0, 0, vert.normal.z * vert.distance)

                        i += 1

                    tris_list.extend(tris)

            export_list.extend(tris_list)
            # f = solid.get_3d_extremity(False, True, True)[0]
            # diff = f.diff(tris_list[0].get_3d_extremity(False, True, True)[0])
            # diff.z = f.diff(Vertex(0, 0, 0)).z

            target = solid.center_geo

            center = vmf.get_group_center(tris_list, geo=True)

            move = target.diff(center)

            move.z = solid.get_axis_extremity(z=True).z

            for trio in tris_list:
                trio.rotate_z(center, 0)
                trio.move(*move.export())

    return export_list
