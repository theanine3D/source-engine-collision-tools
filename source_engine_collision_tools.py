import bpy
import bmesh
from mathutils import Vector
from bpy.utils import(register_class, unregister_class)
from bpy.types import(Panel, PropertyGroup)
from bpy.props import(StringProperty,
                      FloatProperty, BoolProperty)
import re

bl_info = {
    "name": "Source Engine Collision Tools",
    "description": "Quickly generate and optimize collision models for use in Source Engine",
    "author": "Theanine3D",
    "version": (0, 6),
    "blender": (3, 0, 0),
    "category": "Mesh",
    "location": "Properties -> Object Properties",
    "support": "COMMUNITY"
}

# PROPERTY DEFINITIONS


class SrcEngCollProperties(bpy.types.PropertyGroup):
    Decimate_Ratio: bpy.props.FloatProperty(
        name="Decimate Ratio", subtype="FACTOR", description="At 1.0, decimation is disabled. Lower value = stronger decimation, resulting in less accurate but more performant collision mesh. Note: Decimation reduces effectiveness of Merge Adjacent Similars", max=1.0, min=0.0, default=1)
    Extrusion_Modifier: bpy.props.FloatProperty(
        name="Extrude Factor", description="The setting affects the extrusion of each hull. Default will work in most cases", min=0.001, soft_max=200.0, default=40.0)
    Scale_Modifier: bpy.props.FloatProperty(
        name="Scale Modifier", subtype="FACTOR", description="Default will work in most cases. If you see chunks of geometry missing from the generated collision model, try setting this to something lower", soft_min=-0.001, soft_max=100, default=1)
    Similar_Factor: bpy.props.FloatProperty(
        name="Similar Factor", subtype="FACTOR", description="Similarity intensity for Merge Adjacent Similars. A higher factor will result in more hulls merging together, but at the cost of accuracy", min=0.0001, max=1.0, default=0.001)
    Distance_Modifier: bpy.props.FloatProperty(
        name="Distance Modifier", description="Affects the distance at which hulls can be merged. Default will work in most cases. A higher number will result in more hulls merging together, but at the cost of accuracy", soft_min=0.01, max=50, default=10)
    Thin_Threshold: bpy.props.FloatProperty(
        name="Thin Threshold", subtype="FACTOR", description="The thinness threshold to use when removing thin hulls. If set to default, the operator will only remove faces with an area that is lower than 10 percent of the average area of all faces", min=0.0001, max=.5, default=.01)
    Thin_Collapse: bpy.props.BoolProperty(
        name="Collapse", description="If enabled, thin faces will not be deleted, but instead will be collapsed in-place, preventing holes in geometry", default=True)
    QC_Folder: bpy.props.StringProperty(
        name="QC Folder", subtype="DIR_PATH", description="Full path of the folder in which to save the generated QCs", default="//export//phys//", maxlen=1024)
    QC_Src_Models_Dir: bpy.props.StringProperty(
        name="Models Path", subtype="DIR_PATH", description="Path of the folder where your compiled models are stored in the Source Engine game directory (ie. the path in $modelname, but without the model name)", default="mymodels\\", maxlen=1024)
    QC_Src_Mats_Dir: bpy.props.StringProperty(
        name="Materials Path", subtype="DIR_PATH", description="Path of the folder where your VMT and VTF files are stored in the Source Engine game directory (ie. the $cdmaterials path)", default="models\mymodels\\", maxlen=1024)
    VMF_File: bpy.props.StringProperty(
        name="VMF File", subtype="FILE_PATH", description="Path of the VMF map file, created in Hammer or some other mapping tool' ", default="", maxlen=1024)

# FUNCTION DEFINITIONS


def display_msg_box(message="", title="Info", icon='INFO'):
    ''' Open a pop-up message box to notify the user of something               '''
    ''' Example:                                                                '''
    ''' display_msg_box("This is a message", "This is a custom title", "ERROR") '''

    def draw(self, context):
        lines = message.split("\n")
        for line in lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def check_for_selected(verbose=True):

    # Check if any objects are selected.
    if len(bpy.context.selected_objects) == 1:
        if bpy.context.active_object != None:
            if bpy.context.active_object.type == "MESH":
                return True
            else:
                if verbose:
                    display_msg_box(
                        "There is no active mesh object. Click on one and try again", "Error", "ERROR")
                return False
        else:
            if verbose:
                display_msg_box(
                    "There is no active mesh object. Click on one and try again", "Error", "ERROR")
            return False
    else:
        if verbose:
            display_msg_box(
                "One mesh object must be selected and set as active", "Error", "ERROR")
        return False


def get_avg_length(obj):
    object = bpy.context.active_object
    edges = object.data.edges
    lengths = list()
    for edge in edges:
        v0 = object.data.vertices[edge.vertices[0]]
        v1 = object.data.vertices[edge.vertices[1]]
        x2 = (v0.co[0] - v1.co[0]) ** 2
        y2 = (v0.co[1] - v1.co[1]) ** 2
        z2 = (v0.co[2] - v1.co[2]) ** 2
        lengths.append((x2 + y2 + z2) ** 0.5)
    average_length = sum(lengths) / len(lengths)
    return average_length


def generate_SMD_lines():
    empty_SMD_lines = list()
    empty_SMD_lines.append("version 1\n")
    empty_SMD_lines.append("nodes\n")
    empty_SMD_lines.append('0 "root" -1\n')
    empty_SMD_lines.append("end\n")
    empty_SMD_lines.append("skeleton\n")
    empty_SMD_lines.append("time 0\n")
    empty_SMD_lines.append("0 0 0 0 0 0 0\n")
    empty_SMD_lines.append("end\n")
    empty_SMD_lines.append("triangles\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 25.878662  -0.577350 0.577350 -0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 25.878662  0.577350 0.577350 -0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 25.878662  0.577350 -0.577350 -0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 25.878662  -0.577350 0.577350 -0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 25.878662  0.577350 -0.577350 -0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 25.878662  -0.577350 -0.577350 -0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 -25.879150  -0.577350 0.577350 0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 -25.879150  0.577350 -0.577350 0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 -25.879150  0.577350 0.577350 0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 -25.879150  -0.577350 0.577350 0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 -25.879150  -0.577350 -0.577350 0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 -25.879150  0.577350 -0.577350 0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 25.878662  0.577350 -0.577350 -0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 -25.879150  -0.577350 -0.577350 0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 25.878662  -0.577350 -0.577350 -0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 25.878662  -0.577350 0.577350 -0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 -25.879150  0.577350 0.577350 0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 25.878662  0.577350 0.577350 -0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 25.878662  -0.577350 -0.577350 -0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 -25.879150  -0.577350 0.577350 0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 25.878662  -0.577350 0.577350 -0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 25.878662  0.577350 0.577350 -0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 -25.879150  0.577350 -0.577350 0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 25.878662  0.577350 -0.577350 -0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 25.878662  0.577350 -0.577350 -0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 -25.879150  0.577350 -0.577350 0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 -25.879150  -0.577350 -0.577350 0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 25.878662  -0.577350 0.577350 -0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 -25.879150  -0.577350 0.577350 0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 -25.879150  0.577350 0.577350 0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 25.878662  -0.577350 -0.577350 -0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 23.812263 -25.879150  -0.577350 -0.577350 0.577350  1.000000 1.000000 0\n")
    empty_SMD_lines.append(
        "0  23.812263 -23.812263 -25.879150  -0.577350 0.577350 0.577350  1.000000 0.000000 0\n")
    empty_SMD_lines.append("phys\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 25.878662  0.577350 0.577350 -0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 -23.812263 -25.879150  0.577350 0.577350 0.577350  0.000000 0.000000 0\n")
    empty_SMD_lines.append(
        "0  -23.812263 23.812263 -25.879150  0.577350 -0.577350 0.577350  0.000000 1.000000 0\n")
    empty_SMD_lines.append("end\n")
    return empty_SMD_lines


def generate_QC_lines(obj, models_dir, mats_dir):
    QC_template = list()
    QC_template.append(f'$modelname "{models_dir}{obj.name}.mdl"\n')
    QC_template.append(f'$body {obj.name} "Empty.smd"\n')
    QC_template.append('$surfaceprop default\n')
    QC_template.append('$staticprop\n')
    QC_template.append(f'$cdmaterials "{mats_dir}"\n')
    QC_template.append('$sequence ref "Empty.smd"\n')
    QC_template.append(f'$collisionmodel "{obj.name}.smd"\n')
    QC_template.append('{\n')
    QC_template.append('\t$concave\n')
    QC_template.append('}\n')
    return QC_template

# def separate_loose_bmesh(obj, keep_separate=False,):
#     me = obj.data
#     bm = bmesh.new()
#     bm.from_mesh(me)

#     faces = obj.data.polygons
#     verts = obj.data.vertices
#     edges = obj.data.edges
#     meshes = list()
#     return meshes


def bmesh_walk_hull(vert):
    ''' Walk all un-tagged linked verts '''
    vert.tag = True
    yield(vert)
    linked_verts = [e.other_vert(vert) for e in vert.link_edges
                    if not e.other_vert(vert).tag]

    for v in linked_verts:
        if v.tag:
            continue
        yield from bmesh_walk_hull(v)


def bmesh_get_hulls(bm, verts=[]):
    def tag(verts, switch):
        for v in verts:
            v.tag = switch
    tag(bm.verts, True)
    tag(verts, False)
    hulls = list()
    verts = set(verts)
    while verts:
        v = verts.pop()
        verts.add(v)
        hull = set(bmesh_walk_hull(v))
        hulls.append(list(hull))
        tag(hull, False)  # remove tag = True
        verts -= hull
    return hulls


def bmesh_join(target_bm, source_bm):
    '''
    source_bm into target_bm
    returns target_bm with added geometry, if source_bm is not empty.
    '''

    source_bm.verts.layers.int.new('index')
    idx_layer = source_bm.verts.layers.int['index']

    for face in source_bm.faces:
        new_verts = []
        for old_vert in face.verts:
            if not old_vert.tag:
                new_vert = target_bm.verts.new(old_vert.co)
                target_bm.verts.index_update()
                old_vert[idx_layer] = new_vert.index
                old_vert.tag = True

            target_bm.verts.ensure_lookup_table()
            idx = old_vert[idx_layer]
            new_verts.append(target_bm.verts[idx])

        target_bm.faces.new(new_verts)
    return target_bm

# Generate Collision Mesh operator


class GenerateSrcCollision(bpy.types.Operator):
    """Generate a Source Engine-compliant collision model based on the current active object. The original object will be temporarily hidden, but not modified otherwise"""
    bl_idname = "object.src_eng_collision"
    bl_label = "Generate Collision Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected():
            total_hull_count = 0
            root_collection = None
            if 'Collision Models' in bpy.data.collections.keys():
                root_collection = bpy.data.collections['Collision Models']
            else:
                root_collection = bpy.data.collections.new("Collision Models")
                bpy.context.scene.collection.children.link(root_collection)

            obj = bpy.context.active_object
            obj_collections = [
                c for c in bpy.data.collections if obj.name in c.objects.keys()]
            extrude_modifier = (-1) * \
                bpy.context.scene.SrcEngCollProperties.Extrusion_Modifier

            if "_phys" in bpy.context.active_object.name:
                display_msg_box(
                    "You have an existing collision model selected. Select a different model and try again.", "Error", "ERROR")
                return {'FINISHED'}

            original_dimensions = obj.dimensions
            doubles_threshold = bpy.context.scene.SrcEngCollProperties.Distance_Modifier

            obj_phys = None
            collection_phys = None

            bpy.ops.object.mode_set(mode="OBJECT")

            if (obj.name + "_phys") in bpy.data.objects.keys():
                bpy.data.objects.remove(bpy.data.objects[obj.name + "_phys"])

            bpy.ops.object.duplicate(linked=False)
            obj.hide_set(True)
            obj_phys = bpy.context.active_object
            obj_phys.name = obj.name + "_phys"

            # Resize object, based on user setting "Scale Factor"
            scale_modifier = bpy.context.scene.SrcEngCollProperties.Scale_Modifier
            bpy.ops.transform.resize(value=(scale_modifier, scale_modifier, scale_modifier), orient_type='GLOBAL', orient_matrix=(
                (1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, snap=False)
            bpy.ops.object.transform_apply(
                location=False, rotation=True, scale=True)

            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(
                use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.remove_doubles(threshold=doubles_threshold)
            bpy.ops.mesh.tris_convert_to_quads(
                seam=True, sharp=True, materials=True)

            # Decimate and clean up mesh to minimize unnecessary hulls being generated later
            bpy.ops.mesh.dissolve_limited(
                angle_limit=0.0872665, delimit={'NORMAL'})
            bpy.ops.mesh.vert_connect_concave()
            bpy.ops.mesh.face_make_planar(repeat=20)
            bpy.ops.mesh.vert_connect_nonplanar()
            bpy.ops.mesh.decimate(
                ratio=bpy.context.scene.SrcEngCollProperties.Decimate_Ratio)
            bpy.ops.mesh.vert_connect_concave()
            bpy.ops.mesh.vert_connect_nonplanar()

            bpy.ops.mesh.edge_split(type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Extrude faces
            bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip": False, "use_dissolve_ortho_edges": False, "mirror": False}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_axis_ortho": 'X', "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (
                False, False, False), "mirror": False, "use_proportional_edit": False, "snap": False, "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})

            # Move the extruded faces inward
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            bpy.ops.transform.shrink_fatten(value=(
                extrude_modifier), use_even_offset=False, mirror=True, use_proportional_edit=False, snap=False)

            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_smooth()

            # Setup collection
            if (obj_phys.name) in bpy.data.collections.keys():
                collection_phys = bpy.data.collections[obj_phys.name]
            else:
                collection_phys = bpy.data.collections.new(obj_phys.name)
                root_collection.children.link(collection_phys)

            collection_phys.objects.link(obj_phys)

            # Unlink the new collision model from other collections
            for c in obj_collections:
                if obj_phys.name in c.objects.keys():
                    c.objects.unlink(obj_phys)
            if obj_phys.name in bpy.context.scene.collection.objects.keys():
                bpy.context.scene.collection.objects.unlink(obj_phys)

            bpy.ops.object.mode_set(mode='OBJECT')

            # Begin Bmesh processing
            me = obj_phys.data
            bm = bmesh.new()
            bm_processed = bmesh.new()

            bm.from_mesh(me)
            hulls = [hull for hull in bmesh_get_hulls(
                bm, verts=bm.verts)]
            print(me.name, "Hulls to process:", len(hulls))

            # Create individual hull bmeshes
            for hull in hulls:
                bm_hull = bmesh.new()

                # Add vertices to individual bmesh hull
                for vert in hull:
                    bmesh.ops.create_vert(bm_hull, co=vert.co)

                # Generate convex hull
                ch = bmesh.ops.convex_hull(
                    bm_hull, input=bm_hull.verts, use_existing_faces=False)
                bmesh.ops.delete(
                    bm_hull,
                    geom=list(set(ch["geom_unused"] + ch["geom_interior"])),
                    context='VERTS')

                # TODO: this operator seems to make the mesh disappear for some reason. For now, it's commented out
                # bmesh.ops.dissolve_limit(
                #     bm_hull, angle_limit=0.08726646, use_dissolve_boundaries=False, verts=bm_hull.verts, edges=bm_hull.edges, delimit={'NORMAL'})
                bmesh.ops.triangulate(
                    bm_hull, faces=bm_hull.faces, quad_method='BEAUTY', ngon_method='BEAUTY')

                ch2 = bmesh.ops.convex_hull(
                    bm_hull, input=bm_hull.verts, use_existing_faces=False)
                bmesh.ops.delete(
                    bm_hull,
                    geom=list(set(ch2["geom_unused"] + ch2["geom_interior"])),
                    context='VERTS')

                # Add the processed hull to the new main object, which will store all of them
                bmesh_join(bm_processed, bm_hull)
                total_hull_count += 1
                bm_hull.clear()
                bm_hull.free()

            bm_processed.to_mesh(me)
            me.update()
            bm.clear()
            bm.free()
            bm_processed.clear()
            bm_processed.free()

            # End Bmesh processing

            # Recombine into one object
            bpy.ops.object.mode_set(mode='OBJECT')
            obj_phys.name = obj.name + "_phys"
            bpy.ops.object.shade_smooth()

            # Remove non-manifold and degenerates
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(
                use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.select_linked(delimit=set())
            bpy.ops.mesh.delete(type='VERT')

            # Cleanup materials
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.data.materials.clear()
            if "phys" not in bpy.data.materials.keys():
                bpy.data.materials.new("phys")
            bpy.context.active_object.data.materials.append(
                bpy.data.materials["phys"])
            bpy.context.active_object.data.materials[0].diffuse_color = (
                1, 0, 0.78315, 1)

            # Reset size back to normal
            obj_phys.dimensions = original_dimensions
            bpy.ops.object.transform_apply(
                location=False, rotation=True, scale=True)
            display_msg_box(
                "Generated collision mesh with total hull count of " + str(total_hull_count) + ".", "Info", "INFO")
            print("Generated collision mesh with total hull count of " +
                  str(total_hull_count) + ".")

        return {'FINISHED'}

# Split Up Collision Mesh operator


class SplitUpSrcCollision(bpy.types.Operator):
    """Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls"""
    bl_idname = "object.src_eng_split"
    bl_label = "Split Up Collision Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if check_for_selected():
            total_part_count = 0
            root_collection = None
            if 'Collision Models' in bpy.data.collections.keys():
                root_collection = bpy.data.collections['Collision Models']
            else:
                root_collection = bpy.data.collections.new("Collision Models")
                bpy.context.scene.collection.children.link(root_collection)

            obj = bpy.context.active_object
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            original_name = obj.name
            obj_collections = [
                c for c in bpy.data.collections if obj.name in c.objects.keys()]
            for c in obj_collections:
                if "_part_" in c.name:
                    display_msg_box(
                        "Your selected collision mesh is inside a collection with '_part_' inside the name, indicating it's already split up. Rename the collection so that it ends in '_phys', and try again.", "Error", "ERROR")
                    return {'FINISHED'}
            if "_part_" in obj.name:
                display_msg_box(
                    "The collision model you're trying to split up already has '_part_' in its name, indicating that it's already been split up.\nRename the mesh object first so its name ends in '_phys' and try again.", "Error", "ERROR")
                return {'FINISHED'}

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')

            # Separate all hulls into separate objects
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')

            # Split up into 32-hull segments
            hulls = bpy.context.selected_objects
            hull_groups = list()

            start = 0
            end = len(hulls)
            step = 32

            for i in range(start, end, step):
                x = i
                hull_groups.append(hulls[x:x+step])

            bpy.ops.object.select_all(action='DESELECT')

            i = len(hull_groups)-1

            while i >= 0:
                i = len(hull_groups)-1
                new_group_collection = None
                for h in hull_groups[i]:
                    h.select_set(True)

                bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_axis_ortho": 'X', "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (
                    False, False, False), "mirror": False, "use_proportional_edit": False, "snap": False, "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})
                total_part_count += 1
                bpy.ops.object.join()
                new_group_obj = bpy.context.selected_objects[0]

                bpy.context.view_layer.objects.active = new_group_obj
                new_group_obj.name = original_name + "_part_" + str(i).zfill(3)

                # Check if collection for this hull already exists. If not, create it
                if new_group_obj.name not in bpy.data.collections.keys():
                    new_group_collection = bpy.data.collections.new(
                        new_group_obj.name)
                else:
                    new_group_collection = bpy.data.collections[new_group_obj.name]

                root_collection.children.link(new_group_collection)
                for c in obj_collections:
                    c.objects.unlink(new_group_obj)

                new_group_collection.objects.link(new_group_obj)
                bpy.ops.object.transform_apply(
                    location=True, rotation=True, scale=True)
                new_group_obj.select_set(False)

                hull_groups.pop()
                if len(hull_groups) == 0:
                    break

            # Clean up
            total_part_count = str(total_part_count)

            bpy.data.objects.remove(bpy.data.objects[original_name])
            if original_name in bpy.data.collections.keys():
                bpy.data.collections.remove(
                    bpy.data.collections[original_name])
            for o in bpy.data.objects:
                if (original_name + ".") in o.name:
                    bpy.data.objects.remove(o)
            display_msg_box(
                "Split up collision mesh into " + total_part_count + " part(s).", "Info", "INFO")
            print("Split up collision mesh into " +
                  total_part_count + " part(s).")

        return {'FINISHED'}


# Merge Adjacent Similars operator

class Cleanup_MergeAdjacentSimilars(bpy.types.Operator):
    """Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a less accurate, but more performant model. If original model was already low-poly to begin with, you probably won't need this"""
    bl_idname = "object.src_eng_cleanup_merge_similars"
    bl_label = "Merge Adjacent Similars"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected():

            obj = bpy.context.active_object
            original_dimensions = bpy.context.active_object.dimensions
            obj_parts = set()
            doubles_threshold = bpy.context.scene.SrcEngCollProperties.Distance_Modifier
            similarity_threshold = bpy.context.scene.SrcEngCollProperties.Similar_Factor

            # Create working copy
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.duplicate(linked=False)

            # Make sure no faces are selected
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            work_obj = bpy.context.active_object
            faces = work_obj.data.polygons

            while len(faces) > 0:
                # Make sure no faces are selected first
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

                # Select the face and any linked to it
                try:
                    faces[len(faces)-1].select = True
                except:
                    continue
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.select_linked(delimit=set())

                # Store the selected face indexes
                bpy.ops.object.mode_set(mode='OBJECT')
                hull_face_indexes = [
                    f.index for f in faces if f.select]
                # hull_edge_indexes = [
                #     e.index for e in edges if e.select == True]
                # hull_vert_indexes = [
                #     v.index for v in verts if v.select == True]

                # Duplicate the selected faces and get dimensions + origin
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode": 1}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_axis_ortho": 'X', "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (
                    False, False, False), "mirror": False, "use_proportional_edit": False, "snap": False, "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(False)
                work_obj.select_set(False)
                measurement_obj = bpy.context.selected_objects[0]
                bpy.context.view_layer.objects.active = measurement_obj
                bpy.ops.object.origin_set(
                    type='ORIGIN_GEOMETRY', center='MEDIAN')

                # Store the min and max coords (adding/substracting the hull dimensions x 2.5)
                hull_dimensions = measurement_obj.dimensions
                hull_bbox_min = measurement_obj.matrix_world @ Vector(
                    measurement_obj.bound_box[0])
                hull_bbox_max = measurement_obj.matrix_world @ Vector(
                    measurement_obj.bound_box[6])

                x_bounds = [hull_bbox_min[0] - (hull_dimensions[0] * 2.5),
                            hull_bbox_max[0] + (hull_dimensions[0] * 2.5)]
                y_bounds = [hull_bbox_min[1] - (hull_dimensions[1] * 2.5),
                            hull_bbox_max[1] + (hull_dimensions[1] * 2.5)]
                z_bounds = [hull_bbox_min[2] - (hull_dimensions[2] * 2.5),
                            hull_bbox_max[2] + (hull_dimensions[2] * 2.5)]

                # Delete the measurement copy and re-select the original work copy
                bpy.data.objects.remove(measurement_obj)
                work_obj.select_set(True)
                bpy.context.view_layer.objects.active = work_obj

                for i in hull_face_indexes:
                    faces[i].select = True

                # Select similar (perimeter)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_linked(delimit=set())
                # Old method used face perimeter - but EDGE length, normal, and direction are more effective
                # bpy.ops.mesh.select_similar(
                #     type='PERIMETER', threshold=bpy.context.scene.SrcEngCollProperties.Similar_Factor)
                # bpy.ops.mesh.select_similar(
                #     type='DIR', threshold=.0001)
                bpy.ops.mesh.select_mode(type='EDGE')
                bpy.ops.mesh.select_similar(
                    type='DIR', threshold=similarity_threshold)
                bpy.ops.mesh.select_mode(type='VERT')
                bpy.ops.mesh.select_linked(delimit=set())

                # Store the selected face indexes
                bpy.ops.object.mode_set(mode='OBJECT')
                selected_face_indexes = [
                    f.index for f in faces if f.select]

                # Check if each face center is within the boundaries of the bound box (x 2.5).
                for i in selected_face_indexes:
                    center = work_obj.matrix_world @ faces[i].center
                    if center[0] < x_bounds[0] or center[0] > x_bounds[1]:
                        if center[1] < y_bounds[0] or center[1] > y_bounds[1]:
                            if center[2] < z_bounds[0] or center[2] > z_bounds[1]:
                                selected_face_indexes.remove(i)
                                continue

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='VERT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.object.mode_set(mode='OBJECT')
                for i in selected_face_indexes:
                    faces[i].select = True
                bpy.ops.object.mode_set(mode='EDIT')

                bpy.ops.mesh.select_less()
                bpy.ops.mesh.select_less()
                bpy.ops.mesh.select_less()
                bpy.ops.mesh.select_less()

                # Isolate the faces to their own object
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(False)
                work_obj.select_set(False)
                temp_obj = bpy.context.selected_objects[0]
                bpy.context.view_layer.objects.active = temp_obj

                # Resize object, based on user setting "Scale Factor"
                scale_modifier = bpy.context.scene.SrcEngCollProperties.Scale_Modifier
                bpy.ops.transform.resize(value=(scale_modifier, scale_modifier, scale_modifier), orient_type='GLOBAL', orient_matrix=(
                    (1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, snap=False)
                bpy.ops.object.transform_apply(
                    location=False, rotation=True, scale=True)

                # Merge faces
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.select_mode(type='VERT')
                bpy.ops.mesh.remove_doubles(threshold=doubles_threshold)
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.separate(type='LOOSE')

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.quads_convert_to_tris(
                    quad_method='BEAUTY', ngon_method='BEAUTY')
                bpy.ops.mesh.convex_hull(join_triangles=False)
                bpy.ops.mesh.dissolve_limited(
                angle_limit=0.0872665, delimit={'NORMAL'})  # angle_limit = 0.174533 is same as '10 degrees'
                bpy.ops.mesh.quads_convert_to_tris(
                    quad_method='BEAUTY', ngon_method='BEAUTY')
                bpy.ops.mesh.convex_hull(join_triangles=False)

                # Join and store the merged hulls, so we can rejoin all merged pieces later
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.join()

                obj_parts.add(bpy.context.active_object)

                # Deselect the piece, and reselect the main object
                bpy.ops.object.select_all(action='DESELECT')
                work_obj.select_set(True)
                bpy.context.view_layer.objects.active = work_obj

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)

            # Merge all the merged hull parts back into one single object
            for part in obj_parts:
                part.select_set(True)
            bpy.ops.object.join()
            new_obj = bpy.context.active_object
            new_obj.name = obj.name
            bpy.data.objects.remove(obj)

            # Cleanup mesh
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.mesh.select_mode(
                use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.select_linked(delimit=set())
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_smooth()

            # Reset dimensions and apply final transforms
            new_obj.dimensions = original_dimensions
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)

        return {'FINISHED'}

# Remove Thin faces operator


class Cleanup_RemoveThinFaces(bpy.types.Operator):
    """Removes polygons that are smaller than the model's average face area, based on the Thin Threshold setting. If using this on a collision mesh, you should use Force Convex on it afterward"""
    bl_idname = "object.src_eng_cleanup_remove_thin_faces"
    bl_label = "Remove Thin Faces"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected():
            obj = bpy.context.active_object
            faces = obj.data.polygons
            area_threshold = bpy.context.scene.SrcEngCollProperties.Thin_Threshold
            collapse = bpy.context.scene.SrcEngCollProperties.Thin_Collapse
            cumulative_area = 0

            bpy.ops.object.mode_set(mode='OBJECT')

            for f in faces:
                cumulative_area += f.area

            average_area = cumulative_area / len(faces)

            thin_faces = {f.index for f in faces if f.area <
                          (average_area * area_threshold)}

            # Make sure no faces are selected
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(
                use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(
                use_extend=False, use_expand=False, type='FACE')
            bpy.ops.object.mode_set(mode='OBJECT')

            for i in thin_faces:
                faces[i].select = True

            bpy.ops.object.mode_set(mode='EDIT')

            if collapse:
                bpy.ops.mesh.edge_collapse()
                bpy.ops.mesh.select_mode(
                    use_extend=False, use_expand=False, type='VERT')
            else:
                bpy.ops.mesh.delete(type='FACE')

            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

# Force Convex operator


class Cleanup_ForceConvex(bpy.types.Operator):
    """Forces all existing hulls in the selected object to be convex. Warning: Any non-manifold geometry will be removed by this operation"""
    bl_idname = "object.src_eng_cleanup_force_convex"
    bl_label = "Force Convex"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected():

            obj = bpy.context.active_object
            original_name = obj.name
            total_hull_count = 0

            # Make sure no faces are selected
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.transform_apply(
                location=False, rotation=True, scale=True)

            # Select all hulls and separate them into separate objects
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.dissolve_limited(
                angle_limit=0.0872665, delimit={'NORMAL'})
            bpy.ops.mesh.quads_convert_to_tris(
                quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            # Begin Bmesh processing
            me = obj.data
            bm = bmesh.new()
            bm_processed = bmesh.new()

            bm.from_mesh(me)
            hulls = [hull for hull in bmesh_get_hulls(
                bm, verts=bm.verts)]
            print(me.name, "Hulls to process:", len(hulls))

            # Create individual hull bmeshes
            for hull in hulls:
                bm_hull = bmesh.new()

                # Add vertices to individual bmesh hull
                for vert in hull:
                    bmesh.ops.create_vert(bm_hull, co=vert.co)

                # Generate convex hull
                ch = bmesh.ops.convex_hull(
                    bm_hull, input=bm_hull.verts, use_existing_faces=False)
                bmesh.ops.delete(
                    bm_hull,
                    geom=list(set(ch["geom_unused"] + ch["geom_interior"])),
                    context='VERTS')

                bmesh.ops.triangulate(
                    bm_hull, faces=bm_hull.faces, quad_method='BEAUTY', ngon_method='BEAUTY')

                ch2 = bmesh.ops.convex_hull(
                    bm_hull, input=bm_hull.verts, use_existing_faces=False)
                bmesh.ops.delete(
                    bm_hull,
                    geom=list(set(ch2["geom_unused"] + ch2["geom_interior"])),
                    context='VERTS')

                # Add the processed hull to the new main object, which will store all of them
                bmesh_join(bm_processed, bm_hull)
                total_hull_count += 1
                bm_hull.clear()
                bm_hull.free()

            bm_processed.to_mesh(me)
            me.update()
            bm.clear()
            bm.free()
            bm_processed.clear()
            bm_processed.free()

            # Rejoin and clean up
            bpy.context.active_object.name = original_name
            bpy.ops.object.transform_apply(
                location=False, rotation=True, scale=True)
            bpy.ops.object.shade_smooth()

            # Remove non-manifolds
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(
                use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.select_linked(delimit=set())
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            display_msg_box(
                "Processed " + str(total_hull_count) + " hulls.", "Info", "INFO")

        return {'FINISHED'}

# Remove Inside Hulls operator


class Cleanup_RemoveInsideHulls(bpy.types.Operator):
    """Removes hulls that are (entirely or mostly) inside other hulls"""
    bl_idname = "object.src_eng_cleanup_remove_inside"
    bl_label = "Remove Inside Hulls"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if check_for_selected():

            original_name = bpy.context.active_object.name
            # Make sure no faces are selected
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            # Select all hulls and separate them into separate objects
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

            hulls = [o for o in bpy.context.selected_objects]
            hulls_to_delete = set()

            for outer_hull in hulls:

                # Get bounding box lowest and highest vertices - to check if inner hull is inside it later
                hull_bbox_min = outer_hull.matrix_world @ Vector(
                    outer_hull.bound_box[0])
                hull_bbox_max = outer_hull.matrix_world @ Vector(
                    outer_hull.bound_box[6])

                def check_inside_bbox(h):
                    loc = h.location
                    if hull_bbox_min[0] < loc[0] and hull_bbox_max[0] > loc[0]:
                        if hull_bbox_min[1] < loc[1] and hull_bbox_max[1] > loc[1]:
                            if hull_bbox_min[2] < loc[2] and hull_bbox_max[2] > loc[2]:
                                return True
                    else:
                        return False

                # Create list of hulls that are smalller than this hull and within the outer hull's bounding box
                hulls_to_check = [h for h in hulls if h != outer_hull and h.dimensions <
                                  outer_hull.dimensions and check_inside_bbox(h)]

                for inner_hull in hulls_to_check:
                    inner_hull_loc = inner_hull.location
                    outer_hull_faces = outer_hull.data.polygons

                    # This returns a list of frontface indices. Backfaces are not included
                    frontfaces = [f.index for f in outer_hull_faces if f.normal.dot(
                        inner_hull_loc - (outer_hull.matrix_world @ f.center)) > 0]

                    # Zero length means no frontfaces were visible - aka inner hull truly is inside outer hull
                    if len(frontfaces) == 0:

                        # Mark the hull for deletion if it's inside another hull
                        hulls_to_delete.add(inner_hull)
                    else:
                        continue

            bpy.ops.object.mode_set(mode='OBJECT')

            amount_to_remove = str(len(hulls_to_delete))

            # Remove marked hulls
            for h in hulls_to_delete:
                bpy.data.objects.remove(h)

            # Rejoin and clean up
            bpy.ops.object.join()
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

            bpy.context.active_object.name = original_name
            bpy.ops.object.transform_apply(
                location=False, rotation=True, scale=True)
            bpy.ops.object.shade_smooth()

            display_msg_box(
                "Removed " + amount_to_remove + " hull(s).", "Info", "INFO")
            print("Removed " + amount_to_remove + " hull(s).")

        return {'FINISHED'}

# Generate Source Engine QC


class GenerateSourceQC(bpy.types.Operator):
    """Generate QC files used by Source Engine to compile the collision model(s) in the currently active collection"""
    bl_idname = "object.src_eng_qc"
    bl_label = "Generate Source Engine QC"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if check_for_selected():
            QC_folder = bpy.path.abspath(
                bpy.context.scene.SrcEngCollProperties.QC_Folder)
            models_dir = bpy.context.scene.SrcEngCollProperties.QC_Src_Models_Dir
            mats_dir = bpy.context.scene.SrcEngCollProperties.QC_Src_Mats_Dir
            dirs = [bpy.context.scene.SrcEngCollProperties.QC_Folder,
                    models_dir, mats_dir]

            # Check for trailing slashes
            for dir in dirs:
                if not dir.endswith("\\") and not dir.endswith("/"):
                    display_msg_box(
                        "One of your specified QC directories is missing a trailing slash (\\ or /) at the end.\nAdd one first and then try again", "Error", "ERROR")
                    return {'FINISHED'}

           # Get the Collision Models collection
            root_collection = None
            if 'Collision Models' in bpy.data.collections.keys():
                if len(bpy.data.collections["Collision Models"].all_objects) > 0:
                    root_collection = bpy.data.collections['Collision Models']
                else:
                    display_msg_box(
                        "There are no collision models in the 'Collision Models' collection. Place your collision models there first", "Error", "ERROR")
            else:
                display_msg_box(
                    "There is no 'Collision Models' collection. Please create one with that exact name, and then place your collision models inside it", "Error", "ERROR")
            if root_collection == None:
                return {'FINISHED'}

            # Get list of all objects in the Collision Models collection
            objs = [obj for obj in root_collection.all_objects]

            # Generate QC file for every object
            for obj in objs:
                with open(f"{QC_folder}{obj.name}.qc", 'w') as qc_file:
                    qc_file.writelines(generate_QC_lines(
                        obj, models_dir, mats_dir))

            # Generate empty placeholder SMD
            with open(QC_folder + "Empty.smd", 'w') as empty_smd_file:
                empty_smd_file.writelines(generate_SMD_lines())

            display_msg_box("QC files generated successfully in " + QC_folder +
                            "\n\nYou will still need to export your collision models as SMD through other means (ie. Blender Source Tools or SourceOps)", "Info", "INFO")

        return {'FINISHED'}

# Recommended Settings button


class RecommendedCollSettings(bpy.types.Operator):
    """Automatically modify the settings below based on the currently selected, active mesh object. Note: This is not foolproof. You may still need to tweak the settings yourself"""
    bl_idname = "object.src_eng_recc_settings"
    bl_label = "Recommended Settings"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if check_for_selected():

            obj = bpy.context.active_object

            avg_length = get_avg_length(obj)
            extrude_modifier = avg_length * 0.07
            distance_modifier = avg_length * 0.05
            scale_modifier = 1

            # For scale modifier, guideline is that average edge length must be roughly 487.4999679487 or lower
            # for Remove Doubles to work, due to its hardcoded 50 threshold limit
            if distance_modifier > 50.0:
                scale_modifier = 1 / (distance_modifier/50.0)
                distance_modifier = 50.0

            bpy.context.scene.SrcEngCollProperties.Extrusion_Modifier = extrude_modifier
            bpy.context.scene.SrcEngCollProperties.Distance_Modifier = distance_modifier
            bpy.context.scene.SrcEngCollProperties.Scale_Modifier = scale_modifier

        return {'FINISHED'}

# Update VMF operator


class UpdateVMF(bpy.types.Operator):
    """Automatically adds any split-up (ie. mymodel_part_000.mdl) collision models in the 'Collision Models' collection to the VMF, if they aren't already contained in it. IMPORTANT: The first part, '_part_000.mdl' must be added manually to VMF"""
    bl_idname = "object.src_eng_vmf_update"
    bl_label = "Update VMF"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if check_for_selected():
            VMF_path = bpy.path.abspath(
                bpy.context.scene.SrcEngCollProperties.VMF_File)

           # Get the Collision Models collection
            root_collection = None
            if 'Collision Models' in bpy.data.collections.keys():
                if len(bpy.data.collections["Collision Models"].all_objects) > 0:
                    root_collection = bpy.data.collections['Collision Models']
                else:
                    display_msg_box(
                        "There are no collision models in the 'Collision Models' collection. Place your collision models there first", "Error", "ERROR")
            else:
                display_msg_box(
                    "There is no 'Collision Models' collection. Please create one with that exact name, and then place your collision models inside it", "Error", "ERROR")
            if root_collection == None:
                return {'FINISHED'}

            # Get list of all objects in the Collision Models collection
            objs = [
                obj.name for obj in root_collection.all_objects if "_part_" in obj.name]
            objs.sort()

            print("Opening VMF file at: " + VMF_path)
            # Open VMF file for reading and parse data
            with open(VMF_path, 'r+') as vmf_file:

                total_length = len(vmf_file.readlines())

                print(str(total_length) + " lines loaded from VMF file.")
                vmf_file.seek(0)

                contents = vmf_file.read()

                # Make sure it's a real VMF file first
                if "versioninfo" not in contents[0:30]:
                    display_msg_box(
                        "Please select a valid VMF file and try again", "Error", "ERROR")
                    return {'FINISHED'}

                # Setup Regex
                entities_regex = r'\n^[a-z_]+\n\{\n(?:.*?)^(?:\})'
                part_zero_regex = r'(?!:/)[a-z_]*(?:_part_000)'
                id_regex = r'\t\"id\" \"\d+\"'

                # Parse VMF for entities
                entities = re.findall(
                    entities_regex, contents, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                print(str(len(entities)) +
                      " entities were found in the VMF.")

                parts_zero_found = list()
                i = 0

                # Scan entity list for needed data
                for ent in entities:

                    # Look for any _part_0.mdl
                    part_zero_found = re.search(part_zero_regex, ent, re.IGNORECASE |
                                                re.MULTILINE | re.DOTALL)
                    if part_zero_found:
                        parts_zero_found.append(
                            (i, part_zero_found.group()))

                    i += 1

                new_entities_to_add = set()

                # For every _part_000 that was found...
                for part in parts_zero_found:
                    root = part[1][0:-3]
                    entity_index = part[0]
                    matching_objs = set([o for o in objs if root in o])

                    # For every matched Blender object
                    for matched in matching_objs:

                        # Check if the matched object exists in the VMF already
                        if matched not in contents:

                            old_entity = str(entities[entity_index])

                            # Add new part number
                            new_entity = old_entity.replace(
                                "_part_000", "_part_" + matched[-3:])

                            # Remove old entity ID. Hammer will automatically assign a new one
                            old_id = re.search(id_regex, new_entity, re.IGNORECASE |
                                               re.MULTILINE | re.DOTALL)
                            old_id = old_id.group()
                            new_entity = new_entity.replace(old_id, "")

                            new_entities_to_add.add(new_entity)
                        else:
                            continue

                new_entities_to_add = list(new_entities_to_add)
                new_entities_to_add.sort()
                if len(new_entities_to_add) > 0:
                    # Write new entities
                    vmf_file.seek(0, 2)
                    vmf_file.write("\n")
                    vmf_file.writelines(new_entities_to_add)
                    vmf_file.write("\n")
                    vmf_file.close()
                    display_msg_box(
                        "VMF file modified successfully\n"+f"Added {str(len(new_entities_to_add))} new entities to VMF.", "Info", "INFO")
                else:
                    display_msg_box(
                        "VMF is already up-to-date", "Info", "INFO")

        return {'FINISHED'}

# End classes


ops = (
    GenerateSrcCollision,
    SplitUpSrcCollision,
    GenerateSourceQC,
    Cleanup_MergeAdjacentSimilars,
    Cleanup_RemoveThinFaces,
    Cleanup_ForceConvex,
    Cleanup_RemoveInsideHulls,
    RecommendedCollSettings,
    UpdateVMF
)


def menu_func(self, context):
    for op in ops:
        self.layout.operator(op.bl_idname)

# MATERIALS PANEL


class SrcEngCollGen_Panel(bpy.types.Panel):
    bl_label = 'Source Engine Collision Tools'
    bl_idname = "MESH_PT_src_eng_coll_gen"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @ classmethod
    def poll(cls, context):
        return (context.object != None)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.enabled = check_for_selected(verbose=False)

        row0 = layout.row()
        row1 = layout.row()
        row2 = layout.row()
        row3 = layout.row()
        row4 = layout.row()
        layout.separator()

        row5 = layout.row()
        layout.separator()

        row6 = layout.row()
        layout.separator()

        row0.operator("object.src_eng_recc_settings")
        row1.prop(bpy.context.scene.SrcEngCollProperties, "Decimate_Ratio")
        row2.prop(bpy.context.scene.SrcEngCollProperties, "Extrusion_Modifier")
        row2.prop(bpy.context.scene.SrcEngCollProperties, "Scale_Modifier")

        row3.operator("object.src_eng_collision")
        row4.operator("object.src_eng_split")

        # Cleanup UI
        boxCleanup = row5.box()
        boxCleanup.label(text="Clean Up Tools")
        rowCleanup1_Label = boxCleanup.row()
        rowCleanup1 = boxCleanup.row()
        rowCleanup2 = boxCleanup.row()
        boxCleanup.separator()
        rowCleanup3_Label = boxCleanup.row()
        rowCleanup3 = boxCleanup.row()
        rowCleanup4 = boxCleanup.row()
        rowCleanup5_Label = boxCleanup.row()
        rowCleanup5 = boxCleanup.row()
        rowCleanup6 = boxCleanup.row()
        boxCleanup.separator()

        rowCleanup1_Label.label(text="Similarity")
        rowCleanup1.prop(
            bpy.context.scene.SrcEngCollProperties, "Similar_Factor")
        rowCleanup1.prop(
            bpy.context.scene.SrcEngCollProperties, "Distance_Modifier")
        rowCleanup2.operator("object.src_eng_cleanup_merge_similars")

        rowCleanup3_Label.label(text="Thinness")
        rowCleanup3.prop(
            bpy.context.scene.SrcEngCollProperties, "Thin_Threshold")
        rowCleanup3.prop(
            bpy.context.scene.SrcEngCollProperties, "Thin_Collapse")
        rowCleanup4.operator("object.src_eng_cleanup_remove_thin_faces")
        rowCleanup5_Label.label(text="Other")
        rowCleanup5.operator("object.src_eng_cleanup_force_convex")
        rowCleanup6.operator("object.src_eng_cleanup_remove_inside")

        # Compile / QC UI
        boxQC = row6.box()
        boxQC.label(text="Compile Tools")
        rowQC1 = boxQC.row()
        rowQC2 = boxQC.row()
        rowQC3 = boxQC.row()
        rowQC4 = boxQC.row()
        rowQC5 = boxQC.row()
        rowQC6 = boxQC.row()

        rowQC1.prop(bpy.context.scene.SrcEngCollProperties, "QC_Folder")
        rowQC2.prop(bpy.context.scene.SrcEngCollProperties,
                    "QC_Src_Models_Dir")
        rowQC3.prop(bpy.context.scene.SrcEngCollProperties, "QC_Src_Mats_Dir")
        rowQC4.enabled = len(bpy.context.scene.SrcEngCollProperties.QC_Folder) > 0 and len(
            bpy.context.scene.SrcEngCollProperties.QC_Src_Models_Dir) > 0 and len(bpy.context.scene.SrcEngCollProperties.QC_Src_Mats_Dir) > 0
        rowQC4.operator("object.src_eng_qc")
        rowQC5.prop(bpy.context.scene.SrcEngCollProperties, "VMF_File")
        rowQC6.operator("object.src_eng_vmf_update")
        rowQC6.enabled = len(
            bpy.context.scene.SrcEngCollProperties.VMF_File) > 0

# End of classes


classes = (
    SrcEngCollGen_Panel,
    SrcEngCollProperties,
    GenerateSrcCollision,
    SplitUpSrcCollision,
    GenerateSourceQC,
    Cleanup_MergeAdjacentSimilars,
    Cleanup_RemoveThinFaces,
    Cleanup_ForceConvex,
    Cleanup_RemoveInsideHulls,
    RecommendedCollSettings,
    UpdateVMF
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.SrcEngCollProperties = bpy.props.PointerProperty(
        type=SrcEngCollProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.SrcEngCollProperties


if __name__ == "__main__":
    register()
