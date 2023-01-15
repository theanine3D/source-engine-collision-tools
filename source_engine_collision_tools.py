import bpy
from bpy.utils import(register_class, unregister_class)
from bpy.types import(Panel, PropertyGroup)
from bpy.props import(StringProperty,
                      FloatProperty, BoolProperty)

bl_info = {
    "name": "Source Engine Collision Tools",
    "description": "Quickly generate and optimize collision models for use in Source Engine",
    "author": "Theanine3D",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "category": "Mesh",
    "location": "Properties -> Object Properties",
    "support": "COMMUNITY"
}


# PROPERTY DEFINITIONS

class SrcEngCollProperties(bpy.types.PropertyGroup):
    QC_Folder: bpy.props.StringProperty(
        name="QC Folder", description="Full path of the folder in which to save the generated QCs", default="", maxlen=1024)
    Decimate_Ratio: bpy.props.FloatProperty(
        name="Decimate Ratio", subtype="FACTOR", description="A lower ratio will result in a less accurate (but more performant) collision mesh. Leave this at 1.0 if you don't want to decimate at all", max=1.0, min=0.0, default=0.5)
    Extrusion_Modifier: bpy.props.FloatProperty(
        name="Extrude Factor", subtype="FACTOR", description="The setting affects the extrusion of each hull. Default will work in most cases", min=0.01, max=10.0, default=1.0)
    Scale_Modifier: bpy.props.IntProperty(
        name="Scale Factor", description="Default will work in most cases. If you see chunks of geometry missing from the generated collision model, try setting this to something lower", min=-5, max=5, default=0)
    Similar_Factor: bpy.props.FloatProperty(
        name="Similar Factor", subtype="FACTOR", description="Intensity setting for Merge Adjacent Similars. A higher factor will result in more hulls merging together, but at the cost of accuracy", min=0.01, max=1.0, default=0.25)
    Thin_Threshold: bpy.props.FloatProperty(
        name="Thin Threshold", subtype="FACTOR", description="The thinness threshold to use when removing thin hulls. If set to default, the operator will only remove faces with an area that is lower than 10 percent of the average area of all faces", min=0.001, max=.5, default=.1)
    Thin_Linked: bpy.props.BoolProperty(
        name="Affect Linked", description="If enabled, any faces that are linked/connected to the thin faces will also be removed. Leave enabled if you're trying to clean up an existing collision model. Only disable this setting if you want to use Remove Thin Faces on the original non-collision model prior to actually generating the collision.", default=True)

# FUNCTION DEFINITIONS

def display_msg_box(message="", title="Info", icon='INFO'):
    ''' Open a pop-up message box to notify the user of something               '''
    ''' Example:                                                                '''
    ''' display_msg_box("This is a message", "This is a custom title", "ERROR") '''

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def check_for_selected(verbose=True):

    # Check if any objects are selected.
    if len(bpy.context.selected_objects) > 0 and len(bpy.context.selected_objects) < 2:
        if bpy.context.active_object != None:
            if bpy.context.active_object.type == "MESH":
                return True
            else:
                if verbose == True:
                    display_msg_box(
                    "There is no active mesh object. Click on one and try again", "Error", "ERROR")
                return False
        else:
            if verbose == True:
                display_msg_box(
                    "There is no active mesh object. Click on one and try again", "Error", "ERROR")
            return False
    else:
        if verbose == True:
            display_msg_box(
                "One mesh object must be selected and set as active", "Error", "ERROR")
        return False

# Generate Collision Mesh operator

class GenerateSrcCollision(bpy.types.Operator):
    """Generate a Source Engine-compliant collision model based on the current active object. The original object will be temporarily hidden, but not modified otherwise"""
    bl_idname = "object.gen_src_collision"
    bl_label = "Generate Collision Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected() == True:
            
            root_collection = None
            if 'Collision Models' in bpy.data.collections.keys():
                root_collection = bpy.data.collections['Collision Models']
            else:
                root_collection = bpy.data.collections.new("Collision Models")
                bpy.context.scene.collection.children.link(root_collection)

            obj = bpy.context.active_object
            obj_collections = [c for c in bpy.data.collections if obj.name in c.objects.keys()]
            extrude_modifier = bpy.context.scene.SrcEngCollProperties.Extrusion_Modifier

            if "_phys" in bpy.context.active_object.name:
                display_msg_box(
                    "You have an existing collision model selected. Select a different model and try again.", "Error", "ERROR")
                return {'FINISHED'}

            original_dimensions = obj.dimensions
            longest_dim = float(max(original_dimensions))
            doubles_threshold = 0.14999999999999999769 * (1.00080240446594588574 ** longest_dim)
            extrude_factor = -0.17962946163683473686 * (1.00103086506704893382 ** longest_dim) * extrude_modifier # -43.5 for Source scale, -0.18 for Blender scale
            
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
            scale_modifier = (1 * (10 ** float(bpy.context.scene.SrcEngCollProperties.Scale_Modifier)))
            bpy.ops.transform.resize(value=(scale_modifier, scale_modifier, scale_modifier), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, snap=False)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=doubles_threshold)
            bpy.ops.mesh.tris_convert_to_quads(seam=True,sharp=True,materials=True)

            # Decimate and clean up mesh to minimize unnecessary hulls being generated later
            bpy.ops.mesh.dissolve_limited()
            bpy.ops.mesh.vert_connect_concave()
            bpy.ops.mesh.face_make_planar(repeat=20)
            bpy.ops.mesh.vert_connect_nonplanar()
            bpy.ops.mesh.decimate(ratio=bpy.context.scene.SrcEngCollProperties.Decimate_Ratio)
            bpy.ops.mesh.vert_connect_concave()
            bpy.ops.mesh.vert_connect_nonplanar()

            bpy.ops.mesh.edge_split(type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Extrude faces
            bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "snap":False, "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

            # Move the extruded faces inward 
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            bpy.ops.transform.shrink_fatten(value=(extrude_factor), use_even_offset=False, mirror=True, use_proportional_edit=False, snap=False)
            bpy.ops.mesh.edge_collapse()
            bpy.ops.mesh.select_all(action='SELECT')
            
            bpy.ops.mesh.normals_make_consistent(inside=False)

            bpy.ops.object.mode_set(mode='OBJECT')

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

            bpy.ops.object.mode_set(mode='EDIT')

            # Separate all hulls into separate objects
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')

            # Transform all hulls into convex hulls
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.dissolve_limited() # angle_limit = 0.174533 is same as '10 degrees'
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.mesh.convex_hull(join_triangles=False)

            # Recombine into one object
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.join()
            obj_phys.name = obj.name + "_phys"

            # Remove non-manifold and degenerates
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.select_linked(delimit=set())
            bpy.ops.mesh.delete(type='VERT')

            # Cleanup materials
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.data.materials.clear()
            if "phys" not in bpy.data.materials.keys():
                bpy.data.materials.new("phys")
            bpy.context.active_object.data.materials.append(bpy.data.materials["phys"])
            bpy.context.active_object.data.materials[0].diffuse_color = (1, 0, 0.78315, 1)

            # Reset size back to normal
            obj_phys.dimensions = original_dimensions
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        return {'FINISHED'}

# Split Up Collision Mesh operator

class SplitUpSrcCollision(bpy.types.Operator):
    """Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls"""
    bl_idname = "object.gen_src_split"
    bl_label = "Split Up Collision Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if check_for_selected() == True:
            
            root_collection = None
            if 'Collision Models' in bpy.data.collections.keys():
                root_collection = bpy.data.collections['Collision Models']
            else:
                root_collection = bpy.data.collections.new("Collision Models")
                bpy.context.scene.collection.children.link(root_collection)

            obj = bpy.context.active_object
            original_name = obj.name
            obj_collections = [c for c in bpy.data.collections if obj.name in c.objects.keys()]
            
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
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "snap":False, "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
                bpy.ops.object.join()
                new_group_obj = bpy.context.selected_objects[0]

                bpy.context.view_layer.objects.active = new_group_obj
                new_group_obj.name = original_name + "_part_" + str(i)

                # Check if collection for this hull already exists. If not, create it
                if new_group_obj.name not in bpy.data.collections.keys():
                    new_group_collection = bpy.data.collections.new(new_group_obj.name)
                else:
                    new_group_collection = bpy.data.collections[new_group_obj.name]

                root_collection.children.link(new_group_collection)
                for c in obj_collections:
                    c.objects.unlink(new_group_obj)

                new_group_collection.objects.link(new_group_obj)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                new_group_obj.select_set(False)

                hull_groups.pop()
                if len(hull_groups) == 0:
                    break

            # Clean up
            bpy.data.objects.remove(bpy.data.objects[original_name])
            if original_name in bpy.data.collections.keys():
                bpy.data.collections.remove(bpy.data.collections[original_name])
            for o in bpy.data.objects:
                if (original_name + ".") in o.name:
                    bpy.data.objects.remove(o)

        return {'FINISHED'}

# Merge Adjacent Similars operator

class Cleanup_MergeAdjacentSimilars(bpy.types.Operator):
    """Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a less accurate, but more performant model. If original model was already low-poly to begin with, you probably won't need this"""
    bl_idname = "object.gen_src_cleanup_merge_similars"
    bl_label = "Merge Adjacent Similars"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected() == True:
                
                obj = bpy.context.active_object
                obj_parts = set()
                original_dimensions = obj.dimensions
                longest_dim = float(max(original_dimensions))
                doubles_threshold = 0.14999999999999999769 * (1.00080240446594588574 ** longest_dim)
                # Similar threshold is set by user - but just in case, exponential formula here for documentation purposes
                # similarity_threshold = 0.90019867306982895535 * (0.99988964434256221495 ** longest_dim)

                # Create working copy
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.duplicate(linked=False)

                # Make sure no faces are selected
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                work_obj = bpy.context.active_object
                faces = work_obj.data.polygons
                
                while len(faces) > 0:
                    # Isolate similar and adjacent geometry in the copy
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    faces[0].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type='FACE')
                    bpy.ops.mesh.select_linked(delimit=set())
                    try:
                        bpy.ops.mesh.select_similar(type='PERIMETER', threshold=bpy.context.scene.SrcEngCollProperties.Similar_Factor)    # threshold 0.5 for Source scale,, .9 for Blender scale?
                        bpy.ops.mesh.select_mode(type='VERT')
                        bpy.ops.mesh.select_linked(delimit=set())
                    except:
                        continue
                    else:
                        # Isolate the faces to their own object
                        bpy.ops.mesh.separate(type='SELECTED')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        obj.select_set(False)
                        work_obj.select_set(False)
                        temp_obj = bpy.context.selected_objects[0]
                        bpy.context.view_layer.objects.active = temp_obj

                        # Merge faces
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.select_mode(type='VERT')
                        bpy.ops.mesh.remove_doubles(threshold=doubles_threshold)       # threshold 10 for Source scale, .15 for Blender scale
                        bpy.ops.mesh.select_mode(type='FACE')
                        bpy.ops.mesh.separate(type='LOOSE')

                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                        bpy.ops.mesh.convex_hull(join_triangles=False)
                        bpy.ops.mesh.dissolve_limited() # angle_limit = 0.174533 is same as '10 degrees'
                        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

                        # Join and store the merged hulls, so we can rejoin all merged pieces later
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.join()

                        obj_parts.add(bpy.context.active_object)

                        # Deselect the piece, and reselect the main object
                        bpy.ops.object.select_all(action='DESELECT')
                        work_obj.select_set(True)
                        bpy.context.view_layer.objects.active = work_obj
            
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

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
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.mesh.select_non_manifold()
                bpy.ops.mesh.select_linked(delimit=set())
                bpy.ops.mesh.delete(type='VERT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.shade_smooth()

                # Apply final transforms
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        return {'FINISHED'}

# Remove Thin faces operator

class Cleanup_RemoveThinFaces(bpy.types.Operator):
    """Removes any polygons that are smaller than the average face area in the model. Thin Threshold sets just how much smaller each face must be for it to be deleted. WARNING: Can't undo this"""
    bl_idname = "object.gen_src_cleanup_remove_thin_faces"
    bl_label = "Remove Thin Faces"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if check_for_selected() == True:
            obj = bpy.context.active_object
            faces = obj.data.polygons
            area_threshold = bpy.context.scene.SrcEngCollProperties.Thin_Threshold
            affect_linked = bpy.context.scene.SrcEngCollProperties.Thin_Linked
            cumulative_area = 0

            bpy.ops.object.mode_set(mode='OBJECT')

            for f in faces:
                cumulative_area += f.area
            
            average_area = cumulative_area / len(faces)

            thin_faces = {f.index for f in faces if f.area < (average_area * area_threshold)}

            # Make sure no faces are selected
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.object.mode_set(mode='OBJECT')

            for i in thin_faces:
                faces[i].select = True

            bpy.ops.object.mode_set(mode='EDIT')
            if affect_linked:
                bpy.ops.mesh.select_linked(delimit=set())
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

# Generate Source Engine QC

class GenerateSourceQC(bpy.types.Operator):
    """Generate QC files used by Source Engine to compile the collision model(s) in the currently active collection"""
    bl_idname = "object.gen_src_qc"
    bl_label = "Generate Source Engine QC"
    bl_options = {'REGISTER'}

    def execute(self, context):
        
        display_msg_box(
                    "This function is not yet implemented. Keep an eye on the GitHub repo for updates", "Error", "ERROR")

        return {'FINISHED'}

# End classes

ops = (
    GenerateSrcCollision,
    SplitUpSrcCollision,
    GenerateSourceQC,
    Cleanup_MergeAdjacentSimilars,
    Cleanup_RemoveThinFaces
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

        row1 = layout.row()
        row2 = layout.row()
        row3 = layout.row()
        row4 = layout.row()
        layout.separator()

        row5 = layout.row()
        layout.separator()

        row6 = layout.row()
        layout.separator()
        
        row1.prop(bpy.context.scene.SrcEngCollProperties, "Decimate_Ratio")
        row2.prop(bpy.context.scene.SrcEngCollProperties, "Extrusion_Modifier")
        row2.prop(bpy.context.scene.SrcEngCollProperties, "Scale_Modifier")

        row3.operator("object.gen_src_collision")
        row4.operator("object.gen_src_split")

        # Cleanup UI
        boxCleanup = row5.box()
        boxCleanup.label(text="Clean Up Tools")
        rowCleanup1 = boxCleanup.row()
        boxCleanup.separator()
        rowCleanup2 = boxCleanup.row()
        rowCleanup3 = boxCleanup.row()

        rowCleanup1.prop(bpy.context.scene.SrcEngCollProperties, "Similar_Factor")
        rowCleanup1.operator("object.gen_src_cleanup_merge_similars")

        rowCleanup2.prop(bpy.context.scene.SrcEngCollProperties, "Thin_Threshold")
        rowCleanup2.operator("object.gen_src_cleanup_remove_thin_faces")

        rowCleanup3.prop(bpy.context.scene.SrcEngCollProperties, "Thin_Linked")

        # Compile / QC UI
        boxQC = row6.box()
        boxQC.label(text="Compile Tools")
        rowQC1 = boxQC.row()
        rowQC2 = boxQC.row()

        rowQC1.prop(bpy.context.scene.SrcEngCollProperties, "QC_Folder")
        rowQC2.enabled = len(bpy.context.scene.SrcEngCollProperties.QC_Folder) > 0
        rowQC2.operator("object.gen_src_qc")


# End of classes

classes = (
    SrcEngCollGen_Panel,
    SrcEngCollProperties,
    GenerateSrcCollision,
    SplitUpSrcCollision,
    GenerateSourceQC,
    Cleanup_MergeAdjacentSimilars,
    Cleanup_RemoveThinFaces
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
   
    bpy.types.Scene.SrcEngCollProperties  = bpy.props.PointerProperty(
        type=SrcEngCollProperties)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.SrcEngCollProperties

if __name__ == "__main__":
    register()
