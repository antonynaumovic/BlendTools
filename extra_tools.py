import bpy, math, bmesh
from mathutils.geometry import (
                distance_point_to_plane,
                normal)
from .panel_base import BlendTools_Panel


class ExtraTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "Tools"
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


    def draw(self, context):
        scene = context.scene
        settings = scene.mirrorSettings
        layout = self.layout
        layout.operator("object.triangulate", text="Triangulate")
        row = layout.row(align=True)
        row.operator("object.addsuffix", text="Add Low").id="_low"
        row.operator("object.removesuffix", text="Remove Low").id="_low"
        row = layout.row(align=True)
        row.operator("object.addsuffix", text="Add High").id="_high"
        row.operator("object.removesuffix", text="Remove High").id="_high"
        layout.operator("object.decustom", text="Remove Custom Normals").id = True
        layout.operator("object.decustom", text="Add Custom Normals").id = False
        layout.operator("object.showconcave", text="Show Concave")
        

class Triangulate_OT_Operator(bpy.types.Operator):
    bl_idname= "object.triangulate"
    bl_label="triangulate"
    bl_description="Triangulate"

    def execute(self, context):
        scene = context.scene
        C = bpy.context
        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            for ob in obs:
                if ob is not None:
                    obj = ob
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if "WN_Triangulate" not in bpy.context.object.modifiers and bpy.context.object.type == "MESH":
                    triMod = bpy.ops.object.modifier_add(type='TRIANGULATE')
                    for mod in reversed(ob.modifiers):
                        if mod.type == "TRIANGULATE":
                            mod.name = f"WN_Triangulate"
                            break
                    bpy.context.object.modifiers["WN_Triangulate"].keep_custom_normals = True
                    bpy.context.object.modifiers["WN_Triangulate"].min_vertices = 5
        except Exception as e:
            self.report({"WARNING"}, str(e))
        bpy.context.view_layer.objects.active = active

        return {"FINISHED"}

class AddSuffix_OT_Operator(bpy.types.Operator):
    bl_idname= "object.addsuffix"
    bl_label="addsuffix"
    bl_description="Add Suffix"
    id : bpy.props.StringProperty()
    def execute(self, context):
        scene = context.scene
        C = bpy.context
        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            for ob in obs:
                if ob is not None:
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    lookup = ["_low", "_low.001", "_high", "_high.001"]
                    for idx in lookup:
                        bpy.context.object.name = bpy.context.object.name.removesuffix(idx)
                    bpy.context.object.name = bpy.context.object.name + self.id
        except Exception as e:
            self.report({"WARNING"}, str(e))
        bpy.context.view_layer.objects.active = active
        return {"FINISHED"}
    
class RemoveSuffix_OT_Operator(bpy.types.Operator):
    bl_idname= "object.removesuffix"
    bl_label="removesuffix"
    bl_description="Remove Suffix"
    id : bpy.props.StringProperty()
    def execute(self, context):
        scene = context.scene
        C = bpy.context
        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            for ob in obs:
                if ob is not None:
                    ob.select_set(state=True)
                    bpy.context.view_layer.objects.active = ob
                    lookup = [f"{self.id}", f"{self.id}.001"]
                    for idx in lookup:
                        bpy.context.object.name = bpy.context.object.name.removesuffix(idx)
        except Exception as e:
            self.report({"WARNING"}, str(e))
        bpy.context.view_layer.objects.active = active
        return {"FINISHED"}
    

class DeCustom_OT_Operator(bpy.types.Operator):
    bl_idname= "object.decustom"
    bl_label="decustom"
    bl_description="De Custom Split Normal"
    id : bpy.props.BoolProperty()

    def execute(self, context):
        OBs = bpy.context.selected_objects
        active = bpy.context.active_object
        if len(OBs) > 0:
            for ob in OBs:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if bpy.context.object.type == "MESH":
                    if self.id:
                        bpy.ops.mesh.customdata_custom_splitnormals_clear()
                    else:
                        bpy.ops.mesh.customdata_custom_splitnormals_add()
            
        for ob in OBs:
            ob.select_set(state=True)
        bpy.context.view_layer.objects.active = active
        return {"FINISHED"}
    

class ShowConcave_OT_Operator(bpy.types.Operator):
    bl_idname= "object.showconcave"
    bl_label="showconcave"
    bl_description="Flips Normals Of Concave"

    def execute(self, context):
        OBs = bpy.context.selected_objects
        mode = context.active_object.mode
        for ob in OBs:
            bpy.ops.object.mode_set(mode='EDIT')
            mesh = ob.data

            TOL = 0.0001

            # select None
            bpy.ops.mesh.select_all(action='DESELECT')
            bm = bmesh.from_edit_mesh(mesh)
            ngons = [f for f in bm.faces if len(f.verts) > 3]

            for ngon in ngons:
                # define a plane from first 3 points
                co = ngon.verts[0].co
                norm = normal([v.co for v in ngon.verts[:3]])
                ngon.select =  not all(
                    [(distance_point_to_plane(v.co, co, norm)) < TOL
                    for v in ngon.verts[3:]])
                if ngon.select: 
                    bpy.ops.mesh.normals_make_consistent(inside=True)

            bmesh.update_edit_mesh(mesh)
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode=mode)
        bpy.context.space_data.overlay.show_face_orientation = True
        return{'FINISHED'}