# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy, math, traceback
import bmesh
from mathutils.geometry import (
                distance_point_to_plane,
                normal)

bl_info = {
    "name" : "BlendTools",
    "author" : "Antony Naumovic",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


def ClearMirror():
    MirrorSettings.boolVec_Mirror = (False, False, False)
    print("Yes")

def MirrorObject(self, context):
    scene = context.scene
    MirrorSettings = scene.mirrorSettings
    active = bpy.context.active_object
    
    mirrorObj = bpy.context.scene.objects.get("Mirror")
    if not mirrorObj:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
        bpy.context.object.name = "Mirror"
        mirrorObj = bpy.context.object
        mirrorObj.empty_display_size = 0.1
    OBs = bpy.context.selected_objects.copy()
    try:
        for object in OBs:
            if "WN_Mirror" not in bpy.context.object.modifiers:
                bpy.ops.object.modifier_add(type='MIRROR')
                bpy.context.object.modifiers[len(object.modifiers)-1].name = "WN_Mirror"
            mirrorModifier = bpy.context.object.modifiers["WN_Mirror"]
            mirrorModifier.use_axis = MirrorSettings.boolVec_Mirror
            mirrorModifier.mirror_object = mirrorObj
            mirrorModifier.use_clip = True
    except Exception as e:
        print(traceback.format_exc())
        return
    return

class BevelSettings(bpy.types.PropertyGroup):
    float_bevelAmount : bpy.props.FloatProperty(
        name="Bevel Amount",
        description="Bevel Weight Amount",
        default=0.001,
        min=0.0,
        max=30,
        unit='LENGTH',
    )
    float_sharpAngle : bpy.props.FloatProperty(
        name="Sharpness Angle",
        description="Sharp Weight Amount",
        default=0.523599,
        min=0,
        max=math.pi*2,
        unit='ROTATION',
        subtype='ANGLE'
    )
    enum_bevelAction: bpy.props.EnumProperty(
        name="Bevel Preset",
        description="Action Selecting",
        items=[
        ("0", "Sub D", ""),
        ("1", "Default", ""),
        ]
    )
    bool_redoWeights: bpy.props.BoolProperty(
        name="Redo Weights",
        description="Reset Weights and add new",
        default=False
    )
    int_segAmounts: bpy.props.IntProperty(
        name="Segment Count",
        description="Bevel Segment Amount",
        default=1,
        min=1
    )

class MirrorSettings(bpy.types.PropertyGroup):
    boolVec_Mirror: bpy.props.BoolVectorProperty(
        name="Mirror",
        description="Mirror",
        default=(False,False,False),
        update=MirrorObject,
    )

class LODSettings(bpy.types.PropertyGroup):
    enum_LODAction: bpy.props.EnumProperty(
        name="LOD Preset",
        description="LOD Preset Selecting",
        items=[
        ("0", "Hero", ""),
        ("1", "Background", ""),
        ]
    )



class BlendTools_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

class BlendTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_idname = "BLENDTOOLS_PT_panel"
    bl_label = "BlendTools"
    def draw(self, context):
        pass
        
class BevelTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "Bevel"
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


    def draw(self, context):
        scene = context.scene
        settings = scene.bevelSettings
        layout = self.layout
        
        layout.operator("object.bevelmod", text="Bevel")
        layout.prop(settings, "enum_bevelAction")
        layout.prop(settings, "float_bevelAmount")
        layout.prop(settings, "float_sharpAngle")
        layout.prop(settings, "int_segAmounts")
        layout.prop(settings, "bool_redoWeights")

class MirrorTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "Mirror"
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


    def draw(self, context):
        scene = context.scene
        settings = scene.mirrorSettings
        layout = self.layout
        row = layout.row(align=True)
        mirrorMod = list(filter(lambda x: x.name.startswith("WN_Mirror"), bpy.context.object.modifiers))
        if not mirrorMod:
            row.operator("object.addmirror", text="X").id=0
            row.operator("object.addmirror", text="Y").id=1
            row.operator("object.addmirror", text="Z").id=2
        else:
            
            row.prop(mirrorMod[-1], "use_axis", toggle=1, text="X", index=0)
            row.prop(mirrorMod[-1], "use_axis", toggle=1, text="Y", index=1)
            row.prop(mirrorMod[-1], "use_axis", toggle=1, text="Z", index=2)
        if len(list(filter(lambda x: x.name.startswith("WN_Mirror"), bpy.context.object.modifiers))) and len(bpy.context.selected_objects) > 1:
            layout.operator("object.updatemirrormod", text="Copy To Selected")

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

class LODTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "LOD"
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


    def draw(self, context):
        scene = context.scene
        settings = scene.lodSettings
        layout = self.layout
        layout.prop(settings, "enum_LODAction", expand=True)
        layout.operator("object.lodify", text="LODify")
        

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
                    bpy.ops.object.modifier_add(type='TRIANGULATE')
                    bpy.context.object.modifiers[len(obj.modifiers)-1].name = "WN_Triangulate"
                    bpy.context.object.modifiers["WN_Triangulate"].keep_custom_normals = True
                    bpy.context.object.modifiers["WN_Triangulate"].min_vertices = 5
        except Exception as e:
            print(traceback.format_exc())
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
            print(traceback.format_exc())
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
            print(traceback.format_exc())
            self.report({"WARNING"}, str(e))
        bpy.context.view_layer.objects.active = active
        return {"FINISHED"}

class AddMirror_OT_Operator(bpy.types.Operator):
    bl_idname= "object.addmirror"
    bl_label="addmirror"
    bl_description="Add Mirror"
    id : bpy.props.IntProperty()
    def execute(self, context):
        copy = context.copy()
        mirrorObj = bpy.context.scene.objects.get("Mirror")
        if not mirrorObj:
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
            bpy.context.object.name = "Mirror"
            mirrorObj = bpy.context.object
            mirrorObj.empty_display_size = 0.1

        for i in copy["selected_objects"]:
            i.select_set(True)
        mirrorObj.select_set(False)

        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            if "WN_Mirror" not in obj.modifiers:
                bpy.ops.object.modifier_add(type='MIRROR')
                obj.modifiers[len(obj.modifiers)-1].name = "WN_Mirror"
                mirrorMod = obj.modifiers["WN_Mirror"]
                mirrorMod.use_axis[0] = False
                mirrorMod.use_axis[self.id] = True
                mirrorMod.use_clip = True
                mirrorMod.mirror_object = mirrorObj
        bpy.context.view_layer.objects.active = copy['active_object']
        return{"FINISHED"}
    
class UpdateBevelTools_PT_Panel(BlendTools_Panel, bpy.types.Panel):
    bl_parent_id = "BLENDTOOLS_PT_panel"
    bl_label = "Update Bevel"
    @classmethod
    def poll(cls, context):
        return (None if context.object is None else 
        list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers)))


    def draw(self, context):
        scene = context.scene
        settings = scene.bevelSettings
        layout = self.layout
        bevelMods = list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))
        row = layout.row()
        layout.prop(bevelMods[-1], "width", text="Width")
        layout.prop(bevelMods[-1], "segments", text="Segments")
        if len(list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))) and len(bpy.context.selected_objects) > 1:
            layout.operator("object.updatebevelmod", text="Copy To Selected")

class UpdateBevel_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.updatebevelmod"
    bl_label="bevelmod"
    bl_description="Update Bevel"

    def execute(self, context):
        scene = context.scene
        context = bpy.context
        BevelSettings = scene.bevelSettings
        bevelList = list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))
        curBevel = bevelList[-1]
        properties = []
        targets = context.copy()
        for prop in curBevel.bl_rna.properties:
            if not prop.is_readonly:
                properties.append(prop.identifier)
        if len(targets["selected_objects"]) == 0:
            return{"FINISHED"}
        
        for i in targets["selected_objects"]:
            i.select_set(True)
        for target in targets["selected_objects"]:
            bpy.context.view_layer.objects.active = target
            if target.type == "MESH":
                bevelList = list(filter(lambda x: x.name.startswith("WN_Bevel_"), target.modifiers))
                if len(bevelList) > 0:
                    bevelToUpdate = bevelList[-1]
                else:
                    bevelToUpdate = bpy.ops.object.modifier_add(type='BEVEL')
                    target.modifiers[len(target.modifiers)-1].name = "WN_Bevel_1"
                    bevelToUpdate = target.modifiers["WN_Bevel_1"]
                    target.data.use_auto_smooth = True
                for prop in properties:
                    setattr(bevelToUpdate, prop, getattr(curBevel, prop))
        bpy.context.view_layer.objects.active = targets['active_object']
        return{"FINISHED"}

class UpdateMirror_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.updatemirrormod"
    bl_label="mirrormod"
    bl_description="Update Mirror"

    def execute(self, context):
        scene = context.scene
        context = bpy.context
        bevelList = list(filter(lambda x: x.name.startswith("WN_Mirror"), bpy.context.object.modifiers))
        curBevel = bevelList[-1]
        properties = []
        targets = context.copy()
        for prop in curBevel.bl_rna.properties:
            if not prop.is_readonly:
                properties.append(prop.identifier)
        if len(targets["selected_objects"]) == 0:
            return{"FINISHED"}
        
        for i in targets["selected_objects"]:
            i.select_set(True)
        for target in targets["selected_objects"]:
            bpy.context.view_layer.objects.active = target
            if target.type == "MESH":
                bevelList = list(filter(lambda x: x.name.startswith("WN_Mirror"), target.modifiers))
                if len(bevelList) > 0:
                    bevelToUpdate = bevelList[-1]
                else:
                    bevelToUpdate = bpy.ops.object.modifier_add(type='MIRROR')
                    target.modifiers[len(target.modifiers)-1].name = "WN_Mirror"
                    bevelToUpdate = target.modifiers["WN_Mirror"]
                for prop in properties:
                    setattr(bevelToUpdate, prop, getattr(curBevel, prop))
        bpy.context.view_layer.objects.active = targets['active_object']
        return{"FINISHED"}

class Bevel_OT_Operator(bpy.types.Operator):
    
    bl_idname= "object.bevelmod"
    bl_label="bevelmod"
    bl_description="Add Bevel Modifier"

    def execute(self, context):
        scene = context.scene
        C = bpy.context
        BevelSettings = scene.bevelSettings

        obs = bpy.context.selected_objects
        active = bpy.context.active_object
        try:
            for ob in obs:
                #deselect all but just one object and make it active
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                if ob.type == "MESH":
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type="EDGE")
                    if BevelSettings.bool_redoWeights:
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.transform.edge_bevelweight(value=-1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.mesh.edges_select_sharp(sharpness=BevelSettings.float_sharpAngle)
                    bpy.ops.transform.edge_bevelweight(value=1)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bevelList = list(filter(lambda x: x.name.startswith("WN_Bevel_"), bpy.context.object.modifiers))
                    bevelAmount = len(bevelList)
                    if bevelAmount == 0:
                        bpy.context.object.data.use_auto_smooth = True
                        bpy.ops.object.modifier_add(type='BEVEL')
                        bpy.context.object.modifiers[len(ob.modifiers)-1].name = f"WN_Bevel_{bevelAmount+1}"
                        curBevel = bpy.context.object.modifiers[f"WN_Bevel_{bevelAmount+1}"]
                        curBevel.limit_method = 'WEIGHT'
                    else:
                        curBevel = bevelList[-1]
                    if BevelSettings.enum_bevelAction == "0":
                        curBevel.miter_outer = "MITER_ARC"
                        curBevel.use_clamp_overlap = False
                        curBevel.loop_slide = False
                    curBevel.width = BevelSettings.float_bevelAmount
                    curBevel.harden_normals = True
                    curBevel.segments = BevelSettings.int_segAmounts
                for ob in obs:
                    ob.select_set(state=True)
                bpy.context.view_layer.objects.active = active
        except Exception as e:
            print(traceback.format_exc())
            self.report({"WARNING"}, str(e))
        


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
    
class LODify_OT_Operator(bpy.types.Operator):
    bl_idname= "object.lodify"
    bl_label="lodify"
    bl_description="Create LODs"
    id : bpy.props.IntProperty()

    def execute(self, context):
        OBs = bpy.context.selected_objects
        active = bpy.context.active_object
        for ob in OBs:
            ob = bpy.context.active_object
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
        return{'FINISHED'}

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

                print(([distance_point_to_plane(v.co, co, norm) for v in ngon.verts[3:]]))

            bmesh.update_edit_mesh(mesh)
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode=mode)
        bpy.context.space_data.overlay.show_face_orientation = True
        return{'FINISHED'}

classes = (BevelSettings,
           MirrorSettings,
           LODSettings,
           BlendTools_PT_Panel,
           BevelTools_PT_Panel,
           UpdateBevelTools_PT_Panel,
           Bevel_OT_Operator,
           UpdateBevel_OT_Operator,
           MirrorTools_PT_Panel,
           AddMirror_OT_Operator,
           ExtraTools_PT_Panel,
           Triangulate_OT_Operator,
           AddSuffix_OT_Operator,
           RemoveSuffix_OT_Operator,
           UpdateMirror_OT_Operator,
           DeCustom_OT_Operator,
           ShowConcave_OT_Operator,
           LODTools_PT_Panel,
           LODify_OT_Operator
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bevelSettings = bpy.props.PointerProperty(type=BevelSettings)
    bpy.types.Scene.mirrorSettings = bpy.props.PointerProperty(type=MirrorSettings)
    bpy.types.Scene.lodSettings = bpy.props.PointerProperty(type=LODSettings)

def unregister():
    del bpy.types.Scene.bevelSettings
    del bpy.types.Scene.mirrorSettings
    del bpy.types.Scene.lodSettings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()