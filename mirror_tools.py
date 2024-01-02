import bpy
from .panel_base import BlendTools_Panel

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
        self.report({"WARNING"}, str(e))
        return
    return


class MirrorSettings(bpy.types.PropertyGroup):
    boolVec_Mirror: bpy.props.BoolVectorProperty(
        name="Mirror",
        description="Mirror",
        default=(False,False,False),
        update=MirrorObject,
    )

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
    